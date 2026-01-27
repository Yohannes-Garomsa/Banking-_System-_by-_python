from django.shortcuts import render
from .models import Account
from django.db.models import Sum


def account_list(request):
    # Fetch all bank accounts from the MySQL database
    all_accounts = Account.objects.all() 
    total =all_accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    return render(request, 'index.html', {
        'accounts': all_accounts,
        'total_assets': total})