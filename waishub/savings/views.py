from django.shortcuts import render, redirect, get_object_or_404
from .models import Saving
from django.utils.timezone import now
from collections import defaultdict
from decimal import Decimal
import json
from .models import SavingsGoal
from django.contrib.auth.decorators import login_required
from .forms import SavingsGoalForm, SavingForm

@login_required
def savings_summary(request):
    selected_goal_id = request.GET.get('goal')
    goals = SavingsGoal.objects.filter(user=request.user)

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