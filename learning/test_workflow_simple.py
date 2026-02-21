import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import Topic, Content
from adaptive_learning.session_manager import SessionManager
from adaptive_learning.monitoring_collector import MonitoringCollector
from adaptive_learning.test_generator import TestGenerator
from adaptive_learning.assessment_engine import AssessmentEngine
from adaptive_learning.ml_predictor import predict_next_difficulty

print('='*80)
print('INTEGRATION TEST - Study Session Workflow')
print('='*80)

# Phase 1: Setup
print('\nPhase 1: Setup')
user, _ = User.objects.get_or_create(username='workflow_test', defaults={'email': 'test@test.com'})
topic, _ = Topic.objects.get_or_create(user=user, name='Python', defaults={'current_difficulty': 1})
content, _ = Content.objects.get_or_create(
    topic=topic, title='Python Tutorial',
    defaults={'content_type': 'youtube', 'transcript': 'Python tutorial content', 'key_concepts': ['variables'], 'processed': True}
)
print(f'User: {user.username}, Topic: {topic.name}, Content: {content.title}')

# Phase 2: Session
print('\nPhase 2: Study Session')
session = SessionManager.create_session(user, content, 'recommended')
print(f'Session ID: {session.id}, Active: {session.is_active}')

# Record monitoring
MonitoringCollector.record_event(session.id, 'video_play', {'timestamp': 0})
MonitoringCollector.record_event(session.id, 'video_pause', {'timestamp': 120})
metrics = MonitoringCollector.aggregate_metrics(session.id)
print(f'Engagement: {metrics['engagement_score']:.1f}')

SessionManager.complete_session(session.id)
print('Session completed')

# Phase 3: Test Generation
print('\nPhase 3: Test Generation')
test = TestGenerator.generate_test(session.id, topic.current_difficulty)
print(f'Test ID: {test.id}, Questions: {test.total_questions}')

# Phase 4: Answer questions
print('\nPhase 4: Answering Questions')
questions = test.questions.all()
for i, q in enumerate(questions):
    if q.question_type == 'mcq':
        AssessmentEngine.evaluate_mcq(q.id, user, 0, 30)
    elif q.question_type == 'short_answer':
        AssessmentEngine.evaluate_short_answer(q.id, user, 'Test answer', 60)
    elif q.question_type == 'problem_solving':
        AssessmentEngine.evaluate_problem_solving(q.id, user, 'Solution', 120)
print(f'Answered {questions.count()} questions')

# Phase 5: Assessment
print('\nPhase 5: Assessment')
score = AssessmentEngine.calculate_test_score(test.id)
print(f'Score: {score['overall_score']:.1f}%')

# Phase 6: ML Prediction
print('\nPhase 6: ML Prediction')
ml_input = AssessmentEngine.prepare_ml_input(test.id, session.id)
print(f'ML Input - Accuracy: {ml_input['accuracy']:.1f}%, Engagement: {ml_input['engagement_score']:.1f}')
next_diff = predict_next_difficulty(ml_input)
print(f'Current difficulty: {topic.current_difficulty}, Predicted: {next_diff}')

print('\n' + '='*80)
print('✅ ALL PHASES COMPLETED SUCCESSFULLY')
print('='*80)
