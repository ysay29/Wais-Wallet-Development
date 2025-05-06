from django.shortcuts import render
from Transaction.models import Transaction
from django.db.models import Sum

def total_expenses(request):
    expenses = Transaction.objects.filter(type='expense').order_by('-date')
    total = expenses.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    for exp in expenses:
        exp.formatted_date = exp.date.strftime('%Y-%m-%d')  # For chart labels
    return render(request, 'totalexpenses.html', {
        'expenses': expenses,
        'total': total,
    })