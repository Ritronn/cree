"""
Admin interface configuration for tasks app.
"""
from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'user', 'quadrant', 'deadline',
        'urgency_score', 'importance_score', 'is_completed'
    ]
    list_filter = [
        'quadrant', 'is_completed', 'is_manually_categorized'
    ]
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'urgency_score', 'importance_score', 'quadrant']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Scheduling', {
            'fields': ('deadline', 'estimated_time_hours')
        }),
        ('Categorization', {
            'fields': ('urgency_score', 'importance_score', 'quadrant', 'is_manually_categorized')
        }),
        ('Status', {
            'fields': ('is_completed',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
