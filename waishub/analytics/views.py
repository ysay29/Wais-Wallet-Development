from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Transaction.models import Transaction
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
import json

@login_required
def analytics(request):
    """
    View to render the analytics dashboard with real-time data aggregated from the Transaction model.
    """
    try:
        transactions = Transaction.objects.filter(user=request.user)

        print(f"Transactions for user {request.user}: {transactions}")

        if not transactions.exists():
            print("No transactions found for the user.")
            return render(request, 'analytics.html', {'message': "No transaction data available."})

        # Group and aggregate by month
        spend_data = transactions.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total_income=Sum('amount', filter=Q(type='income')),
            total_expenses=Sum('amount', filter=Q(type='expense')),
        ).order_by('month')

        print(f"Spend data: {list(spend_data)}")

        months, income, expenses, balance = [], [], [], []

        for entry in spend_data:
            month = entry['month']
            total_income_val = entry['total_income'] or 0
            total_expenses_val = entry['total_expenses'] or 0

            print(f"Month: {month}, Income: {total_income_val}, Expenses: {total_expenses_val}")

            months.append(month.strftime('%B %Y'))
            income.append(total_income_val)
            expenses.append(total_expenses_val)
            balance.append(total_income_val - total_expenses_val)

        total_income_sum = sum(income)
        total_expenses_sum = sum(expenses)

        print(f"Months: {months}")
        print(f"Income: {income}")
        print(f"Expenses: {expenses}")
        print(f"Balance: {balance}")
        print(f"Total Income: {total_income_sum}")
        print(f"Total Expenses: {total_expenses_sum}")

        context = {
            'months': json.dumps(months),
            'income': json.dumps(income),
            'expenses': json.dumps(expenses),
            'balance': json.dumps(balance),
            'total_income': total_income_sum,
            'total_expenses': total_expenses_sum,
            'has_data': bool(months),  # <-- Add this if you're conditionally rendering charts
        }

        return render(request, 'analytics.html', context)

    except Exception as e:
        print(f"[Analytics View Error] {e}")
        return render(request, 'analytics.html', {'message': "An error occurred while processing the data."})
