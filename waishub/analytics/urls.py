from django.urls import path
from . import views


urlpatterns = [
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/data/', views.analytics_data, name='analytics_data'),
]