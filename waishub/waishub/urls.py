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
# Import necessary modules
from django.contrib import admin  # Django admin module
from django.urls import path, include      # URL routing
from authentication.views import *  # Import views from the authentication app
from django.conf.urls.static import static
from django.conf import settings   # Application settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # Static files serving
from Transaction import views

# Define URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),         # Admin interface
    path('', login, name='login.html'),    # Login page
    path('register/', register, name='register'),  # Registration page
    path('logout/', logout, name='logout'),  # Registration page
    path('dashboard/', include('dashboard.urls')), #Dashboard page
    path('add/', include('Transaction.urls')), #Add Transaction page
]

# Serve media files if DEBUG is True (development mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files using staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
