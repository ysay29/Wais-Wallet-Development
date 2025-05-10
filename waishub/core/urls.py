from django.urls import path
from . import views

urlpatterns = [
    path('aboutus/', views.AboutUs, name='aboutus'),
    path('', views.landing, name='landingpage'),
    path('settings/', views.settings, name='settings'),
    path('add_savings/', views.add_savings, name='addsavings')
]