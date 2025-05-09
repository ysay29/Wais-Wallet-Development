from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

@login_required
def add_transaction(request):
    if request.method == 'POST':
        t = request.POST.get('type')
        cat = request.POST.get('category')
        amt = request.POST.get('amount')
        dt = request.POST.get('date')

        if t and cat and amt and dt:
            Transaction.objects.create(type=t, category=cat, amount=amt, date=dt)
            return redirect(f"{reverse('add_transaction')}?saved=1")

    return render(request, 'add.html')

def transactions_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    
<<<<<<< HEAD
    return render(request, 'Transaction/transactions.html', {'transactions': transactions})

def total_income(request):
    incomes = Transaction.objects.filter(transaction_type='income')
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    
    category_totals_qs = incomes.values('category').annotate(total=Sum('amount'))
    category_totals = {entry['category']: entry['total'] for entry in category_totals_qs}

    return render(request, 'totalincome.html', {
        'incomes': incomes,
        'total_income': total_income,
        'category_totals': category_totals,})

def total_expenses(request):
    expenses = Transaction.objects.filter(type='expense').order_by('-date')
    total = expenses.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    for exp in expenses:
        exp.formatted_date = exp.date.strftime('%Y-%m-%d')  # For chart labels
    return render(request, 'totalexpenses.html', {
        'expenses': expenses,
        'total': total,
    })
=======
    return render(request, 'transactions.html', {'transactions': transactions})
>>>>>>> 614be3a2bbb5344e6c3a651ecc460d5c6f477fd0
