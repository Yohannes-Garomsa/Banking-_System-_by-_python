from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.db import transaction  # Crucial for professional banking
from .models import Account
from .forms import AccountForm, TransferForm

def account_list(request):
    # 1. Handle "Add New Account" (Existing logic)
    form = AccountForm()
    if request.method == 'POST' and 'add_account' in request.POST:
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('account_list')

    # 2. Handle "Transfer Money" (New Professional Logic)
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
                # 'with transaction.atomic()' ensures either BOTH accounts update or NEITHER do.
                with transaction.atomic():
                    sender.balance -= amount
                    receiver.balance += amount
                    sender.save()
                    receiver.save()
                return redirect('account_list')
            else:
                transfer_form.add_error('amount', "Insufficient funds!")

    # 3. Handle Search and Display
    query = request.GET.get('search')
    all_accounts = Account.objects.filter(owner__icontains=query) if query else Account.objects.all()
    total = all_accounts.aggregate(Sum('balance'))['balance__sum'] or 0

    return render(request, 'index.html', {
        'accounts': all_accounts,
        'total_assets': total,
        'query': query,
        'form': form,
        'transfer_form': transfer_form,
    })

# Add the Delete view below it
def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.delete()
    return redirect('account_list')