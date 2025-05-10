from django.urls import path
from .views import savings_summary, add_savings, budget_view

urlpatterns = [
    path('', savings_summary, name='savings'),
    path('add/', add_savings, name='add_savings_goal'),
    path('budgets/', budget_view, name='budget'),
]