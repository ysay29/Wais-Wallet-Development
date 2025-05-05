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
            return redirect('/dashboard/')  # Redirect to your dashboard
        else:
            messages.error(request, "Invalid username or password")
            return redirect('/login/')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already taken!")
            return redirect('/register/')
        
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        messages.info(request, "Account created successfully!")
        return redirect('/login/')
    
    return render(request, 'signup.html')


def logout_view(request):
    django_logout(request)
    return redirect('/login/')
