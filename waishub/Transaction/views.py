from django.shortcuts import render, redirect
from .models import Transaction

def add_transaction(request):
    if request.method == 'POST':
        t = request.POST.get('type')
        cat = request.POST.get('category')
        amt = request.POST.get('amount')
        dt = request.POST.get('date')

        Transaction.objects.create(
            type=t,
            category=cat,
            amount=amt,
            date=dt
        )
        return redirect('add_transaction')

    return render(request, 'Transaction/add.html')
