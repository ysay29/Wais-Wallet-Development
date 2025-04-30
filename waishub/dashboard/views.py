#   PENDING
from django.shortcuts import render

def dashboard_home(request):
    return render(request, 'dashboard/home.html')

def transactions_page(request):
    return render(request, 'dashboard/transactions.html')

def analytics_page(request):
    return render(request, 'dashboard/analytics.html')

def total_income_page(request):
    return render(request, 'dashboard/income.html')

def total_expenses_page(request):
    return render(request, 'dashboard/expenses.html')

def savings_page(request):
    return render(request, 'dashboard/savings.html')

def budgets_page(request):
    return render(request, 'dashboard/budgets.html')

def settings_page(request):
    return render(request, 'dashboard/settings.html')

def about_page(request):
    return render(request, 'dashboard/about.html')
