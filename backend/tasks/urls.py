"""
URL configuration for Task Management API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, CalendarStatusView, CalendarCallbackView,
    RoadmapListView, RoadmapDataView, RoadmapGenerateView, RoadmapToTasksView,
    FlashcardViewSet, FlashcardGenerateView, CourseViewSet
)

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'flashcards', FlashcardViewSet, basename='flashcard')
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('calendar/status/', CalendarStatusView.as_view(), name='calendar-status'),
    path('calendar/callback/', CalendarCallbackView.as_view(), name='calendar-callback'),
    path('roadmap/list/', RoadmapListView.as_view(), name='roadmap-list'),
    path('roadmap/data/<str:slug>/', RoadmapDataView.as_view(), name='roadmap-data'),
    path('roadmap/generate/', RoadmapGenerateView.as_view(), name='roadmap-generate'),
    path('roadmap/to-tasks/', RoadmapToTasksView.as_view(), name='roadmap-to-tasks'),
    path('flashcards/generate/', FlashcardGenerateView.as_view(), name='flashcards-generate'),
    path('', include(router.urls)),
]
