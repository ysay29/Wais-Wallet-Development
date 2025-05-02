"""
URL configuration for waishub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
<<<<<<< Updated upstream
    path('admin/', admin.site.urls), 
=======
    path("admin/", admin.site.urls),          # Admin interface
    path('login/', login, name='login.html'),    # Login page
    path('register/', register, name='register'),  # Registration page
    path('logout/', logout, name='logout'),  # Registration page
    path('dashboard/', include('dashboard.urls')), #Dashboard page
    path('add/', include('Transaction.urls')), #Add transaction page
    path('transactions/', include('TransactionsList.urls')), #Transactions list page
    path('totalincome/',  include('totalincome.urls')), #Total income page
    path('totalexpenses/', include('totalexpenses.urls')), #Total expenses page
>>>>>>> Stashed changes
]
