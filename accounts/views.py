from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from accounts.models import Account, Transaction
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

class AccountListView(ListView):
    model = Account

def account_and_transactions(request, number):
    account = get_object_or_404(Account, number=number)
    trans = Transaction.objects.filter(Q(source_acc=account)|Q(dest_acc=account)).order_by('date')
    return render(request, 'accounts/account_details.html', {
        'account': account,
        'transactions': trans,
    })
