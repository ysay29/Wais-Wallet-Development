from django.db import models
from django.contrib.auth.models import User

class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category_name} ({self.user.username})"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.type} — {self.category} — ₱{self.amount}"

    def formatted_amount(self):
        return f"₱{self.amount:,.2f}"  # This will format the amount with commas and two decimal places

