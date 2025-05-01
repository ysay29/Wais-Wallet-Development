from django.shortcuts import render
from .models import Transaction
from django.utils import timezone

def transactions_view(request):
    # Get the current month 
    current_month = timezone.now().strftime('%B %Y')

    if request.method == 'POST':
        t   = request.POST.get('type')
        cat = request.POST.get('category')
        amt = request.POST.get('amount')
        dt  = request.POST.get('date')

        # Save the transaction with the current month
        Transaction.objects.create(type=t, category=cat, amount=amt, date=dt, month=current_month)
        return redirect('transactions')  # Reload the page

    # Get all transactions for the current month
    transactions = Transaction.objects.filter(month=current_month)

    return render(request, 'TransactionsList/transactions.html', {'transactions': transactions, 'current_month': current_month})

