from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q  # 'Q' is imported here
from django.db import transaction 
from django.views.decorators.cache import never_cache

from .models import Account, Transaction
from .models import Account, Transaction
from .forms import AccountForm, TransferForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from decimal import Decimal



@login_required
@never_cache
def account_list(request):
    if not request.user.is_staff:
        return redirect('customer_dashboard')
   # 1. Handle "Add New Account"
    form = AccountForm()
    if request.method == 'POST' and 'add_account' in request.POST:
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('account_list')

    # 2. Handle "Transfer Money"
    transfer_form = TransferForm()
    if request.method == 'POST' and 'make_transfer' in request.POST:
        transfer_form = TransferForm(request.POST)
        if transfer_form.is_valid():
            sender = transfer_form.cleaned_data['sender']
            receiver = transfer_form.cleaned_data['receiver']
            amount = transfer_form.cleaned_data['amount']

            if sender.id == receiver.id:
                transfer_form.add_error('receiver', "Cannot transfer to the same account!")
            elif sender.balance >= amount:
                with transaction.atomic():
                    sender.balance -= amount
                    receiver.balance += amount
                    sender.save()
                    receiver.save()
                    
                    Transaction.objects.create(
                        sender=sender.owner,
                        receiver=receiver.owner,
                        amount=amount
                    )
                return redirect('account_list')
            else:
                transfer_form.add_error('amount', "Insufficient funds!")

    # 3. Handle Search and Display
    query = request.GET.get('search')
    all_accounts = Account.objects.filter(owner__icontains=query) if query else Account.objects.all()
    total = all_accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    
    history = Transaction.objects.all().order_by('-timestamp')

    return render(request, 'index.html', {
        'accounts': all_accounts,
        'total_assets': total,
        'query': query,
        'form': form,
        'transfer_form': transfer_form,
        'history': history,
    })

@login_required
def customer_dashboard(request):
    try:
        # Get account linked to logged-in user
        account = Account.objects.get(user=request.user)
        
        # We use Q directly here since it was imported from django.db.models
        my_history = Transaction.objects.filter(
            Q(sender=account.owner) | Q(receiver=account.owner)
        ).order_by('-timestamp')
        
    except Account.DoesNotExist:
        return redirect('account_list')

    return render(request, 'customer_dashboard.html', {
        'account': account,
        'my_history': my_history
    })

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically create a Bank Account for the new user
            Account.objects.create(
                user=user, 
                owner=user.username, 
                balance=0.00
            )
            messages.success(request, "Account created successfully! You can now login.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def transaction_receipt(request, ref_id):
    #find the specific transaction by its reference id
    tx=get_object_or_404(Transaction, ref_id=ref_id)
    
    #security:Ensure only the sender or receiver can view the receipt
    account =Account.objects.get(user=request.user)
    if tx.sender !=account.owner and tx.receiver !=account.owner:
        return redirect('customer_dashboard')
    return render(request, 'receipt.html', {'tx':tx})

@login_required
def deposit_money(request):
    if request.method =='POST':
        amount_str=request.POST.get('amount')
        if amount_str:
            amount= Decimal(amount_str)
            Account=Account.objects.get(user=request.user)
            with transaction.atomic():
                #1Update balance
                account.balance +=amount
                account.save()
                #2 create Transaction Record
                new_tx=Transaction.objects.create(
                    sender="External Source",
                    receiver=account.owner,
                    amount=amount,
                    tx_type='DEP'#DEP for deposit
                )
            messages.success(request, f"Successfully deposited ${amount}")
            return redirect('transaction_receipt',ref_id=new_tx.ref_id)
    return redirect('customer_dashboard')
@login_required
def withdraw_money(request):
    if request.method =='POST':
        amount_str=request.POST.get('amount')
        if amount_str:
            amount=Decimal(amount_str)
            account =Account.objects.get(user=request.user)
            if account.balance >=amount:
                with transaction.Atomic():
                    account.balance -=amount
                    account.save()
                    
                    new_tx=Transaction.objects.create(
                        sender=account.owner,
                        receiver="Cash Withdrawal",
                        amount=amount,
                        tx_type='WDL' #WDL for Withdrawal
                    )
                messages.success(request, f"withdraw ${amount}")
                return redirect('transaction_receipt',ref_id=new_tx.ref_id)
            else:
                messages.error(request, "insufficient funds!")
    return redirect('customer_dashboard')
            

def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.delete()
    return redirect('account_list')