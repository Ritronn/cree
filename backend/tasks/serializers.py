"""
Serializers for the Task Management API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Course


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'is_core', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model with automatic categorization."""
    
    course_details = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'deadline', 'estimated_time_hours',
            'course', 'course_details', 'is_graded', 'is_exam_related',
            'urgency_score', 'importance_score', 'quadrant', 'is_manually_categorized',
            'user_priority', 'calendar_event_id', 'scheduled_start', 'scheduled_end',
            'is_completed', 'completed_at', 'is_deleted',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'urgency_score', 'importance_score', 'quadrant',
            'calendar_event_id', 'scheduled_start', 'scheduled_end',
            'completed_at', 'created_at', 'updated_at'
        ]
    
    def validate_title(self, value):
        """Validate that title is non-empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()
    
    def validate_deadline(self, value):
        """Validate that deadline is in the future."""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return value
    
    def validate_estimated_time_hours(self, value):
        """Validate estimated time is positive."""
        if value <= 0:
            raise serializers.ValidationError("Estimated time must be greater than 0.")
        return value
