from django.shortcuts import render, redirect

 
def AboutUs(request):
    return render(request, 'aboutus.html', {})
