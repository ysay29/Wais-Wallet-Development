from django.db import models
from authentication.models import Profile

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    username = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.type} — {self.category} — ₱{self.amount}"
