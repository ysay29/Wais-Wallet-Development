from django.utils.timezone import localtime, now
from datetime import timedelta
from .models import Reminder, Notification

def send_transaction_reminders():
    print("Send transaction reminders task executed")

    now_local = localtime(now())  # Get current local datetime
    time_lower = (now_local - timedelta(seconds=30)).time()
    time_upper = (now_local + timedelta(seconds=30)).time()
    today = now_local.date()

    print("Now:", now_local.time())
    print("Window:", time_lower, "to", time_upper)

    reminders = Reminder.objects.filter(
        alert_time__gte=time_lower,
        alert_time__lte=time_upper,
        enabled=True
    )

    print(f"Found {reminders.count()} reminders.")

    for reminder in reminders:
        already_sent = Notification.objects.filter(
            user=reminder.user,
            message__icontains="Reminder: Don't forget to add your transaction!",
            timestamp__date=today
        ).exists()

        if not already_sent:
            Notification.objects.create(
                user=reminder.user,
                message="Reminder: Don't forget to add your transaction!"
            )
            print(f"Notification sent to {reminder.user.username}")
        else:
            print(f"Skipped: Notification already sent to {reminder.user.username}")
