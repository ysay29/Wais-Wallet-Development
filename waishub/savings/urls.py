from django.urls import path
from .views import savings_summary, add_savings, budget_view, delete_goal

urlpatterns = [
    path('savings/', savings_summary, name='savings'),
    path('add-savings/', add_savings, name='add_savings_goal'),
    path('budgets/', budget_view, name='budget'),
    path('delete-goal/<int:id>/', delete_goal, name='delete_goal'),
]