from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Transaction.models import Transaction
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
import json
from django.http import JsonResponse
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MonthlyFinance


@login_required
def analytics(request):
    """
    View to render the analytics dashboard with real-time data aggregated from the Transaction model.
    """
    try:
        # Fetch all transactions for the logged-in user
        transactions = Transaction.objects.filter(user=request.user)

        # Debugging: Check if transactions are being fetched
        print(f"Transactions for user {request.user}: {transactions}")

        # Check if there are any transactions
        if not transactions.exists():
            print("No transactions found for the user.")
            return render(request, 'analytics.html', {'message': "No transaction data available."})

        # Group and aggregate by month
        spend_data = transactions.annotate(
            month=TruncMonth('date')  # Group by month
        ).values('month').annotate(
            total_income=Sum('amount', filter=Q(type__iexact='income')),  # Case-insensitive match
            total_expenses=Sum('amount', filter=Q(type__iexact='expense')),  # Case-insensitive match
        ).order_by('month')

        # Debugging: Check the aggregated data
        print(f"Aggregated Spend Data: {list(spend_data)}")

        # Extract data for the dashboard
        months, income, expenses, balance = [], [], [], []

        for entry in spend_data:
            month = entry['month']
            total_income_val = entry['total_income'] or 0
            total_expenses_val = entry['total_expenses'] or 0

            # Debugging: Check each entry
            print(f"Month: {month}, Income: {total_income_val}, Expenses: {total_expenses_val}")

            months.append(month.strftime('%B %Y'))
            income.append(float(total_income_val))  # Ensure float conversion
            expenses.append(float(total_expenses_val))  # Ensure float conversion
            balance.append(float(total_income_val) - float(total_expenses_val))  # Calculate balance

        # Calculate totals for income and expenses
        total_income_sum = sum(income)
        total_expenses_sum = sum(expenses)

        # Debugging: Check extracted data
        print(f"Months: {months}")
        print(f"Income: {income}")
        print(f"Expenses: {expenses}")
        print(f"Balance: {balance}")
        print(f"Total Income: {total_income_sum}")
        print(f"Total Expenses: {total_expenses_sum}")

        # Prepare context for the template
        context = {
            'months': json.dumps(months),
            'income': json.dumps(income),
            'expenses': json.dumps(expenses),
            'balance': json.dumps(balance),
            'total_income': total_income_sum,
            'total_expenses': total_expenses_sum,
            'has_data': bool(months),  # Used to conditionally render charts
        }

        # Render the analytics dashboard template
        return render(request, 'analytics.html', context)

    except Exception as e:
        # Debugging: Catch and print any errors
        print(f"[Analytics View Error] {e}")
        return render(request, 'analytics.html', {'message': "An error occurred while processing the data."})

#UPDATE MONTHLY FINANCE
@receiver(post_save, sender=Transaction) 
def update_monthly_finance(sender, instance, **kwargs):
    # Ensure the monthly finance record exists for the month
    finance, created = MonthlyFinance.objects.get_or_create(
        user=instance.user,
        month=instance.date.replace(day=1)
    )
    finance.update_finance()

#ANALYTIC ON DASHBOARD
from django.shortcuts import render
from django.http import JsonResponse
from .models import MonthlyFinance
from datetime import date
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

@login_required
def analytics_data(request):
    # Get current user's finances for the current year and month
    user = request.user
    current_month = date.today().month
    current_year = date.today().year

    # Get monthly finance data
    monthly_finances = MonthlyFinance.objects.filter(user=user, month__year=current_year)

    # Prepare data for chart
    labels = []
    income_data = []
    expense_data = []
    balance_data = []

    for finance in monthly_finances:
        labels.append(finance.month.strftime('%B'))
        income_data.append(float(finance.income))
        expense_data.append(float(finance.expenses))
        balance_data.append(float(finance.balance))

    # Prepare the summary (income, expenses, savings)
    total_income = sum(income_data)
    total_expenses = sum(expense_data)
    savings = total_income - total_expenses

    # Prepare chart data in a structured way
    chart_data = {
        "labels": labels,
        "income": income_data,
        "expenses": expense_data,
        "balance": balance_data
    }

    # Prepare the context to pass to the front-end
    context = {
        'months': labels,            # Monthly labels
        'income': total_income,      # Total income
        'expenses': total_expenses,  # Total expenses
        'savings': savings,          # Total savings
        'chart_data': chart_data,    # Data to update the chart
    }

    # If an AJAX request (fetch request), return JSON data
    if request.is_ajax():
        return JsonResponse(context)

    # Regular GET request, render the page
    return render(request, 'dashboard/index.html', context)
