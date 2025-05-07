from django.urls import path
from .views import index, logout_view
from . import views

urlpatterns = [
    path('', index, name='dashboard'),  # dashboard/index
    path('logout/', logout_view, name='logout'),
]
