from django.urls import path
from .views import index, logout_user, notifications_view, settings_view, mark_notification_read, add_expense

urlpatterns = [
    path('dashboard/', index, name='dashboard'),  # dashboard/index
    path('logout/', logout_user, name='logout'), #logout from dashboard
    path('notifications/', notifications_view, name='notifications'), #notifications page
    path('settings/', settings_view, name='settings'), #settings page
    path('mark-notification-read/', mark_notification_read, name='mark_notification_read'), #notifications page
    path('add-expense/', add_expense, name='add_expense'), #manage budget page
]
