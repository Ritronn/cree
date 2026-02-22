from django.contrib import admin
from .models import (
    Topic, Content, Assessment, Question, UserAnswer,
    UserProgress, MonitoringSession, ConceptMastery, RevisionQueue,
    StudySession, ProctoringEvent, GeneratedTest, TestQuestion,
    TestSubmission, WhiteboardSnapshot, SessionMetrics
)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'current_difficulty', 'mastery_level', 'sessions_completed', 'created_at']
    list_filter = ['current_difficulty', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'content_type', 'processed', 'created_at']
    list_filter = ['content_type', 'processed', 'created_at']
    search_fields = ['title', 'topic__name']
    readonly_fields = ['created_at']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'difficulty_level', 'score', 'adaptive_score', 'is_completed', 'started_at']
    list_filter = ['difficulty_level', 'is_completed', 'started_at']
    search_fields = ['user__username', 'content__title']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'order', 'concept', 'difficulty', 'question_text_short']
    list_filter = ['difficulty', 'concept']
    search_fields = ['question_text', 'concept']
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'is_correct', 'time_taken_seconds', 'attempt_number', 'answered_at']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['user__username']
    readonly_fields = ['answered_at']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'current_difficulty', 'mastery_level', 'average_accuracy', 'total_assessments']
    list_filter = ['current_difficulty', 'updated_at']
    search_fields = ['user__username', 'topic__name']
    readonly_fields = ['updated_at']


@admin.register(MonitoringSession)
class MonitoringSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'total_time_seconds', 'tab_switches', 'focus_lost_count', 'started_at']
    list_filter = ['started_at']
    search_fields = ['user__username', 'content__title']
    readonly_fields = ['started_at', 'ended_at']


@admin.register(ConceptMastery)
class ConceptMasteryAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'concept_name', 'accuracy', 'mastery_level', 'total_questions']
    list_filter = ['mastery_level', 'updated_at']
    search_fields = ['user__username', 'concept_name', 'topic__name']
    readonly_fields = ['updated_at']


@admin.register(RevisionQueue)
class RevisionQueueAdmin(admin.ModelAdmin):
    list_display = ['user', 'concept', 'scheduled_for', 'priority', 'times_reviewed', 'completed']
    list_filter = ['completed', 'scheduled_for', 'priority']
    search_fields = ['user__username', 'concept__concept_name']
    readonly_fields = ['created_at']


# ============================================================================
# STUDY SESSION MONITORING AND TESTING ADMIN
# ============================================================================

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_type', 'content', 'is_active', 'is_completed', 'camera_enabled', 'started_at']
    list_filter = ['session_type', 'is_active', 'is_completed', 'camera_enabled', 'started_at']
    search_fields = ['user__username', 'content__title']
    readonly_fields = ['started_at', 'ended_at']


@admin.register(ProctoringEvent)
class ProctoringEventAdmin(admin.ModelAdmin):
    list_display = ['session', 'event_type', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['session__user__username']
    readonly_fields = ['timestamp']


@admin.register(GeneratedTest)
class GeneratedTestAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'difficulty_level', 'total_questions', 'score', 'is_completed', 'created_at']
    list_filter = ['difficulty_level', 'is_completed', 'created_at']
    search_fields = ['user__username', 'session__content__title']
    readonly_fields = ['created_at', 'started_at', 'completed_at']


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ['test', 'question_type', 'order', 'concept', 'difficulty', 'points']
    list_filter = ['question_type', 'difficulty']
    search_fields = ['question_text', 'concept']


@admin.register(TestSubmission)
class TestSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'is_correct', 'score', 'evaluated_by_ml', 'submitted_at']
    list_filter = ['is_correct', 'evaluated_by_ml', 'submitted_at']
    search_fields = ['user__username']
    readonly_fields = ['submitted_at']


@admin.register(WhiteboardSnapshot)
class WhiteboardSnapshotAdmin(admin.ModelAdmin):
    list_display = ['session', 'created_at']
    list_filter = ['created_at']
    search_fields = ['session__user__username']
    readonly_fields = ['created_at']


@admin.register(SessionMetrics)
class SessionMetricsAdmin(admin.ModelAdmin):
    list_display = ['session', 'engagement_score', 'study_speed', 'total_tab_switches', 'active_time_ratio']
    list_filter = ['calculated_at']
    search_fields = ['session__user__username']
    readonly_fields = ['calculated_at']
