from django.db import models
from django.core.exceptions import ValidationError


ALLOWED_CURRENCIES = [
    ("USD", "USD: US dollar"),
    ("EUR", "EUR: Euro"),
    ("GBP", "GBP: British pound"),
    ("CHF", "CHF: Swiss frank"),
]

def validate_8digits(number):
    if not (10000000 <= number <= 99999999):
        raise ValidationError("Account numbers must be 8 digits. Yours has %i"%len(str(number)))

class Account(models.Model):
    number = models.PositiveIntegerField(help_text="Account number, 8 digits",unique=True,validators=[validate_8digits])
    currency = models.CharField(max_length=3,choices=ALLOWED_CURRENCIES)
    creation_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "Account number %i"%self.number

#class Transaction(models.Model):
    
