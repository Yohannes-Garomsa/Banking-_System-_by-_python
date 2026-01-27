from django.shortcuts import render
from .models import Account
from django.db.models import Sum ,Q


def account_list(request):
   
      query =request.GET.get('search')
      if query:
          #filter accounts where the owner's name contains the search query (case-insensitive)
          all_accounts =Account.objects.filter(owner__icontains=query)
      else:
          all_accounts=Account.objects.all()
      # 2. Recalculate total assets based on what is filtered
      total =all_accounts.aggregate(Sum('balance'))['balance__sum'] or 0
      return render(request, 'index.html', {
        'accounts': all_accounts,
        'total_assets': total,
        'query': query # Send the query back so it stays in the search bar
        })  