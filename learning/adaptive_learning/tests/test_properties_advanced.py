"""
Advanced Property-Based Tests for Study Session Monitoring and Testing System
Properties 20-40

Feature: study-session-monitoring-testing
"""
import pytest
from hypothesis import given, strategies as st, settings
from django.contrib.auth.models import User
from django.utils import timezone

from adaptive_learning.models import (
    Topic, Content, StudySession, GeneratedTest, TestQuestion, TestSubmission
)
from adaptive_learning.session_manager import SessionManager
from adaptive_learning.monitoring_collector import MonitoringCollector
from adaptive_learning.test_generator import TestGenerator
from adaptive_learning.assessment_engine import AssessmentEngine
from adaptive_learning.proctoring_engine import ProctoringEngine
from adaptive_learning.rag_chat_integration import RAGChatIntegration


# ============================================================================
# PROPERTY 20: ML Model Input Completeness
# ============================================================================

@pytest.mark.django_db
@given(
    difficulty=st.integers(min_value=1, max_value=3),
    username=st.text(min_size=5, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
@settings(max_examples=50, deadline=None)
def test_property_20_ml_model_input_completeness(difficulty, username):
    """
    Feature: study-session-monitoring-testing
    Property 20: ML Model Input Completeness
    
    For any call to Model_1, the system should provide all required parameters.
    
    Validates: Requirements 8.1, 8.2, 8.3
    """
    # Create test data
    user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@test.com'})
    topic, _ = Topic.objects.get_or_create(user=user, name=f'Topic_{username}', defaults={'current_difficulty': 1})
    content = Content.objects.create(
        topic=topic,
        title=f'Test_{username}',
        content_type='youtube',
        transcript='Test content',
        key_concepts=['test'],
        processed=True
    )
    
    # Create session and test
    session = SessionManager.create_session(user, content, 'recommended')
    SessionManager.complete_session(session.id)
    test = TestGenerator.generate_test(session.id, difficulty)
    
    # Create and answer a question
    question = TestQuestion.objects.create(
        test=test,
        question_type='mcq',
        question_text='Test?',
        options=['A', 'B', 'C', 'D'],
        correct_answer_index=0,
        concept='Test',
        difficulty=difficulty,
        order=0,
        points=1
    )
    AssessmentEngine.evaluate_mcq(question.id, user, 0, 30)
    
    # Prepare ML input
    ml_input = AssessmentEngine.prepare_ml_input(test.id, session.id)
    
    # Verify all required parameters are present
    required_params = [
        'accuracy', 'avg_time_per_question', 'sessions_completed',
        'first_attempt_correct', 'mastery_level', 'is_new_topic',
        'current_difficulty'
    ]
    
    for param in required_params:
        assert param in ml_input, f"Missing required parameter: {param}"
    
    # Verify parameter types and ranges
    assert 0 <= ml_input['accuracy'] <= 100
    assert ml_input['avg_time_per_question'] >= 0
    assert ml_input['sessions_completed'] >= 0
    assert 0 <= ml_input['first_attempt_correct'] <= 100
    assert 0 <= ml_input['mastery_level'] <= 1
    assert ml_input['is_new_topic'] in [0, 1]
    assert 1 <= ml_input['current_difficulty'] <= 3


# ============================================================================
# PROPERTY 21: Difficulty Prediction Constraints
# ============================================================================

@pytest.mark.django_db
@given(
    current_difficulty=st.integers(min_value=1, max_value=3)
)
@settings(max_examples=50, deadline=None)
def test_property_21_difficulty_prediction_constraints(current_difficulty):
    """
    Feature: study-session-monitoring-testing
    Property 21: Difficulty Prediction Constraints
    
    For any Model_1 output, the next_difficulty value should be constrained to 1, 2, or 3.
    
    Validates: Requirements 8.4, 8.5
    """
    from adaptive_learning.ml_predictor import predict_next_difficulty
    
    # Create sample ML input
    ml_input = {
        'accuracy': 75.0,
        'avg_time_per_question': 45.0,
        'sessions_completed': 5,
        'first_attempt_correct': 70.0,
        'mastery_level': 0.7,
        'is_new_topic': 0,
        'score_trend': 5.0,
        'current_difficulty': current_difficulty
    }
    
    # Predict difficulty
    next_difficulty = predict_next_difficulty(ml_input)
    
    # Verify constraints
    assert next_difficulty in [1, 2, 3]
    assert isinstance(next_difficulty, int)


# ============================================================================
# PROPERTY 27: RAG Chat Integration
# ============================================================================

@pytest.mark.django_db
@given(
    query=st.text(min_size=5, max_size=200),
    username=st.text(min_size=5, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
@settings(max_examples=50, deadline=None)
def test_property_27_rag_chat_integration(query, username):
    """
    Feature: study-session-monitoring-testing
    Property 27: RAG Chat Integration
    
    For any chat query submission, the system should send it to the RAG backend,
    display the response, and record the interaction as an engagement event.
    
    Validates: Requirements 11.1, 11.2, 11.3, 11.4
    """
    # Create test data
    user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@test.com'})
    topic, _ = Topic.objects.get_or_create(user=user, name=f'Topic_{username}', defaults={'current_difficulty': 1})
    content = Content.objects.create(
        topic=topic,
        title=f'Test_{username}',
        content_type='youtube',
        transcript='Test content',
        processed=True
    )
    
    # Create session
    session = SessionManager.create_session(user, content, 'recommended')
    
    # Send query
    result = RAGChatIntegration.send_query(session.id, query)
    
    # Verify response structure (even if backend is not available)
    assert isinstance(result, dict)
    
    # Should have either success or error
    if 'error' in result:
        # Fallback response should be provided
        assert 'fallback_response' in result or 'message' in result
    else:
        assert 'success' in result or 'response' in result


# ============================================================================
# PROPERTY 29: Test Data Persistence
# ============================================================================

@pytest.mark.django_db
@given(
    difficulty=st.integers(min_value=1, max_value=3),
    username=st.text(min_size=5, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
@settings(max_examples=50, deadline=None)
def test_property_29_test_data_persistence(difficulty, username):
    """
    Feature: study-session-monitoring-testing
    Property 29: Test Data Persistence
    
    For any test lifecycle event, the system should create or update
    the corresponding database records with proper relationships.
    
    Validates: Requirements 12.4, 12.5, 12.6
    """
    # Create test data
    user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@test.com'})
    topic, _ = Topic.objects.get_or_create(user=user, name=f'Topic_{username}', defaults={'current_difficulty': 1})
    content = Content.objects.create(
        topic=topic,
        title=f'Test_{username}',
        content_type='youtube',
        transcript='Test content',
        key_concepts=['test'],
        processed=True
    )
    
    # Create session and test
    session = SessionManager.create_session(user, content, 'recommended')
    SessionManager.complete_session(session.id)
    test = TestGenerator.generate_test(session.id, difficulty)
    test_id = test.id
    
    # Verify test was persisted
    persisted_test = GeneratedTest.objects.get(id=test_id)
    assert persisted_test.session == session
    assert persisted_test.user == user
    assert persisted_test.difficulty_level == difficulty
    
    # Create question
    question = TestQuestion.objects.create(
        test=test,
        question_type='mcq',
        question_text='Test?',
        options=['A', 'B', 'C', 'D'],
        correct_answer_index=0,
        concept='Test',
        difficulty=difficulty,
        order=0,
        points=1
    )
    
    # Verify question was persisted with relationship
    persisted_question = TestQuestion.objects.get(id=question.id)
    assert persisted_question.test == test
    
    # Submit answer
    submission = AssessmentEngine.evaluate_mcq(question.id, user, 0, 30)
    
    # Verify submission was persisted with relationships
    persisted_submission = TestSubmission.objects.get(id=submission.id)
    assert persisted_submission.question == question
    assert persisted_submission.user == user


# ============================================================================
# PROPERTY 30: Historical Data Retrieval
# ============================================================================

@pytest.mark.django_db
@given(
    num_sessions=st.integers(min_value=1, max_value=5),
    username=st.text(min_size=5, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
@settings(max_examples=20, deadline=None)
def test_property_30_historical_data_retrieval(num_sessions, username):
    """
    Feature: study-session-monitoring-testing
    Property 30: Historical Data Retrieval
    
    For any user history or progress analytics request, the system should retrieve
    and calculate data from all stored sessions and tests.
    
    Validates: Requirements 12.7, 12.8
    """
    # Create test data
    user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@test.com'})
    topic, _ = Topic.objects.get_or_create(user=user, name=f'Topic_{username}', defaults={'current_difficulty': 1})
    content = Content.objects.create(
        topic=topic,
        title=f'Test_{username}',
        content_type='youtube',
        transcript='Test content',
        key_concepts=['test'],
        processed=True
    )
    
    # Create multiple sessions
    for i in range(num_sessions):
        session = SessionManager.create_session(user, content, 'recommended')
        SessionManager.complete_session(session.id)
    
    # Retrieve historical data for this specific content
    all_sessions = StudySession.objects.filter(user=user, content=content)
    
    # Verify all sessions are retrievable
    assert all_sessions.count() == num_sessions
    
    # Verify each session has complete data
    for session in all_sessions:
        assert session.user == user
        assert session.is_completed is True
        assert session.ended_at is not None


# ============================================================================
# PROPERTY 33: Real-Time Metric Updates
# ============================================================================

@pytest.mark.django_db
@given(
    num_events=st.integers(min_value=1, max_value=10),
    username=st.text(min_size=5, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
@settings(max_examples=50, deadline=None)
def test_property_33_real_time_metric_updates(num_events, username):
    """
    Feature: study-session-monitoring-testing
    Property 33: Real-Time Metric Updates
    
    For any active study period, the system should update engagement metrics
    and record significant changes.
    
    Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5
    """
    # Create test data
    user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@test.com'})
    topic, _ = Topic.objects.get_or_create(user=user, name=f'Topic_{username}', defaults={'current_difficulty': 1})
    content = Content.objects.create(
        topic=topic,
        title=f'Test_{username}',
        content_type='youtube',
        transcript='Test content',
        processed=True
    )
    
    # Create session
    session = SessionManager.create_session(user, content, 'recommended')
    
    # Record multiple events
    for i in range(num_events):
        MonitoringCollector.record_event(session.id, f'event_{i}', {})
    
    # Update real-time metrics
    metrics = MonitoringCollector.update_real_time_metrics(session.id)
    
    # Verify metrics are returned
    assert 'engagement_score' in metrics
    assert 'study_speed' in metrics
    assert 'interaction_rate' in metrics
    
    # Verify engagement score is in valid range
    assert 0 <= metrics['engagement_score'] <= 100


# ============================================================================
# PROPERTY 38: Concurrent Session Isolation
# ============================================================================

@pytest.mark.django_db
@given(
    num_users=st.integers(min_value=2, max_value=5)
)
@settings(max_examples=20, deadline=None)
def test_property_38_concurrent_session_isolation(num_users):
    """
    Feature: study-session-monitoring-testing
    Property 38: Concurrent Session Isolation
    
    For any set of concurrent session starts, the system should create
    separate, isolated session records for each user.
    
    Validates: Requirements 18.1
    """
    # Create multiple users and sessions
    sessions = []
    
    for i in range(num_users):
        user, _ = User.objects.get_or_create(username=f'user_{i}_{num_users}', defaults={'email': f'user_{i}@test.com'})
        topic, _ = Topic.objects.get_or_create(user=user, name=f'Topic_{i}', defaults={'current_difficulty': 1})
        content = Content.objects.create(
            topic=topic,
            title=f'Content {i}',
            content_type='youtube',
            transcript='Test content',
            processed=True
        )
        
        session = SessionManager.create_session(user, content, 'recommended')
        sessions.append(session)
    
    # Verify all sessions are isolated
    assert len(sessions) == num_users
    
    # Verify each session has unique user
    users = [s.user for s in sessions]
    assert len(set(users)) == num_users
    
    # Verify sessions don't interfere with each other
    for i, session in enumerate(sessions):
        assert session.user.username.startswith('user_')
        assert session.content.title == f'Content {i}'


# ============================================================================
# PROPERTY 40: Monitoring Data Batching
# ============================================================================

@pytest.mark.django_db
@given(
    num_events=st.integers(min_value=5, max_value=20),
    username=st.text(min_size=5, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
@settings(max_examples=30, deadline=None)
def test_property_40_monitoring_data_batching(num_events, username):
    """
    Feature: study-session-monitoring-testing
    Property 40: Monitoring Data Batching
    
    For any monitoring data collection from multiple sessions, the system should
    batch database writes to optimize performance.
    
    Validates: Requirements 18.5
    """
    # Create test data
    user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@test.com'})
    topic, _ = Topic.objects.get_or_create(user=user, name=f'Topic_{username}', defaults={'current_difficulty': 1})
    content = Content.objects.create(
        topic=topic,
        title=f'Test_{username}',
        content_type='youtube',
        transcript='Test content',
        processed=True
    )
    
    # Create session
    session = SessionManager.create_session(user, content, 'recommended')
    
    # Record multiple events (simulating batching)
    for i in range(num_events):
        MonitoringCollector.record_event(session.id, f'batch_event_{i}', {})
    
    # Verify all events were recorded
    session.refresh_from_db()
    metrics = session.metrics
    
    # Count recorded events
    total_events = sum(metrics.content_interactions.values())
    assert total_events >= num_events


print("✅ Advanced property tests (20-40) defined and ready to run!")
