from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction, UserCategory
from django.utils import timezone
from decimal import Decimal
from datetime import datetime

@login_required
def add_transaction(request):
    # Get the user's categories for the dropdown or selection
    categories = UserCategory.objects.filter(user=request.user)

    if request.method == 'POST':
        t = request.POST.get('type')  # 'income' or 'expense'
        cat = request.POST.get('category')  # Category name
        amt = request.POST.get('amount')  # Transaction amount
        dt = request.POST.get('date')  # Transaction date

        # Ensure all necessary fields are provided
        if t and cat and amt and dt:
            try:
                # Convert the date string to a datetime object
                dt = datetime.strptime(dt, '%Y-%m-%d')  # Assuming format is 'YYYY-MM-DD'
            except ValueError:
                # Handle invalid date format (you can log it or return a custom error message)
                dt = None
            
            if dt:
                # Check if the category exists for the current user, if not, create it
                if not UserCategory.objects.filter(user=request.user, category_name=cat).exists():
                    UserCategory.objects.create(user=request.user, category_name=cat)

                # Convert the amount to Decimal before saving
                amt = Decimal(amt)

                # Create the transaction in the database
                Transaction.objects.create(user=request.user, type=t, category=cat, amount=amt, date=dt)

                # Redirect with a "saved" query parameter
                return redirect(f"{reverse('add_transaction')}?saved=1")
            else:
                # Handle invalid date format (optional: add a message to the user)
                pass

    return render(request, 'add.html', {'categories': categories})

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
    # Filter transactions by 'income' type and get the total amount
    incomes = Transaction.objects.filter(user=request.user, type='Income')
    
    # Sum the amounts from the filtered incomes
    total_income = sum(income.amount for income in incomes)

    # Calculate category-wise totals for income
    category_totals_qs = incomes.values('category').annotate(total=Sum('amount'))
    category_totals = {entry['category']: entry['total'] for entry in category_totals_qs}

    return render(request, 'totalincome.html', {
        'incomes': incomes,
        'total_income': total_income,  # Using the calculated total_income
        'category_totals': category_totals,
    })

@login_required
def total_expenses(request):
    expenses = Transaction.objects.filter(user=request.user, type='Expense')
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Format the total expenses for display
    formatted_total_expenses = f"₱{total_expenses:,.2f}"

    category_totals_qs = expenses.values('category').annotate(total=Sum('amount'))
    category_totals = {entry['category']: entry['total'] for entry in category_totals_qs}

    return render(request, 'totalexpenses.html', {
        'expenses': expenses,
        'total_expenses': formatted_total_expenses,  # Passing formatted total expense
        'category_totals': category_totals,
    })

