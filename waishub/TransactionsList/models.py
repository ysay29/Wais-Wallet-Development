from django.db import models
from django.utils import timezone

def get_current_month():
    return timezone.now().strftime('%B %Y')

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    type     = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    amount   = models.DecimalField(max_digits=10, decimal_places=2)
    date     = models.DateField(default=timezone.now)
    month    = models.CharField(max_length=20, default=get_current_month)

    def __str__(self):
        return f"{self.type} — {self.category} — ₱{self.amount} ({self.month})"
