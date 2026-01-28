import base64
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q
from django.db import transaction 
from django.views.decorators.cache import never_cache
from django.core.files.base import ContentFile
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Account, Transaction
from .forms import AccountForm, TransferForm

# --- Helper Functions ---
def is_admin(user):
    return user.is_staff

# --- Authentication Redirects ---
@login_required
def login_success(request):
    if request.user.is_staff:
        return redirect('boss_portal')
    return redirect('customer_dashboard')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Use a transaction so if Account fails, the User isn't created
                with transaction.atomic():
                    user = form.save()
                    # Use get_or_create to prevent the Duplicate Entry error
                    Account.objects.get_or_create(
                        user=user, 
                        defaults={
                            'owner': user.username, 
                            'balance': 0.00,
                            'kyc_step': 1
                        }
                    )
                messages.success(request, "Account created successfully! You can now login.")
                return redirect('login')
            except Exception as e:
                # If anything goes wrong, the transaction rolls back
                messages.error(request, f"An error occurred during signup: {e}")
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# --- Boss / Admin Views ---
@user_passes_test(is_admin)
@login_required
@never_cache
def account_list(request):
    accounts = Account.objects.all()
    pending_count = Account.objects.filter(is_verified=False, kyc_step=3).count()
    query = request.GET.get('search')
    if query:
        accounts = accounts.filter(owner__icontains=query)
    
    total = accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    history = Transaction.objects.all().order_by('-timestamp')

    return render(request, 'accounts/index.html', {
        'accounts': accounts,
        'total_assets': total,
        'query': query,
        'pending_count': pending_count,
        'history': history,
    })

@user_passes_test(is_admin)
def approve_account(request, account_id):
    if request.method == "POST":
        account = get_object_or_404(Account, id=account_id)
        account.is_verified = True
        account.save()
        messages.success(request, f"Account for {account.user.username} activated!")
    return redirect('boss_portal')
# --- Updated Customer Dashboard ---
@login_required
def customer_dashboard(request):
    # 1. Get or Create account simply
    account, created = Account.objects.get_or_create(
        user=request.user, 
        defaults={'owner': request.user.username, 'kyc_step': 1}
    )

    # 2. THE ONLY REDIRECT: Only send them away if they are on Step 1 or 2.
    # If kyc_step is 3, 4, or 5... STAY HERE.
    if account.kyc_step < 3 and not account.is_verified:
        return redirect('verify_identity')

    my_history = Transaction.objects.filter(
        Q(sender=account.owner) | Q(receiver=account.owner)
    ).order_by('-timestamp')

    return render(request, 'accounts/dashboard.html', {
        'account': account,
        'my_history': my_history
    })

# --- Updated Identity Verification ---
@login_required
def identity_verification(request):
    account = request.user.account
    
    # THE ONLY REDIRECT: If they are already pending (3) or verified, 
    # get them OUT of here so they don't loop back.
    if account.is_verified or account.kyc_step >= 3:
        return redirect('customer_dashboard')

    if request.method == 'POST':
        if account.kyc_step == 1:
            account.phone_number = request.POST.get('phone_number')
            account.occupation = request.POST.get('occupation')
            account.kyc_step = 2
            account.save()
            return redirect('verify_identity')
        
        elif account.kyc_step == 2:
            id_data = request.POST.get('id_image')
            if id_data:
                format, imgstr = id_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f"id_{request.user.id}.{ext}")
                account.id_card_photo = data
                account.kyc_step = 3  # Move to pending
                account.save()
                return redirect('customer_dashboard')

    return render(request, 'accounts/verify_identity.html', {'account': account})
# --- Banking Operations ---
@login_required
def transfer_money(request):
    account = request.user.account
    if not account.is_verified:
        messages.error(request, "Verification required.")
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        target_username = request.POST.get('target_user')
        amount = Decimal(request.POST.get('amount', 0))
        try:
            receiver_user = User.objects.get(username=target_username)
            receiver_account = Account.objects.get(user=receiver_user)
            if account.balance >= amount and amount > 0:
                with transaction.atomic():
                    account.balance -= amount
                    receiver_account.balance += amount
                    account.save()
                    receiver_account.save()
                    new_tx = Transaction.objects.create(
                        sender=account.owner, receiver=receiver_account.owner,
                        amount=amount, tx_type='TRF'
                    )
                return redirect('transaction_receipt', ref_id=new_tx.ref_id)
        except (User.DoesNotExist, Account.DoesNotExist):
            messages.error(request, "Receiver not found.")
    return redirect('customer_dashboard')

@login_required
def deposit_money(request):
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        account = request.user.account
        with transaction.atomic():
            account.balance += amount
            account.save()
            new_tx = Transaction.objects.create(
                sender="External", receiver=account.owner, amount=amount, tx_type='DEP'
            )
        return redirect('transaction_receipt', ref_id=new_tx.ref_id)
    return redirect('customer_dashboard')

@login_required
def withdraw_money(request):
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        account = request.user.account
        if account.balance >= amount:
            with transaction.atomic():
                account.balance -= amount
                account.save()
                new_tx = Transaction.objects.create(
                    sender=account.owner, receiver="Cash", amount=amount, tx_type='WDL'
                )
            return redirect('transaction_receipt', ref_id=new_tx.ref_id)
    return redirect('customer_dashboard')

@login_required
def transaction_receipt(request, ref_id):
    tx = get_object_or_404(Transaction, ref_id=ref_id)
    return render(request, 'receipt.html', {'tx': tx})

@user_passes_test(is_admin)
def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.delete()
    return redirect('boss_portal')