"""
Monitoring Collector - Collect and aggregate engagement metrics
"""
from django.utils import timezone
from .models import StudySession, SessionMetrics
import json


class MonitoringCollector:
    """Collect and aggregate engagement metrics during study sessions"""
    
    @classmethod
    def record_event(cls, session_id, event_type, event_data=None):
        """
        Record a monitoring event
        
        Args:
            session_id: StudySession ID
            event_type: Type of event (e.g., 'video_pause', 'scroll', 'interaction')
            event_data: dict with event-specific data
            
        Returns:
            dict with success status
        """
        try:
            session = StudySession.objects.get(id=session_id, is_active=True)
            metrics = session.metrics
        except StudySession.DoesNotExist:
            return {'error': 'Session not found or not active'}
        except SessionMetrics.DoesNotExist:
            metrics = SessionMetrics.objects.create(session=session)
        
        # Update content interactions
        interactions = metrics.content_interactions
        if event_type not in interactions:
            interactions[event_type] = 0
        interactions[event_type] += 1
        metrics.content_interactions = interactions
        
        # Update specific counters
        if event_type == 'chat_query':
            metrics.chat_queries_count += 1
        elif event_type == 'whiteboard_snapshot':
            metrics.whiteboard_snapshots_count += 1
        
        metrics.save()
        
        return {
            'success': True,
            'event_type': event_type,
            'timestamp': timezone.now()
        }
    
    @classmethod
    def calculate_engagement_score(cls, session_id):
        """
        Calculate current engagement score (0-100)
        
        Formula:
        - Base score: 100
        - Penalties:
          - Tab switches: -2 per switch
          - Focus losses: -1 per loss
          - Low interaction rate: -10 if < 1 interaction/min
        - Bonuses:
          - High interaction rate: +5 if > 5 interactions/min
          - Chat usage: +5 if used
        
        Args:
            session_id: StudySession ID
            
        Returns:
            float: engagement score (0-100)
        """
        try:
            session = StudySession.objects.get(id=session_id)
            metrics = session.metrics
        except (StudySession.DoesNotExist, SessionMetrics.DoesNotExist):
            return 0.0
        
        score = 100.0
        
        # Calculate elapsed time in minutes
        elapsed_seconds = (timezone.now() - session.started_at).total_seconds()
        elapsed_minutes = max(elapsed_seconds / 60, 1)  # Avoid division by zero
        
        # Penalties
        score -= metrics.total_tab_switches * 2
        score -= metrics.total_focus_losses * 1
        
        # Interaction rate
        total_interactions = sum(metrics.content_interactions.values())
        interaction_rate = total_interactions / elapsed_minutes
        
        if interaction_rate < 1:
            score -= 10
        elif interaction_rate > 5:
            score += 5
        
        # Chat usage bonus
        if metrics.chat_queries_count > 0:
            score += 5
        
        # Clamp score between 0 and 100
        score = max(0.0, min(100.0, score))
        
        # Update metrics
        metrics.engagement_score = score
        metrics.interaction_rate = interaction_rate
        metrics.save()
        
        return score
    
    @classmethod
    def calculate_study_speed(cls, session_id):
        """
        Calculate content consumption rate
        
        Args:
            session_id: StudySession ID
            
        Returns:
            float: content units per minute
        """
        try:
            session = StudySession.objects.get(id=session_id)
            metrics = session.metrics
        except (StudySession.DoesNotExist, SessionMetrics.DoesNotExist):
            return 0.0
        
        # Calculate based on content interactions
        elapsed_seconds = (timezone.now() - session.started_at).total_seconds()
        elapsed_minutes = max(elapsed_seconds / 60, 1)
        
        total_interactions = sum(metrics.content_interactions.values())
        study_speed = total_interactions / elapsed_minutes
        
        metrics.study_speed = study_speed
        metrics.save()
        
        return study_speed
    
    @classmethod
    def get_study_habits(cls, session_id):
        """
        Analyze study patterns and habits
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with habit analysis
        """
        try:
            session = StudySession.objects.get(id=session_id)
            metrics = session.metrics
        except (StudySession.DoesNotExist, SessionMetrics.DoesNotExist):
            return {}
        
        elapsed_seconds = (timezone.now() - session.started_at).total_seconds()
        elapsed_minutes = max(elapsed_seconds / 60, 1)
        
        # Analyze patterns
        habits = {
            'session_duration_minutes': elapsed_minutes,
            'break_taken': session.break_used,
            'interaction_frequency': 'high' if metrics.interaction_rate > 5 else 'medium' if metrics.interaction_rate > 2 else 'low',
            'focus_stability': 'stable' if metrics.total_focus_losses < 3 else 'moderate' if metrics.total_focus_losses < 10 else 'unstable',
            'chat_usage': 'active' if metrics.chat_queries_count > 5 else 'moderate' if metrics.chat_queries_count > 0 else 'none',
            'whiteboard_usage': 'active' if metrics.whiteboard_snapshots_count > 3 else 'moderate' if metrics.whiteboard_snapshots_count > 0 else 'none',
            'violation_rate': (metrics.total_tab_switches + metrics.total_focus_losses) / elapsed_minutes
        }
        
        return habits
    
    @classmethod
    def aggregate_metrics(cls, session_id):
        """
        Aggregate all metrics for ML model input
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with aggregated metrics
        """
        try:
            session = StudySession.objects.get(id=session_id)
            metrics = session.metrics
        except (StudySession.DoesNotExist, SessionMetrics.DoesNotExist):
            return {}
        
        # Calculate all metrics
        engagement_score = cls.calculate_engagement_score(session_id)
        study_speed = cls.calculate_study_speed(session_id)
        habits = cls.get_study_habits(session_id)
        
        # Calculate time metrics
        elapsed_seconds = (timezone.now() - session.started_at).total_seconds()
        active_time = elapsed_seconds - session.break_duration_seconds
        
        # Update metrics
        metrics.total_active_time_seconds = int(active_time)
        metrics.total_idle_time_seconds = session.break_duration_seconds
        metrics.active_time_ratio = active_time / max(elapsed_seconds, 1)
        
        # Calculate average focus duration
        if metrics.total_focus_losses > 0:
            metrics.average_focus_duration_seconds = active_time / (metrics.total_focus_losses + 1)
        else:
            metrics.average_focus_duration_seconds = active_time
        
        metrics.save()
        
        # Return aggregated data for ML model
        return {
            'session_id': session_id,
            'engagement_score': engagement_score,
            'study_speed': study_speed,
            'interaction_rate': metrics.interaction_rate,
            'total_active_time_seconds': metrics.total_active_time_seconds,
            'active_time_ratio': metrics.active_time_ratio,
            'tab_switches': metrics.total_tab_switches,
            'focus_losses': metrics.total_focus_losses,
            'average_focus_duration_seconds': metrics.average_focus_duration_seconds,
            'chat_queries_count': metrics.chat_queries_count,
            'whiteboard_snapshots_count': metrics.whiteboard_snapshots_count,
            'habits': habits,
            'content_interactions': metrics.content_interactions
        }
    
    @classmethod
    def update_real_time_metrics(cls, session_id):
        """
        Update metrics in real-time (called every 10 seconds from frontend)
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with current metrics
        """
        engagement_score = cls.calculate_engagement_score(session_id)
        study_speed = cls.calculate_study_speed(session_id)
        
        try:
            session = StudySession.objects.get(id=session_id)
            metrics = session.metrics
        except (StudySession.DoesNotExist, SessionMetrics.DoesNotExist):
            return {}
        
        return {
            'engagement_score': engagement_score,
            'study_speed': study_speed,
            'interaction_rate': metrics.interaction_rate,
            'tab_switches': metrics.total_tab_switches,
            'focus_losses': metrics.total_focus_losses
        }
