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

    # Extend transaction history with partial balances (i.e. how much do we have after each operation). This is fast if there are few transactions. See the comment en models.Account.balance about how to improve/avoid this real-time calculation
    #trans[0].partialbalance=51
    amounts_columns=[]
    accum=0
    for tr in trans.all():
        if tr.op_type=='tra' and tr.source_acc==account:
            change = -tr.source_amount
        elif tr.op_type=='tra' and tr.dest_acc==account:
            change = + tr.dest_amount
        elif tr.op_type=='wd':
            change = - tr.source_amount
        elif tr.op_type=='dep':
            change = + tr.dest_amount
        else:
            raise NotImplementedError(tr.op_type)
        accum+=change
        amounts_columns.append({'change':change,'accum':accum})

    # Now that we we're here…
    if accum != account.balance:
        raise Exception("Some past operation didn't update the balance, and now reconstructing the transaction history doesn't produce the current balance. Check code. %f vs %f"%(accum,account.balance))
    #partialbalances=[51,1,51,35,53,56]


    return render(request, 'accounts/account_details.html', {
        'account': account,
        #'transactions': trans,
        # This zip() will allow us to consume two lists at the same time in the template
        'transactions_and_amountscolumns': zip(trans,amounts_columns),
    })
