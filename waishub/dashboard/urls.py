from django.urls import path
from .views import index, logout_view
from . import views

urlpatterns = [
    path('', views.index, name='dashboard'),  # dashboard/index
    path('logout/', logout_view, name='logout'),
]
