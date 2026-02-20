"""
Admin interface configuration for tasks app.
"""
from django.contrib import admin
from .models import Task, Course, OAuthToken, NotificationPreference


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'user', 'is_core', 'created_at']
    list_filter = ['is_core', 'created_at']
    search_fields = ['name', 'code', 'user__username']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'quadrant', 'deadline',
        'urgency_score', 'importance_score', 'is_completed', 'is_deleted'
    ]
    list_filter = [
        'quadrant', 'is_completed', 'is_deleted',
        'is_manually_categorized', 'user_priority'
    ]
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OAuthToken)
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_expiry', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_enabled', 'push_enabled', 'in_app_enabled',
        'work_start_hour', 'work_end_hour'
    ]
    list_filter = ['email_enabled', 'push_enabled', 'in_app_enabled']
