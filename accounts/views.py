from django.shortcuts import render,redirect # Add redirect
from .models import Account
from .forms import AccountForm  # Import your new form
from django.db.models import Sum 
from django.shortcuts import get_object_or_404 #


def account_list(request):
     #--part A:Handle New creation--
     
    if request.method =='POST':
        form=AccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('account_list') # Refresh page after saving
    else:
        form =AccountForm()
        
     
    #---part B: Handle search and Display (Existing logic)--
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
        'query': query ,
        'form':form #Send the form to the template
        })  
def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.delete()
    return redirect('account_list')