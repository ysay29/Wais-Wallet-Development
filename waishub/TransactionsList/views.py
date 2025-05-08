from django.shortcuts import render, redirect
from .models import Transaction
from django.utils import timezone

def add_transaction(request):
    if request.method == 'POST':
        t = request.POST.get('type')
        cat = request.POST.get('category')
        amt = request.POST.get('amount')
        dt = request.POST.get('date')
        month = timezone.datetime.strptime(dt, "%Y-%m-%d").strftime('%B %Y')

        Transaction.objects.create(
            type=t,
            category=cat,
            amount=amt,
            date=dt,
            month=month
        )
        return redirect('transactions')
    return render(request, 'TransactionsList/add.html')


def transactions_view(request):
    current_month = timezone.now().strftime('%B %Y')
    transactions = Transaction.objects.filter(month=current_month).order_by('-date')

    return render(request, 'TransactionsList/transactions.html', {
        'transactions': transactions,
        'current_month': current_month
    })
