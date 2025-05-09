from django.shortcuts import render, redirect

 
def AboutUs(request):
    return render(request, 'aboutus.html', {})

def landing(request):
    return render(request, 'landing.html', {})

def settings(request):
    return render(request, 'settings.html', {})