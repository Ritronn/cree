"""
Serializers for the Task Management API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Flashcard, Course


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'is_core', 'created_at']
        read_only_fields = ['id', 'created_at']


class FlashcardSerializer(serializers.ModelSerializer):
    """Serializer for Flashcard (Que-Que Card) model."""
    class Meta:
        model = Flashcard
        fields = [
            'id', 'topic', 'question', 'answer', 'is_favorite', 
            'created_at', 'task', 'course'
        ]
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model with automatic categorization."""
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'deadline', 'estimated_time_hours',
            'is_graded', 'is_exam_related', 'user_priority',
            'urgency_score', 'importance_score', 'quadrant', 'is_manually_categorized',
            'is_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'urgency_score', 'importance_score', 'quadrant',
            'created_at', 'updated_at'
        ]
    
    def validate_title(self, value):
        """Validate that title is non-empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()
    
    def validate_estimated_time_hours(self, value):
        """Validate estimated time is positive."""
        if value <= 0:
            raise serializers.ValidationError("Estimated time must be greater than 0.")
        return value
