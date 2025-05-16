from django.shortcuts import render, redirect, get_object_or_404
from .models import Saving
from django.utils.timezone import now
from collections import defaultdict
from decimal import Decimal
import json
from .models import SavingsGoal
from django.contrib.auth.decorators import login_required
from .forms import SavingsGoalForm, SavingForm
from django.urls import reverse

@login_required
def savings_summary(request):
    goals = SavingsGoal.objects.filter(user=request.user)

    # Handle POST: Add new saving
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        goal_id = request.POST.get('goal')

        try:
            goal = goals.get(id=goal_id)
        except SavingsGoal.DoesNotExist:
            goal = None

        if amount and date and goal:
            Saving.objects.create(
                user=request.user,
                amount=Decimal(amount),
                date=date,
                goal=goal
            )
            # Redirect to prevent re-submission on refresh
            return redirect('savings')  # Ensure 'savings' matches your URL name

    # Handle GET: Display savings summary
    selected_goal_id = request.GET.get('goal')
    if selected_goal_id:
        try:
            selected_goal = goals.get(id=selected_goal_id)
            savings = Saving.objects.filter(user=request.user, goal=selected_goal).order_by('-date')
        except SavingsGoal.DoesNotExist:
            selected_goal = None
            savings = Saving.objects.filter(user=request.user).order_by('-date')
    else:
        selected_goal = None
        savings = Saving.objects.filter(user=request.user).order_by('-date')

    total = sum(s.amount or Decimal('0') for s in savings)
    goal_amount = selected_goal.target_amount if selected_goal else Decimal('400000')
    progress = (total / goal_amount) * 100 if goal_amount else 0

    monthly_totals = defaultdict(Decimal)
    for s in savings:
        if s.date:
            month_label = s.date.strftime('%b %Y')
            monthly_totals[month_label] += s.amount

    context = {
        'goals': goals,
        'selected_goal': selected_goal,
        'savings': savings,
        'total_savings': total,
        'goal': goal_amount,
        'progress_percent': progress,
        'current_month': now(),
        'chart_labels': json.dumps(list(monthly_totals.keys())[::-1]),
        'chart_data': json.dumps([float(v) for v in monthly_totals.values()][::-1]),
    }

    return render(request, 'savings.html', context)


@login_required
def budget_view(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    return render(request, 'budgets.html', {'goals': goals})

@login_required
def add_savings(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            saving_goal = form.save(commit=False)
            saving_goal.user = request.user
            saving_goal.save()
            return redirect('budget')
    else:
        form = SavingsGoalForm()

    return render(request, 'addsavings.html', {'form': form})

@login_required
def delete_goal(request, id):
    goal = get_object_or_404(SavingsGoal, id=id)  # Get the goal by its ID
    goal.delete()  # Delete the goal
    return redirect('budget')  # Redirect to the budgets page