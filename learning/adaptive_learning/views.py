"""
REST API Views for Adaptive Learning System
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    Topic, Content, Assessment, Question, UserAnswer,
    UserProgress, MonitoringSession, ConceptMastery, RevisionQueue
)
from .serializers import (
    TopicSerializer, ContentSerializer, AssessmentSerializer,
    QuestionSerializer, UserAnswerSerializer, UserProgressSerializer,
    MonitoringSessionSerializer, ConceptMasterySerializer,
    RevisionQueueSerializer, AssessmentResultSerializer,
    DifficultyPredictionSerializer
)
from .ml_predictor import predict_next_difficulty, calculate_adaptive_score
from .content_processor import process_content
from .question_generator import generate_questions


class TopicViewSet(viewsets.ModelViewSet):
    """CRUD operations for Topics"""
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Topic.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get detailed progress for a topic"""
        topic = self.get_object()
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            topic=topic
        )
        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def concepts(self, request, pk=None):
        """Get concept mastery breakdown for a topic"""
        topic = self.get_object()
        concepts = ConceptMastery.objects.filter(
            user=request.user,
            topic=topic
        )
        serializer = ConceptMasterySerializer(concepts, many=True)
        return Response(serializer.data)


class ContentViewSet(viewsets.ModelViewSet):
    """CRUD operations for Content"""
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Content.objects.filter(topic__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload and process content"""
        # Auto-create topic if not provided
        topic_id = request.data.get('topic')
        if not topic_id:
            title = request.data.get('title', 'Untitled Topic')
            topic, _ = Topic.objects.get_or_create(
                user=request.user,
                name=title,
                defaults={'description': f'Auto-created topic for: {title}'}
            )
            # Inject topic into request data
            data = request.data.copy()
            data['topic'] = topic.id
        else:
            data = request.data

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        content = serializer.save()
        
        # Process content asynchronously (or synchronously for hackathon)
        try:
            process_content(content)
            content.processed = True
            content.save()
        except Exception as e:
            return Response(
                {'error': f'Content processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(
            ContentSerializer(content).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def generate_assessment(self, request, pk=None):
        """Generate assessment for this content"""
        content = self.get_object()
        
        if not content.processed:
            return Response(
                {'error': 'Content not yet processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user's current difficulty for this topic
        topic = content.topic
        difficulty = topic.current_difficulty
        
        # Create assessment
        assessment = Assessment.objects.create(
            content=content,
            user=request.user,
            difficulty_level=difficulty,
            total_questions=10
        )
        
        # Generate questions
        try:
            questions = generate_questions(
                content=content,
                difficulty=difficulty,
                count=10
            )
            
            # Save questions
            for idx, q_data in enumerate(questions):
                Question.objects.create(
                    assessment=assessment,
                    question_text=q_data['question'],
                    options=q_data['options'],
                    correct_answer_index=q_data['correct_index'],
                    explanation=q_data['explanation'],
                    difficulty=q_data['difficulty'],
                    concept=q_data['concept'],
                    order=idx
                )
        except Exception as e:
            assessment.delete()
            return Response(
                {'error': f'Question generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(
            AssessmentSerializer(assessment).data,
            status=status.HTTP_201_CREATED
        )


class AssessmentViewSet(viewsets.ModelViewSet):
    """CRUD operations for Assessments"""
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Assessment.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get all questions for an assessment"""
        assessment = self.get_object()
        questions = assessment.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Submit answer to a question"""
        assessment = self.get_object()
        question_id = request.data.get('question_id')
        selected_answer = request.data.get('selected_answer_index')
        time_taken = request.data.get('time_taken_seconds')
        
        question = get_object_or_404(Question, id=question_id, assessment=assessment)
        is_correct = selected_answer == question.correct_answer_index
        
        # Save answer
        answer = UserAnswer.objects.create(
            question=question,
            user=request.user,
            selected_answer_index=selected_answer,
            is_correct=is_correct,
            time_taken_seconds=time_taken
        )
        
        return Response(UserAnswerSerializer(answer).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete assessment and calculate results"""
        assessment = self.get_object()
        
        # Mark as completed
        assessment.completed_at = timezone.now()
        assessment.is_completed = True
        
        # Calculate results
        answers = UserAnswer.objects.filter(
            question__assessment=assessment,
            user=request.user
        )
        
        total_questions = assessment.questions.count()
        correct_answers = answers.filter(is_correct=True).count()
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Calculate time metrics
        total_time = sum(a.time_taken_seconds for a in answers)
        avg_time = total_time / total_questions if total_questions > 0 else 0
        
        # Calculate first attempt rate
        first_attempts = answers.filter(attempt_number=1)
        first_attempt_correct = first_attempts.filter(is_correct=True).count()
        first_attempt_rate = (first_attempt_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Calculate adaptive score
        adaptive_score = calculate_adaptive_score(
            accuracy=accuracy,
            avg_time=avg_time,
            first_attempt_rate=first_attempt_rate,
            difficulty=assessment.difficulty_level
        )
        
        assessment.score = accuracy
        assessment.adaptive_score = adaptive_score
        assessment.time_taken_seconds = total_time
        assessment.save()
        
        # Update user progress
        topic = assessment.content.topic
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            topic=topic
        )
        
        # Calculate score trend
        score_trend = 0
        if progress.last_score is not None:
            score_trend = accuracy - progress.last_score
        
        # Update progress metrics
        progress.total_assessments += 1
        progress.last_score = accuracy
        progress.score_trend = score_trend
        progress.last_session_at = timezone.now()
        
        # Recalculate averages
        all_assessments = Assessment.objects.filter(
            content__topic=topic,
            user=request.user,
            is_completed=True
        )
        progress.average_accuracy = sum(a.score for a in all_assessments) / all_assessments.count()
        
        all_answers = UserAnswer.objects.filter(
            question__assessment__content__topic=topic,
            user=request.user
        )
        if all_answers.exists():
            progress.average_time_per_question = sum(a.time_taken_seconds for a in all_answers) / all_answers.count()
            first_attempt_answers = all_answers.filter(attempt_number=1)
            progress.first_attempt_correct_rate = (
                first_attempt_answers.filter(is_correct=True).count() / first_attempt_answers.count() * 100
            )
        
        progress.save()
        
        # Update concept mastery
        self._update_concept_mastery(assessment, answers, topic)
        
        # Predict next difficulty
        next_difficulty = self._predict_next_difficulty(progress, topic)
        
        # Update topic difficulty
        old_difficulty = topic.current_difficulty
        topic.current_difficulty = next_difficulty
        topic.sessions_completed += 1
        topic.mastery_level = progress.average_accuracy / 100
        topic.save()
        
        # Identify weak concepts
        weak_concepts = ConceptMastery.objects.filter(
            user=request.user,
            topic=topic,
            accuracy__lt=70
        ).order_by('accuracy')[:3]
        
        # Prepare result data
        result_data = {
            'assessment_id': assessment.id,
            'score': accuracy,
            'adaptive_score': adaptive_score,
            'time_taken_seconds': total_time,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'accuracy': accuracy,
            'weak_concepts': [
                {
                    'name': c.concept_name,
                    'accuracy': c.accuracy,
                    'mastery_level': c.mastery_level
                }
                for c in weak_concepts
            ],
            'next_difficulty': next_difficulty,
            'difficulty_changed': next_difficulty != old_difficulty,
            'feedback_message': self._generate_feedback(accuracy, next_difficulty, old_difficulty)
        }
        
        serializer = AssessmentResultSerializer(data=result_data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
    
    def _update_concept_mastery(self, assessment, answers, topic):
        """Update concept mastery based on answers"""
        concept_stats = {}
        
        for answer in answers:
            concept = answer.question.concept
            if concept not in concept_stats:
                concept_stats[concept] = {'total': 0, 'correct': 0}
            concept_stats[concept]['total'] += 1
            if answer.is_correct:
                concept_stats[concept]['correct'] += 1
        
        for concept_name, stats in concept_stats.items():
            mastery, _ = ConceptMastery.objects.get_or_create(
                user=self.request.user,
                topic=topic,
                concept_name=concept_name
            )
            
            mastery.total_questions += stats['total']
            mastery.correct_answers += stats['correct']
            mastery.accuracy = (mastery.correct_answers / mastery.total_questions * 100)
            mastery.mastery_level = min(1.0, mastery.accuracy / 100)
            mastery.last_practiced_at = timezone.now()
            
            # Schedule revision for weak concepts
            if mastery.accuracy < 70:
                mastery.next_review_date = timezone.now() + timedelta(days=1)
                mastery.review_interval_days = 1
            else:
                mastery.next_review_date = timezone.now() + timedelta(days=3)
                mastery.review_interval_days = 3
            
            mastery.save()
    
    def _predict_next_difficulty(self, progress, topic):
        """Use ML model to predict next difficulty"""
        user_data = {
            'accuracy': progress.average_accuracy,
            'avg_time_per_question': progress.average_time_per_question,
            'first_attempt_correct': progress.first_attempt_correct_rate,
            'current_difficulty': topic.current_difficulty,
            'sessions_completed': topic.sessions_completed,
            'score_trend': progress.score_trend,
            'mastery_level': topic.mastery_level,
            'is_new_topic': 1 if topic.sessions_completed == 0 else 0
        }
        
        return predict_next_difficulty(user_data)
    
    def _generate_feedback(self, accuracy, next_difficulty, old_difficulty):
        """Generate feedback message"""
        if accuracy >= 85:
            if next_difficulty > old_difficulty:
                return "Excellent work! You're ready for harder challenges."
            return "Great job! Keep up the excellent performance."
        elif accuracy >= 70:
            return "Good progress! Keep practicing to improve further."
        elif accuracy >= 50:
            return "You're getting there. Review the weak concepts and try again."
        else:
            return "Don't worry! Let's review the basics and build your foundation."


class MonitoringViewSet(viewsets.ModelViewSet):
    """Track user engagement during learning"""
    serializer_class = MonitoringSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MonitoringSession.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """Start a new monitoring session"""
        content_id = request.data.get('content_id')
        content = get_object_or_404(Content, id=content_id, topic__user=request.user)
        
        session = MonitoringSession.objects.create(
            user=request.user,
            content=content
        )
        
        return Response(MonitoringSessionSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def track_event(self, request, pk=None):
        """Track an engagement event"""
        session = self.get_object()
        event_type = request.data.get('event_type')
        event_data = request.data.get('data', {})
        
        # Add event to log
        event = {
            'timestamp': timezone.now().isoformat(),
            'type': event_type,
            'data': event_data
        }
        session.events.append(event)
        
        # Update metrics
        if event_type == 'tab_switch':
            session.tab_switches += 1
        elif event_type == 'focus_lost':
            session.focus_lost_count += 1
        elif event_type == 'time_update':
            session.total_time_seconds = event_data.get('total_time', 0)
            session.active_time_seconds = event_data.get('active_time', 0)
        
        session.save()
        
        return Response(MonitoringSessionSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """End a monitoring session"""
        session = self.get_object()
        session.ended_at = timezone.now()
        session.save()
        
        return Response(MonitoringSessionSerializer(session).data)


class ProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """View user progress"""
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get overall progress overview"""
        progress_data = UserProgress.objects.filter(user=request.user)
        
        overview = {
            'total_topics': progress_data.count(),
            'average_mastery': sum(p.mastery_level for p in progress_data) / progress_data.count() if progress_data.exists() else 0,
            'total_assessments': sum(p.total_assessments for p in progress_data),
            'average_accuracy': sum(p.average_accuracy for p in progress_data) / progress_data.count() if progress_data.exists() else 0,
        }
        
        return Response(overview)
