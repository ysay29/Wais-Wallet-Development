from django.urls import path
from . import views
from .views import login_view, register, auth_logout

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', auth_logout, name='logout')
]
