from django.shortcuts import render, redirect
from .models import Saving
from django.utils.timezone import now
from collections import defaultdict
import json

def savings_summary(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        amount = request.POST.get('amount')
        if date and amount:
            Saving.objects.create(date=date, amount=amount)
        return redirect('savings:savings_summary')  

    savings = Saving.objects.all().order_by('-date')
    total = sum(s.amount for s in savings)
    goal = 400000
    progress = (total / goal) * 100 if goal else 0

    # Group savings by month for chart
    monthly_totals = defaultdict(int)
    for s in savings:
        month_label = s.date.strftime('%b %Y')  # Example: 'May 2025'
        monthly_totals[month_label] += s.amount

    chart_labels = list(monthly_totals.keys())[::-1]  # Reverse for chronological order
    chart_data = list(monthly_totals.values())[::-1]

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
