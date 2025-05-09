from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth import logout
from .models import Notification, Reminder
from .forms import ReminderForm
from django.utils import timezone
from Transaction.models import Transaction
from django.db.models import Sum


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
    incomes = Transaction.objects.filter(user=user, type='Income')
    expenses = Transaction.objects.filter(user=user, type='Expense')

    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    savings = total_income - total_expenses
    context = {
        'income': total_income,
        'expenses': total_expenses,
        'savings': savings,
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
            reminder.enabled = form.cleaned_data.get('enabled', False)  # Defaults to False if not provided
            reminder.save()
            print("Reminder saved with:")
            print("Alert time:", form.cleaned_data['alert_time'])
            print("Enabled:", form.cleaned_data['enabled'])
            return redirect('settings')

    else:
        form = ReminderForm(instance=reminder)

    return render(request, 'settings.html', {'form': form})