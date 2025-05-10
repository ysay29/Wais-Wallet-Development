from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth import logout
from .models import Notification, Reminder
from .forms import ReminderForm
from django.utils import timezone
from Transaction.models import Transaction
from django.db.models import Sum
from datetime import timedelta



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
    today = timezone.now()
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)

    # Current month transactions
    this_month_incomes = Transaction.objects.filter(
        user=user, type='Income',
        date__gte=first_day_this_month, date__lte=today
    )
    this_month_expenses = Transaction.objects.filter(
        user=user, type='Expense',
        date__gte=first_day_this_month, date__lte=today
    )

    # Last month transactions
    last_month_incomes = Transaction.objects.filter(
        user=user, type='Income',
        date__gte=first_day_last_month, date__lte=last_day_last_month
    )
    last_month_expenses = Transaction.objects.filter(
        user=user, type='Expense',
        date__gte=first_day_last_month, date__lte=last_day_last_month
    )

    recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]
     # Totals
    total_income = this_month_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = this_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    savings = total_income - total_expenses

    last_income = last_month_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    last_expenses = last_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    last_savings = last_income - last_expenses
    # Percent changes (avoid division by zero)
    def percent_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    income_change = percent_change(total_income, last_income)
    expense_change = percent_change(total_expenses, last_expenses)
    savings_change = percent_change(savings, last_savings)

    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]

    context = {
        'income': total_income,
        'expenses': total_expenses,
        'savings': savings,
        'income_change': income_change,
        'expense_change': expense_change,
        'savings_change': savings_change,
        'recent_transactions': recent_transactions,
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