from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth import logout
from .models import Notification
from django.utils import timezone

#@login_required
def index(request):
    return render(request, 'index.html')  # Your dashboard template

def logout_user(request):
    logout(request)
    return redirect('login') 

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def index(request):
    return render(request, 'index.html') #Not logged in, redirect to login page


def notifications_view(request):
    user = request.user
    today = timezone.localtime().date()

    notifications = Notification.objects.filter(user=user).order_by('-timestamp')
    today_notifications = notifications.filter(timestamp__date=today)
    older_notifications = notifications.exclude(timestamp__date=today)
    unread_count = notifications.filter(read=False).count()

    context = {
        'today_notifications': today_notifications,
        'older_notifications': older_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications.html', context) # Your notifications template