from django.contrib import admin
from accounts.models import Account, Transaction

class AccountAdmin(admin.ModelAdmin):
    list_display = ('number', 'currency', 'creation_date')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'source_account', 'dest_account', 'source_amount', 'dest_amount')
    def source_account(self,t):
        return t.source_acc.number if t.source_acc else None
    def dest_account(self,t):
        return t.dest_acc.number if t.dest_acc else None


admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)

