from django.shortcuts import render
from Transaction.models import Transaction
from django.db.models import Sum

def total_expenses(request):
    # Fetch only the expense transactions
    expenses = Transaction.objects.filter(type='expense').order_by('-date')
    # Sum their amounts
    total = expenses.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    return render(request, 'totalexpenses/totalexpenses.html', {
        'expenses': expenses,
        'total': total,
    })
