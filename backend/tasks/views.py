"""
API views for Task Management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Task
from .serializers import TaskSerializer
from .categorization import categorize_task


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations with automatic categorization.
    
    Endpoints:
    - POST /api/tasks/ - Create task
    - GET /api/tasks/ - List tasks (with filters)
    - GET /api/tasks/{id}/ - Get single task
    - PUT /api/tasks/{id}/ - Update task
    - PATCH /api/tasks/{id}/ - Partial update
    - DELETE /api/tasks/{id}/ - Soft delete
    """
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]  # Disabled auth for hackathon demo
    
    def get_queryset(self):
        """Return all non-deleted tasks (no user filter for demo)."""
        queryset = Task.objects.filter(
            is_deleted=False
        ).select_related('course')
        
        # Apply filters from query parameters
        quadrant = self.request.query_params.get('quadrant')
        if quadrant:
            queryset = queryset.filter(quadrant=quadrant)
        
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        is_completed = self.request.query_params.get('is_completed')
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Create task and trigger automatic categorization."""
        # Get or create a demo user
        demo_user, _ = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@example.com'}
        )
        
        # Save task with demo user
        task = serializer.save(user=demo_user)
        
        # Trigger categorization
        categorization = categorize_task(task)
        if categorization:
            task.urgency_score = categorization['urgency_score']
            task.importance_score = categorization['importance_score']
            task.quadrant = categorization['quadrant']
            task.save()
    
    def perform_update(self, serializer):
        """Update task and recategorize if not manually categorized."""
        task = serializer.save()
        
        # Recategorize if not manually categorized
        if not task.is_manually_categorized:
            categorization = categorize_task(task)
            if categorization:
                task.urgency_score = categorization['urgency_score']
                task.importance_score = categorization['importance_score']
                task.quadrant = categorization['quadrant']
                task.save()
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete task and remove calendar event."""
        task = self.get_object()
        
        # Soft delete
        task.is_deleted = True
        task.calendar_event_id = None
        task.scheduled_start = None
        task.scheduled_end = None
        task.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
