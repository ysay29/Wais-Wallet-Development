from django.db import models
from django.contrib.auth.models import User  # Import User model to associate spending with a user


class MonthlySpending(models.Model):
    """
    Model to store monthly spending data.
    """
    MONTH_CHOICES = [
        ('Jan', 'January'), ('Feb', 'February'), ('Mar', 'March'),
        ('Apr', 'April'), ('May', 'May'), ('Jun', 'June'),
        ('Jul', 'July'), ('Aug', 'August'), ('Sep', 'September'),
        ('Oct', 'October'), ('Nov', 'November'), ('Dec', 'December'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="monthly_spending")  # Link spending to a user
    month = models.CharField(max_length=10, choices=MONTH_CHOICES, verbose_name="Month")
    food = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Food Spending")
    utilities = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Utilities Spending")
    apparel = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Apparel Spending")

    def __str__(self):
        return f"{self.get_month_display()} - Spending"

class MonthlyFinance(models.Model):
    """
    Model to store monthly financial data.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="monthly_finance")
    month = models.DateField(verbose_name="Month")  # Use first day of the month
    income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Income")
    expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Expenses")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def balance(self):
        return self.income - self.expenses

    def __str__(self):
        return f"{self.month.strftime('%B %Y')} - Balance: ₱{self.balance:,.2f}"

    class Meta:
        unique_together = ('user', 'month')
        ordering = ['-month']