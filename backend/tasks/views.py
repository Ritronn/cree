"""
API views for Task Management with Groq AI classification,
drag-and-drop quadrant control, Google Calendar integration,
and roadmap.sh learning paths.
"""
import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Task, Flashcard, Course
from .serializers import TaskSerializer, FlashcardSerializer, CourseSerializer
from .categorization import categorize_task
from .calendar_service import are_calendar_credentials_configured, get_google_auth_url
from .flashcard_service import generate_flashcards_from_topic


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations with auto Groq/formula categorization.

    Endpoints:
    - POST   /api/tasks/               — Create task (AI auto-classifies)
    - GET    /api/tasks/               — List tasks (filters: quadrant, is_completed)
    - GET    /api/tasks/{id}/          — Get single task
    - PATCH  /api/tasks/{id}/          — Update task
    - DELETE /api/tasks/{id}/          — Delete task
    - PATCH  /api/tasks/{id}/move/     — Drag-and-drop: move to new quadrant
    - POST   /api/tasks/{id}/sync_calendar/ — Sync task to Google Calendar
    - GET    /api/calendar/status/     — Check Calendar credentials status
    """
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return all non-deleted tasks with optional filters."""
        queryset = Task.objects.filter(is_deleted=False)

        quadrant = self.request.query_params.get('quadrant')
        if quadrant:
            queryset = queryset.filter(quadrant=quadrant)

        is_completed = self.request.query_params.get('is_completed')
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')

        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        """Create task and trigger automatic Groq/formula categorization."""
        # Use or create a demo user
        demo_user, _ = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@example.com'}
        )

        task = serializer.save(user=demo_user)

        # Auto-classify (Groq AI → formula fallback)
        categorization = categorize_task(task)
        if categorization:
            task.urgency_score = categorization['urgency_score']
            task.importance_score = categorization['importance_score']
            task.quadrant = categorization['quadrant']
            task.save()

    def perform_update(self, serializer):
        """Update task and recategorize if not manually categorized."""
        task = serializer.save()
        if not task.is_manually_categorized:
            categorization = categorize_task(task)
            if categorization:
                task.urgency_score = categorization['urgency_score']
                task.importance_score = categorization['importance_score']
                task.quadrant = categorization['quadrant']
                task.save()

    def destroy(self, request, *args, **kwargs):
        """Soft-delete a task."""
        task = self.get_object()
        task.is_deleted = True
        task.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='move')
    def move(self, request, pk=None):
        """
        Drag-and-drop: move task to a different quadrant.
        Marks task as manually categorized.

        PATCH /api/tasks/{id}/move/
        Body: {"quadrant": "urgent_important"}
        """
        task = self.get_object()
        new_quadrant = request.data.get('quadrant')

        valid_quadrants = ['urgent_important', 'important_not_urgent', 'urgent_not_important', 'neither']
        if new_quadrant not in valid_quadrants:
            return Response(
                {'error': f'Invalid quadrant. Must be one of: {", ".join(valid_quadrants)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.quadrant = new_quadrant
        task.is_manually_categorized = True
        task.save()

        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='sync_calendar')
    def sync_calendar(self, request, pk=None):
        """
        Sync a task to Google Calendar.

        POST /api/tasks/{id}/sync_calendar/
        Body: {"access_token": "ya29..."}
        """
        if not are_calendar_credentials_configured():
            return Response({
                'error': 'Google Calendar not configured',
                'help': 'Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to backend/.env',
                'auth_url': None,
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        task = self.get_object()
        access_token = request.data.get('access_token')

        if not access_token:
            # Return OAuth URL for the client to initiate auth
            auth_url = get_google_auth_url(state=str(task.id))
            return Response({
                'need_auth': True,
                'auth_url': auth_url,
            }, status=status.HTTP_200_OK)

        try:
            from .calendar_service import create_calendar_event
            result = create_calendar_event(task, access_token)
            task.calendar_event_id = result['event_id']
            task.save()
            return Response({
                'success': True,
                'event_id': result['event_id'],
                'html_link': result['html_link'],
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='complete')
    def complete(self, request):
        """Mark a task as completed: PATCH /api/tasks/{id}/complete/"""
        return Response({'error': 'Use PATCH /api/tasks/{id}/ with is_completed=true'})


class CalendarStatusView(APIView):
    """Return Google Calendar configuration status."""
    permission_classes = [AllowAny]

    def get(self, request):
        configured = are_calendar_credentials_configured()
        return Response({
            'configured': configured,
            'auth_url': get_google_auth_url() if configured else None,
            'message': 'Google Calendar is ready' if configured
                       else 'Add real Google OAuth credentials to backend/.env to enable Calendar sync',
        })


class CalendarCallbackView(APIView):
    """
    Handle Google OAuth2 callback.
    Exchanges the auth code for an access token, then redirects
    the user back to the frontend with the token as a query param.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        state = request.query_params.get('state', '')
        error = request.query_params.get('error')

        frontend_url = 'http://localhost:5173'

        if error:
            return HttpResponseRedirect(
                f'{frontend_url}?calendar_error={error}'
            )

        if not code:
            return HttpResponseRedirect(
                f'{frontend_url}?calendar_error=no_code'
            )

        try:
            from google_auth_oauthlib.flow import Flow

            client_config = {
                "web": {
                    "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                    "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                    "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI',
                                                'http://localhost:8000/api/calendar/callback/')],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            }

            flow = Flow.from_client_config(
                client_config,
                scopes=['https://www.googleapis.com/auth/calendar.events'],
                redirect_uri=os.getenv('GOOGLE_REDIRECT_URI',
                                       'http://localhost:8000/api/calendar/callback/')
            )

            flow.fetch_token(code=code)
            credentials = flow.credentials

            # Redirect back to frontend with the access token
            import urllib.parse
            params = {
                'google_token': credentials.token,
                'calendar_task': state,
            }
            if credentials.refresh_token:
                params['google_refresh'] = credentials.refresh_token

            return HttpResponseRedirect(
                f'{frontend_url}?{urllib.parse.urlencode(params)}'
            )

        except Exception as e:
            import urllib.parse
            return HttpResponseRedirect(
                f'{frontend_url}?calendar_error={urllib.parse.quote(str(e))}'
            )


# ─── Roadmap Views ──────────────────────────────────────────────

class RoadmapListView(APIView):
    """Return list of available roadmap.sh roadmaps."""
    permission_classes = [AllowAny]

    def get(self, request):
        from .roadmap_service import get_available_roadmaps
        roadmaps = get_available_roadmaps()
        return Response({
            'roadmaps': roadmaps,
            'count': len(roadmaps),
        })


class RoadmapDataView(APIView):
    """Return raw JSON data for a specific roadmap (native rendering)."""
    permission_classes = [AllowAny]

    def get(self, request, slug):
        from .roadmap_service import get_roadmap_data
        data = get_roadmap_data(slug)
        if not data:
            return Response({'error': 'Roadmap data not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)


class RoadmapGenerateView(APIView):
    """
    Generate a custom learning roadmap from one topic to another.

    POST /api/roadmap/generate/
    Body: {"from_topic": "Python", "to_topic": "Machine Learning"}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        from_topic = request.data.get('from_topic', '').strip()
        to_topic = request.data.get('to_topic', '').strip()

        if not from_topic or not to_topic:
            return Response(
                {'error': 'Both from_topic and to_topic are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from .roadmap_service import generate_custom_roadmap
        roadmap = generate_custom_roadmap(from_topic, to_topic)
        return Response(roadmap)


class RoadmapToTasksView(APIView):
    """
    Convert roadmap milestones into Eisenhower Matrix tasks.

    POST /api/roadmap/to-tasks/
    Body: {"topics": [{"name": "...", "description": "...", "estimated_hours": N}, ...]}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        topics = request.data.get('topics', [])
        if not topics:
            return Response(
                {'error': 'No topics provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        demo_user, _ = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@example.com'}
        )

        from django.utils import timezone
        from datetime import timedelta
        from decimal import Decimal

        created_tasks = []
        for i, topic in enumerate(topics):
            name = topic.get('name', f'Roadmap Topic {i+1}')
            desc = topic.get('description', '')
            hours = float(topic.get('estimated_hours', 2))

            # Spread deadlines across future days
            deadline = timezone.now() + timedelta(days=(i + 1) * 3)

            task = Task.objects.create(
                user=demo_user,
                title=f'📚 {name}',
                description=desc,
                deadline=deadline,
                estimated_time_hours=Decimal(str(max(0.5, hours))),
            )

            # Auto-classify
            categorization = categorize_task(task)
            if categorization:
                task.urgency_score = categorization['urgency_score']
                task.importance_score = categorization['importance_score']
                task.quadrant = categorization['quadrant']
                task.save()

            created_tasks.append(TaskSerializer(task).data)

        return Response({
            'created': len(created_tasks),
            'tasks': created_tasks,
        }, status=status.HTTP_201_CREATED)


# ─── Flashcard (Que-Que Card) Views ──────────────────────────────

class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course management."""
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]
    queryset = Course.objects.all()

    def get_queryset(self):
        return Course.objects.all()


class FlashcardViewSet(viewsets.ModelViewSet):
    """ViewSet for Flashcard management."""
    serializer_class = FlashcardSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Flashcard.objects.all()
        task_id = self.request.query_params.get('task_id')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        is_favorite = self.request.query_params.get('is_favorite')
        if is_favorite:
            queryset = queryset.filter(is_favorite=is_favorite.lower() == 'true')

        return queryset

    @action(detail=False, methods=['delete'], url_path='delete_topic')
    def delete_topic(self, request):
        """Delete all flashcards for a specific topic."""
        topic = request.query_params.get('topic')
        if not topic:
            return Response({'error': 'Topic parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        count, _ = Flashcard.objects.filter(topic=topic).delete()
        return Response({'success': True, 'deleted': count}, status=status.HTTP_200_OK)


class FlashcardGenerateView(APIView):
    """
    Generate flashcards for a specific task or topic using AI.
    
    POST /api/flashcards/generate/
    Body: {"task_id": "...", "topic": "...", "description": "...", "scope": "..."}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        task_id = request.data.get('task_id')
        topic = request.data.get('topic')
        description = request.data.get('description', '')
        scope = request.data.get('scope', 'specific_topics')

        if task_id:
            task = get_object_or_404(Task, id=task_id)
            topic = topic or task.title
            description = description or task.description

        if not topic:
            return Response({'error': 'Topic is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate cards via AI
        cards_data = generate_flashcards_from_topic(topic, description, scope)
        
        demo_user, _ = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@example.com'}
        )

        created_cards = []
        for card in cards_data:
            flashcard = Flashcard.objects.create(
                user=demo_user,
                task_id=task_id if task_id else None,
                topic=topic,
                question=card.get('question'),
                answer=card.get('answer')
            )
            created_cards.append(FlashcardSerializer(flashcard).data)

        return Response({
            'success': True,
            'count': len(created_cards),
            'cards': created_cards
        }, status=status.HTTP_201_CREATED)
