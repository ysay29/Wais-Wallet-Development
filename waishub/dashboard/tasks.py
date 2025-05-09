from django.utils.timezone import now
from .models import Reminder, Notification
from datetime import timedelta


def send_transaction_reminders():
    now_time = now().time().replace(second=0, microsecond=0)
    plus_one = (now() + timedelta(minutes=1)).time().replace(second=0, microsecond=0)
    today = now().date()
    reminders = Reminder.objects.filter(alert_time__gte=now_time, alert_time__lt=plus_one)
    # Filter reminders for the next minute


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
print("Scheduler is running at", now())
