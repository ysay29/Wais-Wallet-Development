from django.shortcuts import render
from Transaction.models import Transaction
from django.db.models import Sum

def total_income(request):
    # Fetch only the income transactions
    incomes = Transaction.objects.filter(type='income').order_by('-date')
    # Sum their amounts
    total = incomes.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    return render(request, 'totalincome/totalincome.html', {
        'incomes': incomes,
        'total': total,
    })
