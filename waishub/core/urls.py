from django.urls import path
from . import views

urlpatterns = [
    path('aboutus/', views.AboutUs, name='aboutus')
]