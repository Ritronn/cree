"""
URL configuration for eisenhower_matrix project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """Root API endpoint with available routes."""
    return JsonResponse({
        'message': 'Eisenhower Matrix Task Management API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'tasks': '/api/tasks/ (coming soon)',
            'auth': '/api/auth/ (coming soon)',
        },
        'documentation': 'See README.md for setup instructions'
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('tasks.urls')),
]
