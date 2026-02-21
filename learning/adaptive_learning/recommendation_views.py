"""
Recommendation and Browser Extension API Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import WeakPoint, CourseRecommendation, BrowserExtensionData, StudySession
from .recommendation_service import RecommendationService


class WeakPointViewSet(viewsets.ViewSet):
    """Manage weak points and recommendations"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all weak points for current user"""
        weak_points = WeakPoint.objects.filter(
            user=request.user
        ).order_by('confidence_score')
        
        data = [
            {
                'id': wp.id,
                'topic': wp.topic,
                'subtopic': wp.subtopic,
                'incorrect_count': wp.incorrect_count,
                'total_attempts': wp.total_attempts,
                'accuracy': wp.accuracy,
                'confidence_score': wp.confidence_score,
                'first_identified': wp.first_identified,
                'last_attempted': wp.last_attempted,
                'recommendations_generated': wp.recommendations_generated
            }
            for wp in weak_points
        ]
        
        return Response({
            'count': len(data),
            'weak_points': data
        })
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get all recommendations for user's weak points"""
        result = RecommendationService.get_recommendations_for_user(request.user)
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def generate_recommendations(self, request, pk=None):
        """Generate recommendations for a specific weak point"""
        try:
            weak_point = WeakPoint.objects.get(id=pk, user=request.user)
        except WeakPoint.DoesNotExist:
            return Response(
                {'error': 'Weak point not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        result = RecommendationService.generate_recommendations(weak_point)
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark a recommendation as viewed"""
        recommendation_id = request.data.get('recommendation_id')
        
        try:
            recommendation = CourseRecommendation.objects.get(
                id=recommendation_id,
                user=request.user
            )
            recommendation.viewed = True
            recommendation.save()
            
            return Response({'success': True})
        except CourseRecommendation.DoesNotExist:
            return Response(
                {'error': 'Recommendation not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class BrowserExtensionViewSet(viewsets.ViewSet):
    """Handle browser extension integration"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def heartbeat(self, request):
        """
        Receive heartbeat from browser extension
        
        Expected data:
        {
            "session_id": 123,
            "tab_switches": 5,
            "blocked_attempts": 2,
            "extension_active": true
        }
        """
        session_id = request.data.get('session_id')
        tab_switches = request.data.get('tab_switches', 0)
        blocked_attempts = request.data.get('blocked_attempts', 0)
        extension_active = request.data.get('extension_active', False)
        
        if not session_id:
            return Response(
                {'error': 'session_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = StudySession.objects.get(id=session_id, user=request.user)
        except StudySession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create extension data
        extension_data, created = BrowserExtensionData.objects.get_or_create(
            session=session,
            defaults={
                'tab_switches': tab_switches,
                'blocked_attempts': blocked_attempts,
                'extension_active': extension_active
            }
        )
        
        if not created:
            # Update existing data
            extension_data.tab_switches = tab_switches
            extension_data.blocked_attempts = blocked_attempts
            extension_data.extension_active = extension_active
            extension_data.save()
        
        return Response({
            'success': True,
            'session_id': session_id,
            'extension_active': extension_active
        })
    
    @action(detail=False, methods=['post'])
    def violation(self, request):
        """
        Log a violation from browser extension
        
        Expected data:
        {
            "session_id": 123,
            "event_type": "tab_switch" | "blocked_site",
            "url": "https://example.com",
            "timestamp": "2026-02-20T10:30:00Z"
        }
        """
        session_id = request.data.get('session_id')
        event_type = request.data.get('event_type')
        url = request.data.get('url', '')
        
        if not session_id or not event_type:
            return Response(
                {'error': 'session_id and event_type required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = StudySession.objects.get(id=session_id, user=request.user)
        except StudySession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get extension data
        extension_data = BrowserExtensionData.objects.filter(session=session).first()
        
        if not extension_data:
            extension_data = BrowserExtensionData.objects.create(session=session)
        
        # Add event to log
        event = {
            'timestamp': timezone.now().isoformat(),
            'event_type': event_type,
            'url': url
        }
        
        if not extension_data.events:
            extension_data.events = []
        
        extension_data.events.append(event)
        
        # Update counters
        if event_type == 'tab_switch':
            extension_data.tab_switches += 1
        elif event_type == 'blocked_site':
            extension_data.blocked_attempts += 1
        
        extension_data.save()
        
        # Also create proctoring event
        from .proctoring_engine import ProctoringEngine
        if event_type == 'tab_switch':
            ProctoringEngine.record_tab_switch(session_id)
        
        return Response({
            'success': True,
            'event_logged': True
        })
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get extension status for a session"""
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = StudySession.objects.get(id=session_id, user=request.user)
            extension_data = BrowserExtensionData.objects.filter(session=session).first()
            
            if not extension_data:
                return Response({
                    'extension_active': False,
                    'tab_switches': 0,
                    'blocked_attempts': 0
                })
            
            return Response({
                'extension_active': extension_data.extension_active,
                'tab_switches': extension_data.tab_switches,
                'blocked_attempts': extension_data.blocked_attempts,
                'last_heartbeat': extension_data.last_heartbeat
            })
        
        except StudySession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
