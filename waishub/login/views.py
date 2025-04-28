from django.shortcuts import render, redirect
from .forms import LoginForm

def sign_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})
 

# Create your views here.
