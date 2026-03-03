"""
Simplified data models for the Eisenhower Matrix Task Management system.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Task(models.Model):
    """
    Represents a task in the Eisenhower Matrix system.
    """
    QUADRANT_CHOICES = [
        ('urgent_important', 'Urgent & Important'),
        ('important_not_urgent', 'Important but Not Urgent'),
        ('urgent_not_important', 'Urgent but Not Important'),
        ('neither', 'Neither Urgent nor Important'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    # UUID primary key to match the existing database schema
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    estimated_time_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.1)]
    )

    # Task attributes for categorization
    is_graded = models.BooleanField(default=False)
    is_exam_related = models.BooleanField(default=False)

    # Categorization
    urgency_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.0
    )
    importance_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.0
    )
    quadrant = models.CharField(
        max_length=50,
        choices=QUADRANT_CHOICES,
        default='neither'
    )
    is_manually_categorized = models.BooleanField(default=False)

    # Priority and scheduling
    user_priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    calendar_event_id = models.CharField(max_length=255, blank=True, null=True)
    scheduled_start = models.DateTimeField(blank=True, null=True)
    scheduled_end = models.DateTimeField(blank=True, null=True)

    # Status
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Course reference (nullable)
    course = models.ForeignKey(
        'Course', on_delete=models.SET_NULL,
        related_name='tasks', blank=True, null=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_deleted', 'is_completed']),
            models.Index(fields=['quadrant']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return self.title


class Course(models.Model):
    """
    Represents a course/subject for task organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    is_core = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = [('user', 'code')]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Flashcard(models.Model):
    """
    Represents a revision card (Que-Que Card) for a specific topic or task.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcards')
    task = models.ForeignKey(
        Task, on_delete=models.SET_NULL,
        related_name='flashcards', blank=True, null=True
    )
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL,
        related_name='flashcards', blank=True, null=True
    )
    topic = models.CharField(max_length=255)
    question = models.TextField()
    answer = models.TextField()
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.topic}: {self.question[:30]}..."
