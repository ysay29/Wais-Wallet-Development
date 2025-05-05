from django.urls import path
from .views import savings_summary

urlpatterns = [
    path('', savings_summary, name='savings'),
]