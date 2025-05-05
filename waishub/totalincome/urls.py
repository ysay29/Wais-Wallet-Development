from django.urls import path
from .views import total_income

urlpatterns = [
    path('', total_income, name='totalincome'),
]