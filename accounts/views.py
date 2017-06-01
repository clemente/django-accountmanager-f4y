from django.shortcuts import render
from django.views.generic.list import ListView
from accounts.models import Account

# Create your views here.
class AccountListView(ListView):
    model = Account
