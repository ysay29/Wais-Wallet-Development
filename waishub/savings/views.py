from django.shortcuts import render, redirect
from .models import Saving
from django.utils.timezone import now
from collections import defaultdict
from decimal import Decimal
import json

def savings_summary(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        amount = request.POST.get('amount')

        # Validate the inputs
        if date and amount:
            try:
                # Convert amount to Decimal and save the instance
                amount = Decimal(amount)
                Saving.objects.create(date=date, amount=amount)
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
    total = sum(s.amount for s in savings if s.amount)  # Ensure `amount` is not None
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
<<<<<<< HEAD
    chart_data = [float(v) for v in monthly_totals.values()][::-1] 
    
=======
    chart_data = [float(value) for value in monthly_totals.values()][::-1]  # Convert Decimal to float

>>>>>>> 7aa97bd36cd60875df314a07c4b3dac58b90d201
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