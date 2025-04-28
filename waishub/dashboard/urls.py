from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('transactions/', views.transactions_page, name='transactions'),
    path('analytics/', views.analytics_page, name='analytics'),
    path('income/', views.total_income_page, name='total_income'),
    path('expenses/', views.total_expenses_page, name='total_expenses'),
    path('savings/', views.savings_page, name='savings'),
    path('budgets/', views.budgets_page, name='budgets'),
    path('settings/', views.settings_page, name='settings'),
    path('about/', views.about_page, name='about'),
]
