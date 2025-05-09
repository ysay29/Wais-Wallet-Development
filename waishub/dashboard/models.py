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
    
