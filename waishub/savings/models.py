from django.db import models
from django.contrib.auth.models import User

class Saving(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    goal = models.ForeignKey('SavingsGoal', on_delete=models.CASCADE, related_name='savings', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.goal:
            # Recalculate the total savings for this goal
            self.goal.current_amount = self.goal.savings.aggregate(total=models.Sum('amount'))['total'] or 0
            self.goal.save()

    def __str__(self):
        return f"{self.date} - ₱{self.amount} (Goal: {self.goal.name if self.goal else 'None'})"
    
class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='savings_goals')

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

    @property
    def progress_percent(self):
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100

    @property
    def remaining(self):
        return max(self.target_amount - self.current_amount, 0)
