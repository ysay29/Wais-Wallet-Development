from django.shortcuts import render, redirect
from .models import Transaction
from django.utils import timezone

def transactions_view(request):
    current_month = timezone.now().strftime('%B %Y')

    if request.method == 'POST':
        t   = request.POST.get('type')
        cat = request.POST.get('category')
        amt = request.POST.get('amount')
        dt  = request.POST.get('date')

        Transaction.objects.create(type=t, category=cat, amount=amt, date=dt, month=current_month)
        return redirect('transactions')

    transactions = Transaction.objects.filter(month=current_month)

    return render(request, 'TransactionsList/transactions.html', {
        'transactions': transactions,
        'current_month': current_month
    })
