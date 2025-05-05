from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout as django_logout

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')  # Use name='dashboard'
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        ...
        user = User.objects.create_user(...)
        messages.info(request, "Account created successfully!")
        auth_login(request, user)  # Auto-login after sign-up
        return redirect('dashboard')

    return render(request, 'signup.html')
