"""
URL routing for Adaptive Learning API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TopicViewSet, ContentViewSet, AssessmentViewSet,
    MonitoringViewSet, ProgressViewSet
)
from .study_session_views import (
    StudySessionViewSet, MonitoringViewSet as SessionMonitoringViewSet,
    ProctoringViewSet, TestViewSet, WhiteboardViewSet, ChatViewSet
)
from .dashboard_views import DashboardViewSet
from .recommendation_views import WeakPointViewSet, BrowserExtensionViewSet

router = DefaultRouter()
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'content', ContentViewSet, basename='content')
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'monitoring', MonitoringViewSet, basename='monitoring')
router.register(r'progress', ProgressViewSet, basename='progress')

# Dashboard routes
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

# Study Session Monitoring and Testing routes
router.register(r'study-sessions', StudySessionViewSet, basename='study-session')
router.register(r'session-monitoring', SessionMonitoringViewSet, basename='session-monitoring')
router.register(r'proctoring', ProctoringViewSet, basename='proctoring')
router.register(r'tests', TestViewSet, basename='test')
router.register(r'whiteboard', WhiteboardViewSet, basename='whiteboard')
router.register(r'chat', ChatViewSet, basename='chat')

# Weak Points and Recommendations
router.register(r'weak-points', WeakPointViewSet, basename='weak-point')

# Browser Extension
router.register(r'extension', BrowserExtensionViewSet, basename='extension')

urlpatterns = [
    path('', include(router.urls)),
]
