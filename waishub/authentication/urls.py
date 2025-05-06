from django.urls import path
from . import views
from .views import login_view, register

urlpatterns = [
    path('', login_view, name='login'),
    path('', register, name='register'),
]
