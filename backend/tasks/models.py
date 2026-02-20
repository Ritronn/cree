"""
Simplified data models for the Eisenhower Matrix Task Management system.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


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

    # Using AutoField (integer) instead of UUID for simplicity
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    estimated_time_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.1)]
    )

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

    # Status
    is_completed = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['quadrant']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return self.title
