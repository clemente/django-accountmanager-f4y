"""f4y URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from accounts.api import AccountResource, TransactionResource
from accounts.views import AccountListView, account_and_transactions

account_resource = AccountResource()
transaction_resource = TransactionResource()

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^api/', include(account_resource.urls)),
    url(r'^api/', include(transaction_resource.urls)),

    url(r'^$', AccountListView.as_view(), name='account-list'),
    url(r'^account/(?P<number>\d{8})/$', account_and_transactions, name='account-detail'),
]
