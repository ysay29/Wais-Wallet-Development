from django.urls import path
from .views import add_transaction, transactions_list, total_income, total_expenses

urlpatterns = [
    path('add/', add_transaction, name='add_transaction'),
    path('transactions/', transactions_list, name='transactions'),
    path('income/', total_income, name='totalincome'),
    path('expenses/', total_expenses, name='totalexpenses'),
]
