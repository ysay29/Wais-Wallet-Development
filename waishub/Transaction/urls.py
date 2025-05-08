from django.urls import path
from .views import add_transaction, transactions_list

urlpatterns = [
    path('', add_transaction, name='add_transaction'),
    path('', transactions_list, name='transactions_list'),
]
