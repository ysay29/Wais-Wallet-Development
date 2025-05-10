from django.db import models
from django.contrib.auth.models import User
<<<<<<< HEAD

=======
>>>>>>> 89542f6e6a337578c0973ae1b2b9bedfb71182d6

class Saving(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    goal_term = models.CharField(max_length=100, blank=True)  # e.g., '6 months'
    reminder_frequency = models.CharField(max_length=100, blank=True)  # e.g., 'weekly'

    def __str__(self):
        return f"{self.date} - {self.category}: ₱{self.amount}"
    
class SavingsGoal(models.Model):
    TERM_CHOICES = [
        ('3 months', '3 months'),
        ('6 months', '6 months'),
        ('1 year', '1 year'),
        ('2 years', '2 years'),
    ]

    REMINDER_CHOICES = [
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
    ]

    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    reminder = models.CharField(max_length=20, choices=REMINDER_CHOICES)

    def progress_percent(self):
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100