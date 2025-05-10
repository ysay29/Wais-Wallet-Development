from django.shortcuts import render, redirect, get_object_or_404
from .models import Saving
from django.utils.timezone import now
from collections import defaultdict
from decimal import Decimal
import json
from .models import SavingsGoal
from django.contrib.auth.decorators import login_required
from .forms import SavingsGoalForm

@login_required
def savings_summary(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        amount = request.POST.get('amount')

        # Validate the inputs
        if date and amount:
            try:
                # Convert amount to Decimal and save the instance
                amount = Decimal(amount)
                Saving.objects.create(user=request.user, date=date, amount=amount)
            except (ValueError, TypeError, Decimal.InvalidOperation):
                # Handle invalid amount input
                return render(request, 'savings.html', {
                    'error': 'Invalid amount. Please enter a valid number.'
                })
        else:
            # Handle missing fields
            return render(request, 'savings.html', {
                'error': 'Both date and amount are required.'
            })

        return redirect('savings')  # Ensure the URL name matches your urlpatterns

    # Fetch all savings and calculate totals
    savings = Saving.objects.all().order_by('-date')
    total = sum(s.amount or Decimal('0') for s in savings)# Ensure `amount` is not None
    goal = Decimal('400000')  # Use Decimal for goal
    progress = (total / goal) * 100 if goal else 0

    # Group savings by month for chart
    monthly_totals = defaultdict(Decimal)
    for s in savings:
        if s.date:  # Ensure date is not None
            month_label = s.date.strftime('%b %Y')  # Example: 'May 2025'
            monthly_totals[month_label] += s.amount

    # Convert Decimal values to float for JSON serialization
    chart_labels = list(monthly_totals.keys())[::-1]  # Reverse for chronological order
    chart_data = [float(value) for value in monthly_totals.values()][::-1]  # Convert Decimal to float

    context = {
        'savings': savings,
        'total_savings': total,
        'goal': goal,
        'progress_percent': progress,
        'current_month': now(),
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'savings.html', context)

@login_required
def budget_view(request):
    goals = SavingsGoal.objects.all()
    return render(request, 'budgets.html', {'goals': goals})

@login_required
def add_savings(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('budget')  # Redirect to 'budget', not 'budget_view'
    else:
        form = SavingsGoalForm()
    return render(request, 'addsavings.html', {'form': form})

@login_required
def delete_goal(request, id):
    goal = get_object_or_404(SavingsGoal, id=id)  # Get the goal by its ID
    goal.delete()  # Delete the goal
    return redirect('budget')  # Redirect to the budgets page