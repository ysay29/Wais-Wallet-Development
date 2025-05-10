from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    icon_url = models.URLField(default="https://cdn-icons-png.flaticon.com/512/992/992700.png")
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"
    
class Reminder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alert_time = models.TimeField()
    enabled = models.BooleanField(default=True)  #Notification enabled by default

    def __str__(self):
        return f"{self.user.username} - {self.alert_time}"
    
class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'user')  # prevent duplicates per user

    def __str__(self):
        return self.name
    
class Budget(models.Model):
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    review_period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - ₱{self.amount}"

    