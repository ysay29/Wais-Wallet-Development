from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.contrib import messages
from django.contrib.auth import logout
from .models import Notification, Reminder, Budget, Category
from .forms import ReminderForm
from django.utils import timezone
from Transaction.models import Transaction
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from Transaction.models import Transaction, UserCategory
from django.utils.dateparse import parse_date
from savings.models import Saving, SavingsGoal
from savings.views import savings_summary
import json
from django.utils.timezone import localdate
from django.shortcuts import get_object_or_404




def landing(request):
    return render(request, 'landing.html')  # Your dashboard template

def aboutus(request):
    return(render, 'aboutus.html')


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
        user=user, type__iexact='income',
        date__gte=first_day_this_month, date__lte=today
    )
    this_month_expenses = Transaction.objects.filter(
        user=user, type__iexact='expense',
        date__gte=first_day_this_month, date__lte=today
    )

    # Last month transactions
    last_month_incomes = Transaction.objects.filter(
        user=user, type__iexact='income',
        date__gte=first_day_last_month, date__lte=last_day_last_month
    )
    last_month_expenses = Transaction.objects.filter(
        user=user, type__iexact='expense',
        date__gte=first_day_last_month, date__lte=last_day_last_month
    )

    recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]
     # Totals
    total_income = this_month_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = this_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # --- Savings: Use actual savings from savings_summary ---
    from savings.models import Saving
    from decimal import Decimal

    # Get all savings for this user for the current month
    savings_qs = Saving.objects.filter(
        user=user,
        date__gte=first_day_this_month,
        date__lte=today
    )
    savings_actual = sum(s.amount for s in savings_qs) or 0

    # Theoretical savings (income - expenses)
    savings_max = total_income - total_expenses

    # Clamp savings to not exceed (income - expenses)
    savings = min(savings_actual, savings_max)

    # --- Last month savings for percent change ---
    last_income = last_month_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    last_expenses = last_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    last_month_savings_qs = Saving.objects.filter(
        user=user,
        date__gte=first_day_last_month,
        date__lte=last_day_last_month
    )
    last_month_savings_actual = sum(s.amount for s in last_month_savings_qs) or 0
    last_savings_max = last_income - last_expenses
    last_savings = min(last_month_savings_actual, last_savings_max)

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

    # Chart data for dashboard (aggregate by month for current year)
    from django.db.models.functions import TruncMonth
    # Use Transaction directly for accurate per-user aggregation
    transactions = Transaction.objects.filter(user=user)
    monthly_data = transactions.annotate(
        month=TruncMonth('date')
    ).values('month').order_by('month').annotate(
        income=Sum('amount', filter=Q(type__iexact='income')),
        expenses=Sum('amount', filter=Q(type__iexact='expense'))
    )

    labels = []
    income_chart = []
    expenses_chart = []
    balance_chart = []

    for entry in monthly_data:
        month = entry['month']
        income_val = entry['income'] or 0
        expenses_val = entry['expenses'] or 0
        labels.append(month.strftime('%B %Y'))
        income_chart.append(float(income_val))
        expenses_chart.append(float(expenses_val))
        balance_chart.append(float(income_val) - float(expenses_val))

    # Fetch all budgets for the user
    budgets = Budget.objects.filter(user=user).select_related('category')

    # --- Savings Goals Reminders ---
    # Send a notification if a goal's reminder is due and within its term and matches alert_time
    from savings.models import SavingsGoal
    today = localdate()
    now_time = timezone.localtime().time()
    # Get user's reminder (for alert_time)
    try:
        user_reminder = Reminder.objects.get(user=user)
        alert_time = user_reminder.alert_time
        notif_enabled = user_reminder.enabled
    except Reminder.DoesNotExist:
        alert_time = None
        notif_enabled = False

    goals = SavingsGoal.objects.filter(user=user)
    for goal in goals:
        # Calculate goal term end date
        start_date = goal.created_at.date() if hasattr(goal, 'created_at') and goal.created_at else today
        if goal.term == '3 months':
            end_date = start_date + timedelta(days=90)
        elif goal.term == '6 months':
            end_date = start_date + timedelta(days=180)
        elif goal.term == '1 year':
            end_date = start_date + timedelta(days=365)
        elif goal.term == '2 years':
            end_date = start_date + timedelta(days=730)
        else:
            end_date = start_date + timedelta(days=365)

        # Only remind if within term and notifications are enabled and alert_time matches
        if start_date <= today <= end_date and notif_enabled and alert_time:
            # Check if reminder is due today and at the correct time (±2 min window)
            reminder_due = False
            # Use correct field for reminder frequency
            if goal.reminder == 'Daily':
                reminder_due = True
            elif goal.reminder == 'Weekly' and today.weekday() == 0:
                reminder_due = True
            elif goal.reminder == 'Monthly' and today.day == 1:
                reminder_due = True
            elif goal.reminder == 'Quarterly' and today.month in [1, 4, 7, 10] and today.day == 1:
                reminder_due = True

            # Only send at the correct time (±2 min window)
            if reminder_due and abs((datetime.combine(today, alert_time) - datetime.combine(today, now_time)).total_seconds()) < 120:
                already_sent = Notification.objects.filter(
                    user=user,
                    message__icontains=f"Add  savings for goal {goal.name}",
                    timestamp__date=today
                ).exists()
                if not already_sent:
                    Notification.objects.create(
                        user=user,
                        message=f"Add  savings for goal {goal.name}"
                    )

    # Transaction reminder (not for goals)
    if notif_enabled and alert_time:
        now_time = timezone.localtime().time()
        send_reminder = abs((datetime.combine(today, alert_time) - datetime.combine(today, now_time)).total_seconds()) < 120
        already_sent = Notification.objects.filter(
            user=user,
            message__icontains="Reminder: Don't forget to add your transaction!",
            timestamp__date=today
        ).exists()
        if send_reminder and not already_sent:
            Notification.objects.create(
                user=user,
                message="Reminder: Don't forget to add your transaction!"
            )

    # Calculate if each budget is exceeded for the current review period
    today = timezone.localdate()
    for budget in budgets:
        # Determine period start and end
        if budget.review_period == 'weekly':
            period_start = today - timedelta(days=today.weekday())
            period_end = period_start + timedelta(days=6)
        elif budget.review_period == 'monthly':
            period_start = today.replace(day=1)
            next_month = (period_start + timedelta(days=32)).replace(day=1)
            period_end = next_month - timedelta(days=1)
        elif budget.review_period == 'quarterly':
            quarter = (today.month - 1) // 3 + 1
            period_start = today.replace(month=3 * quarter - 2, day=1)
            if quarter < 4:
                next_quarter_month = 3 * quarter + 1
                next_quarter_year = today.year
            else:
                next_quarter_month = 1
                next_quarter_year = today.year + 1
            next_quarter = period_start.replace(year=next_quarter_year, month=next_quarter_month, day=1)
            period_end = next_quarter - timedelta(days=1)
        else:
            period_start = today
            period_end = today

        # Sum all expenses for this category and period
        period_expenses = Transaction.objects.filter(
            user=user,
            category=budget.category.name,
            type__iexact='expense',
            date__gte=period_start,
            date__lte=period_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Mark as exceeded if expenses > budget amount
        budget.exceeded = float(period_expenses) > float(budget.amount)

        # --- Overspending Notification: only once per day ---
        if budget.exceeded:
            already_sent = Notification.objects.filter(
                user=user,
                message__icontains=f"Overspending Warning on {budget.category.name}",
                timestamp__date=today  # Only check for today, not period_start
            ).exists()
            if not already_sent:
                Notification.objects.create(
                    user=user,
                    message=f"Overspending Warning on {budget.category.name}"
                )

    context = {
        'income': total_income,
        'expenses': total_expenses,
        'savings': savings,
        'income_change': income_change,
        'expense_change': expense_change,
        'savings_change': savings_change,
        'recent_transactions': recent_transactions,
        'has_unread_notifications': has_unread_notifications, 
        'budgets': budgets,
        # Chart context for dashboard chart.js
        'months': json.dumps(labels),
        'income_chart': json.dumps(income_chart),
        'expenses_chart': json.dumps(expenses_chart),
        'balance_chart': json.dumps(balance_chart),
        'has_data': bool(labels),
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
    # Show all reminders, including goal reminders (with or without "Reminder" prefix)
    reminder_notifications = notifications.filter(
        Q(message__icontains="Reminder") | Q(message__icontains="Add  savings for goal") | Q(message__icontains="Add your savings for")
    )

    context = {
        'today_notifications': today_notifications,
        'older_notifications': older_notifications,
        'unread_count': unread_count,
        'reminder_notifications': reminder_notifications.distinct(),
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

@require_POST
@login_required
def delete_notification(request):
    notif_id = request.POST.get('notif_id')
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.delete()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@require_POST
@login_required
def delete_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'success'})

@require_POST
@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    budget.delete()
    messages.success(request, "Budget deleted successfully.")
    return redirect('dashboard')

@require_POST
@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    transaction.delete()
    messages.success(request, "Transaction deleted successfully.")
    return redirect('transactions')

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
            # Save the enabled state and alert_time from the form
            reminder.enabled = form.cleaned_data.get('enabled', False)
            reminder.alert_time = form.cleaned_data.get('alert_time')
            reminder.save()
            messages.success(request, "Reminder settings saved successfully.")
            return redirect('dashboard')  # Redirect to dashboard after saving
    else:
        form = ReminderForm(instance=reminder)

    return render(request, 'settings.html', {'form': form})

@login_required
def update_username(request):
    if request.method == "POST":
        new_username = request.POST.get("username")
        if new_username:
            request.user.username = new_username
            request.user.save()
            return redirect('settings')
    return redirect('settings')

@login_required
def add_expense(request):
    user = request.user

    # Only show categories that are actually used for expenses in the transaction list
    expense_categories = (
        Transaction.objects.filter(user=user, type__iexact='expense')
        .values_list('category', flat=True)
        .distinct()
    )

    if request.method == 'POST':
        category_name = request.POST.get('category')
        new_category = request.POST.get('new_category')
        final_category_name = new_category if new_category else category_name
        amount = request.POST.get('amount')
        review_period = request.POST.get('review_period')

        if final_category_name and amount and review_period:
            from .models import Category
            category_obj, _ = Category.objects.get_or_create(
                name=final_category_name,
                defaults={'user': user}
            )
            if category_obj.user_id is None:
                category_obj.user = user
                category_obj.save()

            # --- Replace existing budget for this user/category/review_period ---
            Budget.objects.filter(
                user=user,
                category=category_obj,
                review_period=review_period
            ).delete()

            # --- Overspending Notification Logic ---
            today = timezone.localdate()
            if review_period == 'daily':
                period_start = today
                period_end = today
            elif review_period == 'weekly':
                period_start = today - timedelta(days=today.weekday())
                period_end = period_start + timedelta(days=6)
            elif review_period == 'monthly':
                period_start = today.replace(day=1)
                next_month = (period_start + timedelta(days=32)).replace(day=1)
                period_end = next_month - timedelta(days=1)
            elif review_period == 'quarterly':
                quarter = (today.month - 1) // 3 + 1
                period_start = today.replace(month=3 * quarter - 2, day=1)
                if quarter < 4:
                    next_quarter_month = 3 * quarter + 1
                    next_quarter_year = today.year
                else:
                    next_quarter_month = 1
                    next_quarter_year = today.year + 1
                next_quarter = period_start.replace(year=next_quarter_year, month=next_quarter_month, day=1)
                period_end = next_quarter - timedelta(days=1)
            else:
                period_start = today
                period_end = today

            # Sum all expenses for this category and period
            period_expenses = Transaction.objects.filter(
                user=user,
                category=final_category_name,
                type__iexact='expense',
                date__gte=period_start,
                date__lte=period_end
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            # Overspending Notification: only once per day
            if float(period_expenses) > float(amount):
                already_sent = Notification.objects.filter(
                    user=user,
                    message__icontains=f"Overspending Warning on {final_category_name}",
                    timestamp__date=timezone.localdate()
                ).exists()
                if not already_sent:
                    Notification.objects.create(
                        user=user,
                        message=f"Overspending Warning on {final_category_name}"
                    )

            Budget.objects.create(
                user=user,
                category=category_obj,
                amount=amount,
                review_period=review_period
            )
            messages.success(request, 'Budget saved successfully!')
            return redirect('add_expense')
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'addexpenses.html', {'categories': expense_categories})

def filter_dashboard_data(request):
    filter_type = request.GET.get('type')
    date_str = request.GET.get('date')
    user = request.user

    today = datetime.today().date()

    # Determine filter range
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

    # Filter transactions for the user and date range
    transactions = Transaction.objects.filter(date__range=[start, end], user=user)

    # Calculate totals
    income = transactions.filter(type__iexact='income').aggregate(total=Sum('amount'))['total'] or 0
    expenses = transactions.filter(type__iexact='expense').aggregate(total=Sum('amount'))['total'] or 0

    # --- Use only actual savings from Saving model for the selected period ---
    from savings.models import Saving
    savings_qs = Saving.objects.filter(
        user=user,
        date__gte=start,
        date__lte=end
    )
    savings = sum(s.amount for s in savings_qs) or 0

    chart_labels = []
    chart_income = []
    chart_expenses = []
    chart_balance = []

    if filter_type == 'year':
        # Group by month for the year
        from django.db.models.functions import TruncMonth
        monthly_data = transactions.annotate(
            month=TruncMonth('date')
        ).values('month').order_by('month').annotate(
            income=Sum('amount', filter=Q(type__iexact='income')),
            expenses=Sum('amount', filter=Q(type__iexact='expense'))
        )
        for entry in monthly_data:
            month = entry['month']
            income_val = entry['income'] or 0
            expenses_val = entry['expenses'] or 0
            chart_labels.append(month.strftime('%b'))  # 'Jan', 'Feb', etc.
            chart_income.append(float(income_val))
            chart_expenses.append(float(expenses_val))
            chart_balance.append(float(income_val) - float(expenses_val))
    else:
        # Group by day for other filters
        date_cursor = start
        daily_income = {t['date']: t['amount'] for t in transactions.filter(type__iexact='income').values('date').annotate(amount=Sum('amount'))}
        daily_expenses = {t['date']: t['amount'] for t in transactions.filter(type__iexact='expense').values('date').annotate(amount=Sum('amount'))}
        while date_cursor <= end:
            label = date_cursor.strftime('%b %d')
            inc = float(daily_income.get(date_cursor, 0))
            exp = float(daily_expenses.get(date_cursor, 0))
            chart_labels.append(label)
            chart_income.append(inc)
            chart_expenses.append(exp)
            chart_balance.append(inc - exp)
            date_cursor += timedelta(days=1)

    # Recent transactions for this filter
    tx_list = [
        {
            'category': t.category,
            'amount': float(t.amount),
            'type': t.type
        } for t in transactions.order_by('-date')[:5]
    ]

    chart_data = {
        'labels': chart_labels,
        'income': chart_income,
        'expenses': chart_expenses,
        'balance': chart_balance,
    }

    return JsonResponse({
        'income': income,
        'expenses': expenses,
        'savings': savings,
        'chart_data': chart_data,
        'transactions': tx_list
    })

# Function to delete all data for the logged-in user
@login_required
def delete_all_data(request):
    if request.method == 'POST':
        # Perform data deletion
        Transaction.objects.filter(user=request.user).delete()  # Delete all transactions
        Budget.objects.filter(user=request.user).delete()  # Delete all budgets
        Notification.objects.filter(user=request.user).delete()  # Delete all notifications
        Saving.objects.filter(user=request.user).delete()  # Delete all savings records
        UserCategory.objects.filter(user=request.user).delete()  # Delete all user categories
        messages.success(request, 'Your data has been deleted successfully.')
        return redirect('settings')  # Redirect to the settings page after deletion

    return render(request, 'settings.html')