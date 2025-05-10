from django.db import models
from django.contrib.auth.models import User

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
