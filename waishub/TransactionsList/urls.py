from django.urls import path
from .views import transactions_view, add_transaction

urlpatterns = [
    path('', transactions_view, name='transactions'),
    path('add/', add_transaction, name='add_transaction'),
]
