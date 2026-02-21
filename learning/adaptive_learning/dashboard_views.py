"""
Dashboard Views - Weekly sessions, completion stats, session limits
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q, Avg
from datetime import timedelta
from .models import StudySession, GeneratedTest, TestResult, SessionLimit, WeakPoint
from .serializers import StudySessionSerializer


class DashboardViewSet(viewsets.ViewSet):
    """Dashboard data and statistics"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get dashboard overview with:
        - Completion percentage
        - Weekly sessions
        - Pending tests
        - Session limits
        """
        user = request.user
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Get weekly sessions
        weekly_sessions = StudySession.objects.filter(
            user=user,
            started_at__date__gte=week_ago
        ).order_by('-started_at')
        
        # Calculate completion stats
        total_sessions = weekly_sessions.count()
        completed_tests = TestResult.objects.filter(
            user=user,
            completed_at__date__gte=week_ago
        ).count()
        
        completion_percentage = (completed_tests / total_sessions * 100) if total_sessions > 0 else 0
        
        # Get pending tests
        pending_tests = GeneratedTest.objects.filter(
            user=user,
            is_completed=False,
            created_at__gte=timezone.now() - timedelta(hours=6)
        ).select_related('session')
        
        # Get or create today's session limit
        session_limit, created = SessionLimit.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'sessions_created': 0,
                'tests_pending': pending_tests.count(),
                'can_create_session': True
            }
        )
        
        # Update session limit status
        if session_limit.tests_pending > 0:
            session_limit.can_create_session = False
            session_limit.blocked_reason = f"Complete {session_limit.tests_pending} pending test(s) first"
        elif session_limit.sessions_created >= session_limit.max_sessions_per_day:
            session_limit.can_create_session = False
            session_limit.blocked_reason = "Daily limit reached (3 sessions per day)"
        else:
            session_limit.can_create_session = True
            session_limit.blocked_reason = ""
        
        session_limit.save()
        
        # Serialize sessions with test status
        sessions_data = []
        for session in weekly_sessions:
            try:
                test = session.generated_test
                test_status = {
                    'exists': True,
                    'test_id': test.id,
                    'completed': test.is_completed,
                    'score': test.score if test.is_completed else None,
                    'expires_at': session.test_available_until,
                    'expired': session.test_available_until < timezone.now() if session.test_available_until else False
                }
            except GeneratedTest.DoesNotExist:
                test_status = {
                    'exists': False,
                    'test_id': None,
                    'completed': False,
                    'score': None,
                    'expires_at': None,
                    'expired': False
                }
            
            sessions_data.append({
                'id': session.id,
                'workspace_name': session.workspace_name,
                'session_type': session.session_type,
                'started_at': session.started_at,
                'ended_at': session.ended_at,
                'is_completed': session.is_completed,
                'study_duration_seconds': session.study_duration_seconds,
                'test_status': test_status
            })
        
        # Get weak points summary
        weak_points_count = WeakPoint.objects.filter(
            user=user,
            confidence_score__lt=0.7
        ).count()
        
        return Response({
            'completion_percentage': round(completion_percentage, 1),
            'total_sessions': total_sessions,
            'completed_tests': completed_tests,
            'pending_tests': pending_tests.count(),
            'weekly_sessions': sessions_data,
            'session_limit': {
                'can_create': session_limit.can_create_session,
                'sessions_today': session_limit.sessions_created,
                'max_sessions': session_limit.max_sessions_per_day,
                'blocked_reason': session_limit.blocked_reason,
                'tests_pending': session_limit.tests_pending
            },
            'weak_points_count': weak_points_count,
            'stats': {
                'total_study_time': sum(s.study_duration_seconds for s in weekly_sessions),
                'average_session_duration': weekly_sessions.aggregate(Avg('study_duration_seconds'))['study_duration_seconds__avg'] or 0,
                'sessions_this_week': total_sessions
            }
        })
    
    @action(detail=False, methods=['get'])
    def weekly_sessions(self, request):
        """Get detailed weekly sessions"""
        user = request.user
        week_ago = timezone.now() - timedelta(days=7)
        
        sessions = StudySession.objects.filter(
            user=user,
            started_at__gte=week_ago
        ).select_related('content').order_by('-started_at')
        
        serializer = StudySessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completion_stats(self, request):
        """Get detailed completion statistics"""
        user = request.user
        
        # All-time stats
        all_sessions = StudySession.objects.filter(user=user, is_completed=True)
        all_tests = TestResult.objects.filter(user=user)
        
        # This month stats
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_sessions = all_sessions.filter(started_at__gte=month_start)
        month_tests = all_tests.filter(completed_at__gte=month_start)
        
        return Response({
            'all_time': {
                'total_sessions': all_sessions.count(),
                'total_tests': all_tests.count(),
                'average_score': all_tests.aggregate(Avg('total_score'))['total_score__avg'] or 0,
                'total_study_hours': sum(s.study_duration_seconds for s in all_sessions) / 3600
            },
            'this_month': {
                'total_sessions': month_sessions.count(),
                'total_tests': month_tests.count(),
                'average_score': month_tests.aggregate(Avg('total_score'))['total_score__avg'] or 0,
                'total_study_hours': sum(s.study_duration_seconds for s in month_sessions) / 3600
            }
        })
