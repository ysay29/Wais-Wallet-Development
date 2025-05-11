from django.shortcuts import render
from .models import MonthlySpending  # Import the MonthlySpending model


def analytics(request):
    """
    View to render the analytics dashboard with spending data.
    """
    # Fetch all MonthlySpending records for the logged-in user, ordered by ID
    spend_data = MonthlySpending.objects.filter(user=request.user).order_by('id')

    # Check if there is any spending data
    if not spend_data.exists():
        context = {
            'message': "No spending data available.",
        }
        return render(request, 'analytics.html', context)  # Reference the global template

    # Extract data for the dashboard
    months = [entry.month for entry in spend_data]
    income = [entry.income for entry in spend_data]
    expenses = [entry.expense for entry in spend_data]
    balance = [inc - exp for inc, exp in zip(income, expenses)]

    # Extract category-specific spending
    food = [entry.food for entry in spend_data]
    utilities = [entry.utilities for entry in spend_data]
    apparel = [entry.apparel for entry in spend_data]

    # Calculate totals for each category
    food_total = sum(food)
    utilities_total = sum(utilities)
    apparel_total = sum(apparel)

    # Prepare context for the template
    context = {
        'months': months,
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'food_total': food_total,
        'utilities_total': utilities_total,
        'apparel_total': apparel_total,
    }

    # Render the analytics dashboard template
    return render(request, 'analytics.html', context)  # Reference the global template