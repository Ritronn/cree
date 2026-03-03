"""
Google Calendar integration service for the Eisenhower Matrix app.
Handles OAuth flow and event creation/updates.
"""
import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def are_calendar_credentials_configured():
    """Check if real Google Calendar credentials are present."""
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
    return (
        client_id and
        client_secret and
        client_id != 'your-google-client-id' and
        client_secret != 'your-google-client-secret'
    )


def get_google_auth_url(state=None):
    """Generate Google OAuth2 authorization URL."""
    if not are_calendar_credentials_configured():
        return None

    try:
        from google_auth_oauthlib.flow import Flow

        client_config = {
            "web": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/calendar/callback/')],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/calendar.events'],
            redirect_uri=os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/calendar/callback/')
        )

        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state or ''
        )
        return auth_url
    except Exception as e:
        logger.error(f"Error generating auth URL: {e}")
        return None


def create_calendar_event(task, access_token):
    """
    Create a Google Calendar event for a task.

    Args:
        task: Task model instance
        access_token: Valid Google OAuth access token

    Returns:
        dict with event_id and html_link, or raises an exception
    """
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials

        credentials = Credentials(token=access_token)
        service = build('calendar', 'v3', credentials=credentials)

        # Calculate event end time (deadline - estimated_hours to deadline)
        import datetime
        deadline = task.deadline
        estimated_secs = int(float(task.estimated_time_hours) * 3600)
        start_time = deadline - datetime.timedelta(seconds=estimated_secs)

        # Add quadrant emoji and label
        quadrant_labels = {
            'urgent_important': '🔴 [Do First]',
            'important_not_urgent': '🟡 [Schedule]',
            'urgent_not_important': '🔵 [Delegate]',
            'neither': '⚫ [Eliminate]',
        }
        label = quadrant_labels.get(task.quadrant, '')

        event_body = {
            'summary': f"{label} {task.title}",
            'description': (
                f"{task.description}\n\n"
                f"---\n"
                f"Eisenhower Quadrant: {task.get_quadrant_display()}\n"
                f"Urgency Score: {task.urgency_score}\n"
                f"Importance Score: {task.importance_score}\n"
                f"Estimated Time: {task.estimated_time_hours}h\n"
                f"Created by Eisenhower Matrix Task Manager"
            ),
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': deadline.isoformat(),
                'timeZone': 'UTC',
            },
            'colorId': _get_calendar_color(task.quadrant),
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 60},
                    {'method': 'email', 'minutes': 1440},  # 1 day before
                ],
            },
        }

        # Update existing event if we have one
        if task.calendar_event_id:
            event = service.events().update(
                calendarId='primary',
                eventId=task.calendar_event_id,
                body=event_body
            ).execute()
        else:
            event = service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()

        return {
            'event_id': event['id'],
            'html_link': event.get('htmlLink', ''),
        }

    except Exception as e:
        logger.error(f"Calendar event creation failed: {e}")
        raise


def _get_calendar_color(quadrant):
    """Map Eisenhower quadrant to Google Calendar color ID."""
    color_map = {
        'urgent_important': '11',       # Tomato (red)
        'important_not_urgent': '5',    # Banana (yellow)
        'urgent_not_important': '7',    # Peacock (blue)
        'neither': '8',                 # Graphite (gray)
    }
    return color_map.get(quadrant, '8')
