"""
Proctoring Engine - Enforce AMCAT-level rules and monitor violations
"""
from django.utils import timezone
from .models import ProctoringEvent, StudySession


class ProctoringEngine:
    """Handle proctoring events and violations"""
    
    # Allowed screenshot sources
    ALLOWED_SCREENSHOT_SOURCES = ['whiteboard', 'chat']
    
    @classmethod
    def initialize_proctoring(cls, session_id):
        """
        Initialize proctoring for a session
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with proctoring config
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        return {
            'success': True,
            'session_id': session_id,
            'rules': {
                'tab_switching': 'monitored',
                'copy_paste': 'blocked',
                'screenshots': 'conditional',  # Allowed for whiteboard/chat only
                'camera': 'requested'
            },
            'allowed_screenshot_sources': cls.ALLOWED_SCREENSHOT_SOURCES
        }
    
    @classmethod
    def record_tab_switch(cls, session_id, timestamp=None):
        """Record tab switch violation"""
        return cls._record_event(session_id, 'tab_switch', timestamp)
    
    @classmethod
    def record_copy_attempt(cls, session_id, timestamp=None):
        """Record copy attempt"""
        return cls._record_event(session_id, 'copy_attempt', timestamp)
    
    @classmethod
    def record_paste_attempt(cls, session_id, timestamp=None):
        """Record paste attempt"""
        return cls._record_event(session_id, 'paste_attempt', timestamp)
    
    @classmethod
    def record_focus_lost(cls, session_id, timestamp=None):
        """Record window focus lost"""
        return cls._record_event(session_id, 'focus_lost', timestamp)
    
    @classmethod
    def record_focus_gained(cls, session_id, timestamp=None):
        """Record window focus gained"""
        return cls._record_event(session_id, 'focus_gained', timestamp)
    
    @classmethod
    def record_screenshot_attempt(cls, session_id, source, timestamp=None):
        """
        Record screenshot attempt and determine if allowed
        
        Args:
            session_id: StudySession ID
            source: 'content', 'whiteboard', or 'chat'
            timestamp: optional datetime
            
        Returns:
            dict with allowed status
        """
        allowed = source in cls.ALLOWED_SCREENSHOT_SOURCES
        event_type = 'screenshot_allowed' if allowed else 'screenshot_blocked'
        
        cls._record_event(
            session_id,
            event_type,
            timestamp,
            details={'source': source}
        )
        
        return {
            'allowed': allowed,
            'source': source,
            'message': f'Screenshot {"allowed" if allowed else "blocked"} for {source}'
        }
    
    @classmethod
    def record_camera_status(cls, session_id, enabled, timestamp=None):
        """Record camera enable/disable event"""
        event_type = 'camera_enabled' if enabled else 'camera_disabled'
        return cls._record_event(
            session_id,
            event_type,
            timestamp,
            details={'enabled': enabled}
        )
    
    @classmethod
    def _record_event(cls, session_id, event_type, timestamp=None, details=None):
        """
        Internal method to record proctoring event
        
        Args:
            session_id: StudySession ID
            event_type: Type of event
            timestamp: optional datetime
            details: optional dict with additional data
            
        Returns:
            dict with success status
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        event = ProctoringEvent.objects.create(
            session=session,
            event_type=event_type,
            details=details or {}
        )
        
        # Update session metrics
        try:
            metrics = session.metrics
            if event_type == 'tab_switch':
                metrics.total_tab_switches += 1
            elif event_type in ['focus_lost', 'focus_gained']:
                metrics.total_focus_losses += 1
            metrics.save()
        except:
            pass  # Metrics might not exist yet
        
        return {
            'success': True,
            'event_id': event.id,
            'event_type': event_type,
            'timestamp': event.timestamp
        }
    
    @classmethod
    def get_violation_summary(cls, session_id):
        """
        Get summary of all violations for a session
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with violation counts
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        events = ProctoringEvent.objects.filter(session=session)
        
        summary = {
            'session_id': session_id,
            'total_events': events.count(),
            'violations': {
                'tab_switches': events.filter(event_type='tab_switch').count(),
                'copy_attempts': events.filter(event_type='copy_attempt').count(),
                'paste_attempts': events.filter(event_type='paste_attempt').count(),
                'screenshots_blocked': events.filter(event_type='screenshot_blocked').count(),
                'focus_losses': events.filter(event_type='focus_lost').count(),
            },
            'allowed_actions': {
                'screenshots_allowed': events.filter(event_type='screenshot_allowed').count(),
            },
            'camera_status': {
                'enabled': session.camera_enabled,
                'permission_requested': session.camera_permission_requested
            }
        }
        
        return summary

    
    @classmethod
    def request_camera_permission(cls, session_id):
        """
        Request camera permission for a session
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with permission request status
        """
        try:
            session = StudySession.objects.get(id=session_id)
            session.camera_permission_requested = True
            session.save()
            
            return {
                'success': True,
                'session_id': session_id,
                'permission_requested': True,
                'message': 'Camera permission requested'
            }
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
    
    @classmethod
    def handle_camera_permission(cls, session_id, granted):
        """
        Handle camera permission response
        
        Args:
            session_id: StudySession ID
            granted: bool - whether permission was granted
            
        Returns:
            dict with camera status
        """
        try:
            session = StudySession.objects.get(id=session_id)
            session.camera_enabled = granted
            session.save()
            
            # Record event
            cls.record_camera_status(session_id, granted)
            
            return {
                'success': True,
                'session_id': session_id,
                'camera_enabled': granted,
                'message': f'Camera {"enabled" if granted else "disabled"}'
            }
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
    
    @classmethod
    def record_face_detection(cls, session_id, faces_detected, timestamp=None):
        """
        Record face detection event
        
        Args:
            session_id: StudySession ID
            faces_detected: int - number of faces detected
            timestamp: optional datetime
            
        Returns:
            dict with success status
        """
        event_type = 'face_detected' if faces_detected > 0 else 'no_face_detected'
        
        return cls._record_event(
            session_id,
            event_type,
            timestamp,
            details={'faces_detected': faces_detected}
        )
