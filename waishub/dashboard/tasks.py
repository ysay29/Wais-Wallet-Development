from django.utils.timezone import localtime, now
from .models import Reminder, Notification
from datetime import timedelta, timezone

def send_transaction_reminders():
    print("Send transaction reminders task executed")  # Debugging print to check if the task runs
    now_local = localtime(now())  
    time_lower = (now_local - timedelta(minutes=10)).time()
    time_upper = (now_local + timedelta(minutes=10)).time()

    print("Now:", now_local.time())
    print("Window:", time_lower, "to", time_upper)

    reminders = Reminder.objects.filter(
        alert_time__gte=time_lower,
        alert_time__lte=time_upper,
        enabled=True
    )

    print(f"Found {len(reminders)} reminders within the time window.")  # Debug to check if reminders exist

    for reminder in reminders:
        already_sent = Notification.objects.filter(
        user=reminder.user,
        timestamp__date=timezone.localtime().date()
    )

        print(f"Already sent? {already_sent.exists()}")  # Debug message
        if already_sent.exists():
            print(f"Existing notifications: {already_sent}")
        
        if not already_sent:
            print(f"Creating notification for {reminder.user.username}")  # Debug message
            Notification.objects.create(
                user=reminder.user,
                message="Reminder: Don't forget to add your transaction!"
            )
        else:
            print(f"Notification already sent to {reminder.user.username}")
