from django.utils.timezone import localtime, now
from .models import Reminder, Notification
from datetime import timedelta

def send_transaction_reminders():
    now_local = localtime(now())  
    time_lower = (now_local - timedelta(seconds=30)).time()
    time_upper = (now_local + timedelta(seconds=30)).time()

    print("Now:", now_local.time())
    print("Window:", time_lower, "to", time_upper)

    reminders = Reminder.objects.filter(
        alert_time__gte=time_lower,
        alert_time__lte=time_upper,
        enabled=True  # ✅ Only send to users who enabled it
    )

    today = now_local.date() 

    for reminder in reminders:
        already_sent = Notification.objects.filter(
            user=reminder.user,
            message__icontains="add your transaction",
            timestamp__date=today
        ).exists()

        if not already_sent:
            Notification.objects.create(
                user=reminder.user,
                message="Reminder: Don't forget to add your transaction!"
            )
            print(f"Notification sent to {reminder.user.username}")
