from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Transaction

def add_transaction(request):
    if request.method == 'POST':
        t = request.POST.get('type')
        cat = request.POST.get('category')
        amt = request.POST.get('amount')
        dt = request.POST.get('date')

        if t and cat and amt and dt:
            Transaction.objects.create(type=t, category=cat, amount=amt, date=dt)
            return redirect(f"{reverse('add_transaction')}?saved=1")

    return render(request, 'Transaction/add.html')
