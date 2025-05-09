from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth import logout
from .models import Notification, Transaction, Reminder
from .forms import ReminderForm
from django.utils import timezone

#@login_required
def index(request):
    return render(request, 'index.html')  # Your dashboard template

def logout_user(request):
    logout(request)
    return redirect('login') 

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def index(request):
    user = request.user
    recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]

    context = {
        'recent_transactions': recent_transactions
    }
    return render(request, 'index.html', context)

@login_required
def notifications_view(request):
    user = request.user
    today = timezone.localtime().date()

    notifications = Notification.objects.filter(user=user).order_by('-timestamp')
    today_notifications = notifications.filter(timestamp__date=today)
    older_notifications = notifications.exclude(timestamp__date=today)
    unread_count = notifications.filter(read=False).count()
    reminder_notifications = notifications.filter(message__icontains="Reminder")

    context = {
        'today_notifications': today_notifications,
        'older_notifications': older_notifications,
        'unread_count': unread_count,
        'reminder_notifications': reminder_notifications,
    }
    return render(request, 'notifications.html', context) # Your notifications template

@login_required
def settings_view(request):
    try:
        reminder = Reminder.objects.get(user=request.user)
    except Reminder.DoesNotExist:
        reminder = None

    if request.method == 'POST':
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            print("Reminder saved with:")
            print("Alert time:", form.cleaned_data['alert_time'])
            print("Enabled:", form.cleaned_data['enabled'])
            return redirect('settings')

    else:
        form = ReminderForm(instance=reminder)

    return render(request, 'settings.html', {'form': form})