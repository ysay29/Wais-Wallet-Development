from django.urls import path
from .views import transactions_view

urlpatterns = [
    path('', total_income, name='totalincome'),
]
