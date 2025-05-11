from django.urls import path
from .views import analytics  # Import the analytics view

app_name = 'analytics'

urlpatterns = [
    path('analytics/', analytics, name='analytics'),  # Map the analytics view to the root URL
]