from django.contrib import admin
from accounts.models import Account

class AccountAdmin(admin.ModelAdmin):
    list_display = ('number', 'currency', 'creation_date')

admin.site.register(Account, AccountAdmin)
