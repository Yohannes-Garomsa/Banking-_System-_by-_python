from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Sum, Q  # 'Q' is imported here
from django.db import transaction 
from django.views.decorators.cache import never_cache

from .models import Account, Transaction
from .models import Account, Transaction
from .forms import AccountForm, TransferForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.models import User

import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def is_admin(user):
    return user.is_staff # Only staff/admins return True

    
@login_required
def login_success(request):
    if request.user.is_staff:
        return redirect('boss_portal')
    else:
        return redirect('customer_dashboard')


@user_passes_test(is_admin) # This locks the door for regular customers
@login_required
@never_cache
@user_passes_test(lambda u:u.is_staff)
def account_list(request):
    #get all accounts
    accounts=Account.objects.all()
    
    # Specifically count how many are waiting for verification
    pending_count=Account.objects.filter(is_verified=False).count()
    return render(request,'accounts/index.html',{
        'accounts':accounts,
        'pending_count':pending_count
    })
    
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
        account = request.user.account
    except Account.DoesNotExist:
        # If it's an admin, send them to the boss portal
        if request.user.is_staff:
            return redirect('boss_portal')
        # For others, maybe tell them to contact the bank
        messages.error(request, "You do not have a bank account profile.")
        return redirect('login')
    
    account=request.user.account
    # If the user hasn't uploaded their ID yet, send them to verify
    if not account.id_card_photo:
        return redirect('verify_identity')
    
    # If they uploaded it but the Boss hasn't clicked "Approve"
    if not account.is_verified:
        return render(request,'accounts/success_pending.html')
    
    #...otherwise, show the real dashboard ...
    return render(request,'accounts/dashboard.html')
    
    
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
            account=Account.objects.get(user=request.user)
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
                with transaction.atomic():
                    account.balance -=amount
                    account.save()
                    
                    new_tx=Transaction.objects.create(
                        sender=account.owner,
                        receiver="Cash Withdrawal",
                        amount=amount,
                        tx_type='WDL' #WDL for Withdrawal
                    )
                messages.success(request, f"Successfully withdraw ${amount}")
                return redirect('transaction_receipt',ref_id=new_tx.ref_id)
            else:
                messages.error(request, "insufficient funds!")
    return redirect('customer_dashboard')

@login_required
def transfer_money(request):
    #check if the user is verified
    if not request.user.account.is_verified:
        return render(request, 'accounts/success_pending.html')
    
    if request.method =='POST':
        target_username=request.POST.get('target_user')
        amount_str=request.POST.get('amount')
        if target_username and amount_str:
            amount=Decimal(amount_str)
            sender_account=Account.objects.get(user=request.user)
            #1 check if target user exist
            try:
                receiver_user=User.objects.get(username=target_username)
                receiver_account=Account.objects.get(user=receiver_user)
            except(User.DoesNotExist,Account.DoesNotExist):
                messages.error(request, f"User '{target_username}' not found")
                return redirect('customer_dashboard')
            #2 Prevent sending money to your self
            if sender_account == receiver_account:
                messages.error(request, "You cannot send money to you self")
                redirect('customer_dashboard')
            #3 check for sufficient funds
            if sender_account.balance >=amount:
                with transaction.atomic():
                    #deduct from sender
                    sender_account.balance -= amount
                    sender_account.save()
                    
                    #add to receiver 
                    receiver_account.balance +=amount
                    receiver_account.save()
                    
                    #create the official record
                    new_tx =Transaction.objects.create(
                        sender=sender_account.owner,
                        receiver=receiver_account.owner,
                        amount=amount,
                        tx_type='TRF' #TRF for transfer
                    )
                messages.success(request, f"successfully sent ${amount} to {target_username}!")
                return redirect('transaction_receipt',ref_id=new_tx.ref_id)
            else:
                messages.error(request, "Insufficient funds for this transfer.")
    return redirect('customer_dashboard')

def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.delete()
    return redirect('account_list')

@login_required
def identity_verification(request):
    if request.method =='POST':
        id_data=request.POST.get('id_image')
        # Inside the POST check
        phone = request.POST.get('phone_number') # Make sure your HTML has an input with this name
        if phone:
           account.phone_number = phone
        
        if id_data:
            #convert the base64 image from the webcam to file
            format, imgstr =id_data.split(';base64,')
            ext =format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f"id_{request.user.id}.{ext}")
            
            
            #save to the user's account
            account =request.user.account
            account.id_card_photo=data
            account.save()
            
            return redirect('customer_dashboard') # Or a success page
        
    return render(request,'accounts/verify_identity.html')

@user_passes_test(lambda u: u.is_staff)
def approve_account(request, account_id):
    if request.method == "POST":
        account = Account.objects.get(id=account_id)
        account.is_verified = True
        account.save()
        messages.success(request, f"Account for {account.user.username} has been activated!")
    return redirect('boss_portal')
            