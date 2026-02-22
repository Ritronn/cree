"""
Whiteboard Manager - Handle whiteboard functionality and screenshots
"""
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import StudySession, WhiteboardSnapshot
import base64
import io


class WhiteboardManager:
    """Manage whiteboard functionality during study sessions"""
    
    @classmethod
    def save_whiteboard_state(cls, session_id: int, state_data: dict) -> dict:
        """
        Save current whiteboard state
        
        Args:
            session_id: StudySession ID
            state_data: dict with whiteboard drawing data
            
        Returns:
            dict with success status
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        # Store state data in session or separate model if needed
        # For now, we'll just acknowledge the save
        return {
            'success': True,
            'session_id': session_id,
            'timestamp': timezone.now()
        }
    
    @classmethod
    def capture_screenshot(cls, session_id: int, image_data: str, notes: str = '') -> dict:
        """
        Save screenshot and return URL
        
        Args:
            session_id: StudySession ID
            image_data: base64 encoded image data or file
            notes: optional user notes
            
        Returns:
            dict with screenshot URL and ID
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        try:
            # Handle base64 encoded image
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                # Extract base64 data
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Decode base64
                image_bytes = base64.b64decode(imgstr)
                
                # Create file
                image_file = ContentFile(image_bytes, name=f'whiteboard_{session_id}_{timezone.now().timestamp()}.{ext}')
                
                # Create snapshot
                snapshot = WhiteboardSnapshot.objects.create(
                    session=session,
                    image=image_file,
                    notes=notes
                )
                
                return {
                    'success': True,
                    'snapshot_id': snapshot.id,
                    'image_url': snapshot.image.url if snapshot.image else None,
                    'created_at': snapshot.created_at
                }
            
            return {'error': 'Invalid image data format'}
        
        except Exception as e:
            return {'error': f'Screenshot capture failed: {str(e)}'}
    
    @classmethod
    def download_whiteboard(cls, session_id: int) -> dict:
        """
        Generate downloadable whiteboard file
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with download URL or file data
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        # Get all snapshots for this session
        snapshots = WhiteboardSnapshot.objects.filter(session=session).order_by('-created_at')
        
        if not snapshots.exists():
            return {'error': 'No whiteboard snapshots found'}
        
        # Return latest snapshot
        latest = snapshots.first()
        
        return {
            'success': True,
            'download_url': latest.image.url if latest.image else None,
            'snapshot_count': snapshots.count(),
            'latest_snapshot_id': latest.id
        }
    
    @classmethod
    def clear_whiteboard(cls, session_id: int) -> dict:
        """
        Clear whiteboard state
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with success status
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        # Just acknowledge the clear - actual clearing happens on frontend
        return {
            'success': True,
            'session_id': session_id,
            'message': 'Whiteboard cleared'
        }
    
    @classmethod
    def get_all_snapshots(cls, session_id: int) -> dict:
        """
        Get all whiteboard snapshots for a session
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with list of snapshots
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        snapshots = WhiteboardSnapshot.objects.filter(session=session).order_by('-created_at')
        
        snapshot_list = []
        for snapshot in snapshots:
            snapshot_list.append({
                'id': snapshot.id,
                'image_url': snapshot.image.url if snapshot.image else None,
                'notes': snapshot.notes,
                'created_at': snapshot.created_at
            })
        
        return {
            'success': True,
            'snapshots': snapshot_list,
            'count': len(snapshot_list)
        }
