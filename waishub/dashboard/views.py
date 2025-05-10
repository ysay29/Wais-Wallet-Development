from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.contrib import messages
from django.contrib.auth import logout
from .models import Notification, Reminder, Budget, Category
from .forms import ReminderForm
from django.utils import timezone
from Transaction.models import Transaction
from django.db.models import Sum
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from Transaction.models import Transaction, UserCategory
from django.utils.dateparse import parse_date



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

    # Check if there are any unread notifications
    has_unread_notifications = Notification.objects.filter(user=user, read=False).exists()

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
        'has_unread_notifications': has_unread_notifications, 
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

@require_POST
@login_required
def mark_notification_read(request):
    notif_id = request.POST.get('notif_id')
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.read = True
        notif.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)
    
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

@login_required
def add_expense(request):
    user = request.user

    # Get distinct expense categories for the logged-in user
    categories = UserCategory.objects.filter(user=user).values_list('category_name', flat=True)

    if request.method == 'POST':
        category = request.POST.get('category')
        new_category = request.POST.get('new_category')

        # Use new_category if it's provided
        final_category = new_category if new_category else category

        amount = request.POST.get('amount')
        review_period = request.POST.get('review_period')

        if final_category and amount and review_period:
            # Optionally save new category to UserCategory if it's new
            if new_category:
                UserCategory.objects.get_or_create(user=user, category_name=new_category)

            Budget.objects.create(
                user=user,
                category=final_category,
                amount=amount,
                review_period=review_period
            )
            messages.success(request, 'Budget saved successfully!')
            return redirect('add_expense')
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'addexpenses.html', {'categories': categories})


def filter_dashboard_data(request):
    filter_type = request.GET.get('type')
    date_str = request.GET.get('date')
    
    today = datetime.today().date()
    
    if filter_type == 'day':
        start = end = today
    elif filter_type == 'week':
        start = today - timedelta(days=today.weekday())  # Monday
        end = start + timedelta(days=6)
    elif filter_type == 'month':
        start = today.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif filter_type == 'year':
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
    elif filter_type == 'date' and date_str:
        date = parse_date(date_str)
        start = end = date
    else:
        return JsonResponse({'error': 'Invalid filter'}, status=400)

    transactions = Transaction.objects.filter(date__range=[start, end], user=request.user)

    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    savings = income - expenses

    # Grouping for chart (example: day-based labels)
    grouped = {}
    for tx in transactions:
        label = tx.date.strftime('%b %d')
        grouped[label] = grouped.get(label, 0) + tx.amount if tx.type == 'expense' else grouped.get(label, 0)

    chart_data = {
        'labels': list(grouped.keys()),
        'values': list(grouped.values())
    }

    tx_list = [
        {
            'category': t.category,
            'amount': float(t.amount),
            'type': t.type
        } for t in transactions.order_by('-date')[:5]
    ]

    return JsonResponse({
        'income': income,
        'expenses': expenses,
        'savings': savings,
        'chart_data': chart_data,
        'transactions': tx_list
    })