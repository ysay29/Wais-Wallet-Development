from django.urls import path
from .views import total_expenses

urlpatterns = [
    path('', total_expenses, name='totalexpenses'),
]