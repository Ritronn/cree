"""
API URLs for Authentication
Separate from main accounts URLs to avoid conflicts
"""
from django.urls import path
from .api_views import api_register, api_login, api_logout, api_current_user

urlpatterns = [
    path('register/', api_register, name='api_register'),
    path('login/', api_login, name='api_login'),
    path('logout/', api_logout, name='api_logout'),
    path('current-user/', api_current_user, name='api_current_user'),
]
