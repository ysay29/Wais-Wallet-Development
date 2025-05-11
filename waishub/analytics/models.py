from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models import Sum


class MonthlyFinance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="monthly_finance")
    month = models.DateField(verbose_name="Month", default=date.today)
    income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def balance(self):
        """
        Calculate the balance as income minus expenses.
        """
        return self.income - self.expenses

    def update_finance(self):
        """
        Update the income and expenses for the given month by aggregating data from the Transaction model.
        """
        from Transaction.models import Transaction

        # Ensure the Transaction model has a `date` field for filtering by month
        transactions = Transaction.objects.filter(
            user=self.user,
            date__year=self.month.year,
            date__month=self.month.month
        )

        # Aggregate income and expenses
        self.income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0.00
        self.expenses = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0.00
        self.save()

    def __str__(self):
        """
        String representation of the MonthlyFinance object.
        """
        return f"{self.month.strftime('%B %Y')} - Balance: ₱{self.balance:,.2f}"

    class Meta:
        unique_together = ('user', 'month')  # Ensure one record per user per month
        ordering = ['-month']  # Order by most recent month