from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, ("Successfuly Logged In"))
            return redirect('dashboard')  # Use name='dashboard'
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    return render(request, 'login.html', {})


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already taken!")
            return redirect('/register/')

        user = User.objects.create_user(email=email, username=username)
        user.set_password(password)
        user.save()

        messages.info(request, "Account created successfully!")
        login(request, user)  # Auto-login after sign-up
        return redirect('/')  # safer than just 'dashboard'
    return render(request, 'signup.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("Successfuly Logged Out!"))
    return redirect('login')