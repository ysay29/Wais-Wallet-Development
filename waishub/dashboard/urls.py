from django.urls import path
from .views import index, logout_user, notifications_view, settings_view
from . import views

urlpatterns = [
    path('dashboard/', index, name='dashboard'),  # dashboard/index
    path('logout/', logout_user, name='logout'), #logout from dashboard
    path('notifications/', notifications_view, name='notifications'), #notifications page
    path('settings/', settings_view, name='settings'), #settings page
]
