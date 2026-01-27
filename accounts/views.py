from django.shortcuts import render
from .models import Account

def account_list(request):
    # Fetch all bank accounts from the MySQL database
    all_accounts = Account.objects.all() 
    return render(request, 'index.html', {'accounts': all_accounts})