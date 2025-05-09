from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction
from django.utils import timezone


@login_required
def add_transaction(request):
    if request.method == 'POST':
        t = request.POST.get('type')
        cat = request.POST.get('category')
        amt = request.POST.get('amount')
        dt = request.POST.get('date')

        if t and cat and amt and dt:
            Transaction.objects.create(user=request.user, type=t, category=cat, amount=amt, date=dt)
            return redirect(f"{reverse('add_transaction')}?saved=1")
        

    return render(request, 'add.html')

@login_required
def transactions_list(request):
    selected_month = request.GET.get('month', 'All')
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    if selected_month and selected_month != "All":
        try:
            month_number = timezone.datetime.strptime(selected_month, "%B").month
            transactions = transactions.filter(date__month=month_number)
        except ValueError:
            pass  # Invalid month name, skip filtering

    months = [
        "All", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    return render(request, 'transactions.html', {
        'transactions': transactions,
        'selected_month': selected_month,
        'months': months,
    })

@login_required
def total_income(request):
    incomes = Transaction.objects.filter(type='income')
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    
    category_totals_qs = incomes.values('category').annotate(total=Sum('amount'))
    category_totals = {entry['category']: entry['total'] for entry in category_totals_qs}

    return render(request, 'totalincome.html', {
        'incomes': incomes,
        'total_income': total_income,
        'category_totals': category_totals,})

@login_required
def total_expenses(request):
    expenses = Transaction.objects.filter(type='expense')
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    category_totals_qs = expenses.values('category').annotate(total=Sum('amount'))
    category_totals = {entry['category']: entry['total'] for entry in category_totals_qs}

    return render(request, 'totalexpenses.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'category_totals': category_totals,
    })
