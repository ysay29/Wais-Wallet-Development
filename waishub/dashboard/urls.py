from django.urls import path
from .views import index, logout_user
from authentication.views import logout_user
from . import views

urlpatterns = [
    path('dashboard/', index, name='dashboard'),  # dashboard/index
    path('logout/', logout_user, name='logout'), #logout from dashboard
]
