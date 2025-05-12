from django.urls import path
from .views import analytics  # Import the analytics view
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics, name='analytics'),
    path('data/', views.analytics_data, name='analytics_data'),
]