from django.db import models
from django.core.exceptions import ValidationError


ALLOWED_CURRENCIES = [
    ("USD", "USD: US dollar"),
    ("EUR", "EUR: Euro"),
    ("GBP", "GBP: British pound"),
    ("CHF", "CHF: Swiss frank"),
]
OPERATION_TYPES = [
    ("dep", "Deposit (add money)"),
    ("wd", "Withdrawal (take money)"),
    ("tra", "Transfer (move money)"), # with same or different currency
]

def validate_8digits(number):
    if not (10000000 <= number <= 99999999):
        raise ValidationError("Account numbers must be 8 digits. Yours has %i"%len(str(number)))

class Account(models.Model):
    number = models.PositiveIntegerField(help_text="Account number, 8 digits",unique=True,blank=True,null=False,validators=[validate_8digits])
    currency = models.CharField(max_length=3,choices=ALLOWED_CURRENCIES)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Account number %i"%self.number

    def save(self):
        if not self.number:
            # Give sequential IDs automatically
            try:
                self.number = Account.objects.latest('number').number+1
            except Account.DoesNotExist:
                self.number = 1
        super(Account, self).save()

class Transaction(models.Model):
    """
    A transaction includes widthdrawals, deposits and internal transfers. We consider withdrawal=="transfer to null account", deposit=="transfer from null account".
    """
    # id: implicit. Unique. Note that e.g. a deposit and withdrawal can't share id either
    date = models.DateTimeField()
    op_type = models.CharField(max_length=3,choices=OPERATION_TYPES,verbose_name="Operation type",) # stored as field so that we know which fields should be null/not-null without having to detect it
    source_acc = models.ForeignKey(Account,blank=True,null=True,verbose_name="Source account",help_text="Used in transfers; must be blank for deposits",related_name="transactions_with_this_source")
    dest_acc = models.ForeignKey(Account,blank=True,null=True,verbose_name="Destination account",help_text="Used in transfers; must be blank for withdrawals",related_name="transactions_with_this_dest")
    source_amount = models.FloatField(help_text="Amount in source account's currency, or in withdrawal account's currency. Not used in deposits", blank=True, null=True)
    dest_amount = models.FloatField(help_text="Amount in destination account's currency, or in deposit account's currency. Not used in withdrawals", blank=True, null=True)
    # I don't implement (because not required):
    # - currency_rate: official money exchange rate used in this transaction. Can be computed approximately by dividing source_amount/dest_amount
    # - currency_date: timestamp of the currency rate used for the transaction
    creation_date = models.DateTimeField(auto_now_add=True) # Probably the same as "date" (except for DB migrations, etc.), but it's safe to store both

    def clean(self):
        if self.op_type=='dep':
            if self.source_amount or not self.dest_amount:
                raise ValidationError("Deposits must have just a destination amount")
            if self.source_acc or not self.dest_acc:
                raise ValidationError("Deposits must have just a destination account")
        elif self.op_type=='wd':
            if not self.source_amount or self.dest_amount:
                raise ValidationError("Withdrawals must have just a source amount")
            if not self.source_acc or self.dest_acc:
                raise ValidationError("Withdrawals must have just a source account")
        elif self.op_type=='tra':
            if not self.source_amount or not self.dest_amount:
                raise ValidationError("Transfers must have both amounts")
            if not self.source_acc or not self.dest_acc:
                raise ValidationError("Transfers must have both accounts")
        else:
            raise NotImplementedError(self.op_type)
