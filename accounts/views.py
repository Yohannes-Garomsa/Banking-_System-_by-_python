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
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .models import Account, Transaction, OnboardingApplication
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
                with transaction.atomic():
                    user = form.save()
                    Account.objects.get_or_create(
                        user=user, 
                        defaults={'balance': 0.00}
                    )
                messages.success(request, "Account created successfully! You can now login.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"An error occurred during signup: {e}")
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# --- Boss / Admin Portal ---
@staff_member_required
@never_cache
def boss_dashboard(request):
    """The Modern Bank Admin Portal Command Center with Search & Management"""
    
    # 1. Handle Account Search (Search by Account Number or Username)
    acc_query = request.GET.get('acc_search', '')
    if acc_query:
        accounts_list = Account.objects.filter(
            Q(account_number__icontains=acc_query) | 
            Q(user__username__icontains=acc_query)
        ).select_related('user')
    else:
        accounts_list = Account.objects.all().order_by('-created_at')[:15]

    # 2. Global Bank Statistics
    total_assets = Account.objects.aggregate(Sum('balance'))['balance__sum'] or 0
    total_customers = Account.objects.count()
    
    # 3. KYC Applications logic
    pending_apps = OnboardingApplication.objects.filter(status='pending').order_by('-created_at')
    app_query = request.GET.get('search')
    if app_query:
        pending_apps = pending_apps.filter(full_name__icontains=app_query)
    
    pending_count = pending_apps.count()
    recent_transactions = Transaction.objects.all().order_by('-timestamp')[:10]

    return render(request, 'accounts/admin_dashboard.html', {
        'accounts': accounts_list,
        'applications': pending_apps,
        'total_assets': total_assets,
        'total_customers': total_customers,
        'pending_count': pending_count,
        'history': recent_transactions,
        'query': app_query,
        'acc_query': acc_query,
    })

@staff_member_required
def approve_kyc(request, app_id):
    """Approves a Geda Bank Application and opens an account"""
    application = get_object_or_404(OnboardingApplication, id=app_id)
    
    if application.status == 'pending':
        try:
            # Note: In a real system, you'd link this to a NEW user, 
            # for now, we follow your logic of creating the Account model entry.
            with transaction.atomic():
                application.status = 'approved'
                application.save()
                
                Account.objects.create(
                    user=request.user, # Adjust this to link to the specific customer user in production
                    account_number=Account.generate_account_number(),
                    balance=1000.00 
                )
            messages.success(request, f"Vault activated for {application.full_name}!")
        except Exception as e:
            messages.error(request, f"Approval error: {e}")
            
    return redirect('boss_portal')

@staff_member_required
def toggle_freeze(request, pk):
    """Requirement: Security feature to lock/unlock account activity"""
    account = get_object_or_404(Account, pk=pk)
    account.is_frozen = not account.is_frozen
    account.save()
    status = "Frozen" if account.is_frozen else "Active"
    messages.info(request, f"Account {account.account_number} is now {status}.")
    return redirect('boss_portal')

@staff_member_required
def delete_account(request, pk):
    """Close/Delete bank accounts"""
    account = get_object_or_404(Account, pk=pk)
    username = account.user.username
    account.delete()
    messages.warning(request, f"Account for {username} has been closed and deleted.")
    return redirect('boss_portal')

# --- Customer Dashboard & Identity ---
@login_required
def customer_dashboard(request):
    account, created = Account.objects.get_or_create(user=request.user)
    
    my_history = Transaction.objects.filter(
        Q(sender=request.user.username) | Q(receiver=request.user.username)
    ).order_by('-timestamp')

    return render(request, 'accounts/dashboard.html', {
        'account': account,
        'my_history': my_history
    })

@login_required
def identity_verification(request):
    """KYC flow for users needing verification"""
    account, created = Account.objects.get_or_create(user=request.user)
    
    if account.is_verified or getattr(account, 'kyc_step', 0) >= 3:
        return redirect('customer_dashboard')

    if request.method == 'POST':
        kyc_step = getattr(account, 'kyc_step', 1)
        if kyc_step == 1:
            account.phone_number = request.POST.get('phone_number')
            account.kyc_step = 2
            account.save()
        elif kyc_step == 2:
            account.kyc_step = 3
            account.save()
            return redirect('customer_dashboard')

    return render(request, 'accounts/verify_identity.html', {'account': account})

# --- Banking Operations ---

@login_required
def transfer_money(request):
    if request.method == 'POST':
        sender_account = request.user.account
        
        # NEW SECURITY CHECK
        if sender_account.is_frozen:
            messages.error(request, "Transaction Denied: Your account is currently frozen.")
            return redirect('customer_dashboard')

        target_username = request.POST.get('target_user')
        amount = Decimal(request.POST.get('amount', 0))
        try:
            receiver_user = User.objects.get(username=target_username)
            receiver_account = Account.objects.get(user=receiver_user)
            
            if sender_account.balance >= amount and amount > 0:
                with transaction.atomic():
                    sender_account.balance -= amount
                    receiver_account.balance += amount
                    sender_account.save()
                    receiver_account.save()
                    new_tx = Transaction.objects.create(
                        sender=request.user.username, 
                        receiver=target_username,
                        amount=amount, 
                        tx_type='TRF'
                    )
                return redirect('transaction_receipt', ref_id=new_tx.ref_id)
            else:
                messages.error(request, "Insufficient funds.")
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
                sender="External", receiver=request.user.username, amount=amount, tx_type='DEP'
            )
        return redirect('transaction_receipt', ref_id=new_tx.ref_id)
    return redirect('customer_dashboard')

@login_required
def withdraw_money(request):
    if request.method == 'POST':
        account = request.user.account
        
        # NEW SECURITY CHECK
        if account.is_frozen:
            messages.error(request, "Withdrawal Denied: Account is frozen.")
            return redirect('customer_dashboard')

        amount = Decimal(request.POST.get('amount', 0))
        if account.balance >= amount:
            with transaction.atomic():
                account.balance -= amount
                account.save()
                new_tx = Transaction.objects.create(
                    sender=request.user.username, receiver="Cash", amount=amount, tx_type='WDL'
                )
            return redirect('transaction_receipt', ref_id=new_tx.ref_id)
        else:
            messages.error(request, "Insufficient funds.")
    return redirect('customer_dashboard')

@login_required
def transaction_receipt(request, ref_id):
    tx = get_object_or_404(Transaction, ref_id=ref_id)
    return render(request, 'receipt.html', {'tx': tx})

# --- Onboarding Entry Point ---
def onboarding(request):
    if request.user.is_authenticated:
        return redirect('customer_dashboard')
    return render(request,'accounts/onboarding.html')

def submit_onboarding(request):
    if request.method == "POST":
        OnboardingApplication.objects.create(
            full_name=request.POST.get('fullname'),
            country=request.POST.get('country'),
            kebele=request.POST.get('kebele'),
            national_id=request.POST.get('national_id'),
            job_position=request.POST.get('job'),
            age=request.POST.get('age'),
            phone=request.POST.get('phone'),
            is_id_captured=True,
            is_face_captured=True
        )
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)