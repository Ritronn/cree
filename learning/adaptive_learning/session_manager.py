"""
Session Manager - Handles study session lifecycle, timers, and breaks
"""
from datetime import datetime, timedelta
from django.utils import timezone
from .models import StudySession, SessionMetrics


class SessionManager:
    """Manage study session lifecycle and timing"""
    
    # Session configurations (in seconds)
    RECOMMENDED_STUDY_TIME = 2 * 60 * 60  # 2 hours
    RECOMMENDED_BREAK_TIME = 20 * 60  # 20 minutes
    STANDARD_STUDY_TIME = 50 * 60  # 50 minutes
    STANDARD_BREAK_TIME = 10 * 60  # 10 minutes
    
    # Reminder times for recommended mode (in seconds)
    REMINDER_70_MIN = 70 * 60
    REMINDER_90_MIN = 90 * 60
    
    @classmethod
    def create_session(cls, user, content, session_type='recommended', workspace_name='My Study Session'):
        """
        Create a new study session
        
        Args:
            user: User instance
            content: Content instance
            session_type: 'recommended', 'standard', or 'custom'
            workspace_name: Name for the workspace
            
        Returns:
            StudySession instance
        """
        # Calculate test availability (6 hours from now)
        test_available_until = timezone.now() + timedelta(hours=6)
        
        session = StudySession.objects.create(
            user=user,
            content=content,
            session_type=session_type,
            workspace_name=workspace_name,
            test_available_until=test_available_until,
            is_active=True
        )
        
        # Create associated metrics object
        SessionMetrics.objects.create(session=session)
        
        return session
    
    @classmethod
    def get_session_config(cls, session_type):
        """Get timing configuration for session type"""
        if session_type == 'recommended':
            return {
                'study_time': cls.RECOMMENDED_STUDY_TIME,
                'break_time': cls.RECOMMENDED_BREAK_TIME,
                'break_flexible': True
            }
        else:  # standard
            return {
                'study_time': cls.STANDARD_STUDY_TIME,
                'break_time': cls.STANDARD_BREAK_TIME,
                'break_flexible': False
            }
    
    @classmethod
    def start_break(cls, session_id):
        """
        Start break timer
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with break info
        """
        try:
            session = StudySession.objects.get(id=session_id, is_active=True)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found or not active'}
        
        if session.break_used:
            return {'error': 'Break already used'}
        
        # Mark break as started
        session.break_started_at = timezone.now()
        session.break_used = True
        session.save()
        
        config = cls.get_session_config(session.session_type)
        
        return {
            'success': True,
            'break_started_at': session.break_started_at,
            'break_duration_seconds': config['break_time'],
            'break_flexible': config['break_flexible']
        }
    
    @classmethod
    def end_break(cls, session_id):
        """
        End break and resume session
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with session info
        """
        try:
            session = StudySession.objects.get(id=session_id, is_active=True)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found or not active'}
        
        if not session.break_started_at:
            return {'error': 'Break not started'}
        
        # Calculate break duration
        break_end = timezone.now()
        break_duration = (break_end - session.break_started_at).total_seconds()
        
        session.break_ended_at = break_end
        session.break_duration_seconds = int(break_duration)
        session.save()
        
        # Check if study time is complete
        elapsed_study_time = cls.get_elapsed_study_time(session)
        config = cls.get_session_config(session.session_type)
        
        if elapsed_study_time >= config['study_time']:
            return cls.complete_session(session_id)
        
        return {
            'success': True,
            'break_ended_at': break_end,
            'break_duration_seconds': session.break_duration_seconds,
            'resume_study': True
        }
    
    @classmethod
    def check_reminder_trigger(cls, session):
        """
        Check if break reminder should be shown (recommended mode only)
        
        Args:
            session: StudySession instance
            
        Returns:
            dict with reminder info
        """
        if session.session_type != 'recommended':
            return {'show_reminder': False}
        
        if session.break_used:
            return {'show_reminder': False}
        
        elapsed = cls.get_elapsed_study_time(session)
        
        # Check 70-minute reminder
        if elapsed >= cls.REMINDER_70_MIN and not session.reminder_70_shown:
            session.reminder_70_shown = True
            session.save()
            return {
                'show_reminder': True,
                'reminder_type': '70_min',
                'message': 'You\'ve been studying for 70 minutes. Consider taking a break soon.'
            }
        
        # Check 90-minute reminder
        if elapsed >= cls.REMINDER_90_MIN and not session.reminder_90_shown:
            session.reminder_90_shown = True
            session.save()
            return {
                'show_reminder': True,
                'reminder_type': '90_min',
                'message': 'You\'ve been studying for 90 minutes. A break is recommended.'
            }
        
        return {'show_reminder': False}
    
    @classmethod
    def get_elapsed_study_time(cls, session):
        """
        Calculate elapsed study time (excluding breaks)
        
        Args:
            session: StudySession instance
            
        Returns:
            int: elapsed seconds
        """
        now = timezone.now()
        total_elapsed = (now - session.started_at).total_seconds()
        
        # Subtract break time if break is active
        if session.break_started_at and not session.break_ended_at:
            break_elapsed = (now - session.break_started_at).total_seconds()
            return int(total_elapsed - break_elapsed)
        
        # Subtract completed break time
        return int(total_elapsed - session.break_duration_seconds)
    
    @classmethod
    def get_session_status(cls, session_id):
        """
        Get current session status
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with session status
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        config = cls.get_session_config(session.session_type)
        elapsed_study = cls.get_elapsed_study_time(session)
        
        # Check if session should auto-complete
        if elapsed_study >= config['study_time'] and session.is_active:
            # Mark break as expired if not used
            if not session.break_used and session.session_type == 'recommended':
                session.break_expired = True
                session.save()
        
        # Check for reminders
        reminder_info = cls.check_reminder_trigger(session)
        
        return {
            'session_id': session.id,
            'session_type': session.session_type,
            'is_active': session.is_active,
            'is_completed': session.is_completed,
            'elapsed_study_seconds': elapsed_study,
            'total_study_seconds': config['study_time'],
            'remaining_study_seconds': max(0, config['study_time'] - elapsed_study),
            'break_used': session.break_used,
            'break_expired': session.break_expired,
            'break_active': session.break_started_at is not None and session.break_ended_at is None,
            'break_duration_seconds': session.break_duration_seconds,
            'camera_enabled': session.camera_enabled,
            'reminder': reminder_info
        }
    
    @classmethod
    def complete_session(cls, session_id):
        """
        Mark session as complete and calculate final metrics
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with session summary
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        if session.is_completed:
            return {'error': 'Session already completed'}
        
        # Mark as completed
        session.is_active = False
        session.is_completed = True
        session.ended_at = timezone.now()
        session.study_duration_seconds = cls.get_elapsed_study_time(session)
        
        # Mark break as expired if not used (recommended mode)
        if not session.break_used and session.session_type == 'recommended':
            session.break_expired = True
        
        session.save()
        
        # Get metrics
        try:
            metrics = session.metrics
        except SessionMetrics.DoesNotExist:
            metrics = SessionMetrics.objects.create(session=session)
        
        return {
            'success': True,
            'session_id': session.id,
            'completed_at': session.ended_at,
            'total_study_seconds': session.study_duration_seconds,
            'break_duration_seconds': session.break_duration_seconds,
            'break_expired': session.break_expired,
            'engagement_score': metrics.engagement_score,
            'violations': {
                'tab_switches': metrics.total_tab_switches,
                'focus_losses': metrics.total_focus_losses
            }
        }
    
    @classmethod
    def update_camera_status(cls, session_id, enabled):
        """
        Update camera permission status
        
        Args:
            session_id: StudySession ID
            enabled: bool
            
        Returns:
            dict with status
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        session.camera_enabled = enabled
        session.camera_permission_requested = True
        session.save()
        
        return {
            'success': True,
            'camera_enabled': enabled
        }
