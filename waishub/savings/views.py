from django.shortcuts import render
from .models import Saving
from django.db.models import Sum
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

@login_required
def savings_summary(request):
    savings = Saving.objects.all().order_by('-date')
    total = savings.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    # Get the most recent saving goal settings
    last_saving = savings.first()
    monthly_goal = last_saving.goal_amount if last_saving and last_saving.goal_amount else 1  # avoid divide by zero
    goal_term = last_saving.goal_term if last_saving else ''
    reminder_frequency = last_saving.reminder_frequency if last_saving else ''

    progress_percentage = min((total / monthly_goal) * 100, 100)

    context = {
        'savings': savings,
        'total': total,
        'current_month': now().strftime('%B %Y'),
        'progress_percentage': progress_percentage,
        'monthly_goal': monthly_goal,
        'goal_term': goal_term,
        'reminder_frequency': reminder_frequency,
    }
    return render(request, 'savings.html', context)

def add_savings(request):
    pass
