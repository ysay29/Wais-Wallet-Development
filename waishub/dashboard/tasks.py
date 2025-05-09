from django.utils.timezone import now
from dashboard.models import Reminder, Notification

def send_transaction_reminders():
    current_time = now().time().replace(second=0, microsecond=0)
    today = now().date()
    reminders = Reminder.objects.filter(alert_time=current_time)

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
