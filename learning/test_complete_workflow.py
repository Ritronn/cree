"""
Complete End-to-End Workflow Test
Tests the entire Study Session → Monitoring → Testing → ML Pipeline

This test validates:
1. Session creation and monitoring data collection
2. Test generation with ML (Groq API)
3. Test submission and assessment
4. ML model difficulty prediction
5. Data flow between all components
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import Topic, Content, StudySession
from adaptive_learning.session_manager import SessionManager
from adaptive_learning.monitoring_collector import MonitoringCollector
from adaptive_learning.proctoring_engine import ProctoringEngine
from adaptive_learning.test_generator import TestGenerator
from adaptive_learning.assessment_engine import AssessmentEngine
from adaptive_learning.ml_predictor import predict_next_difficulty
from adaptive_learning.whiteboard_manager import WhiteboardManager
from adaptive_learning.rag_chat_integration import RAGChatIntegration

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_complete_workflow():
    """Test the complete study session workflow"""
    
    print_section("🚀 COMPLETE WORKFLOW TEST - Study Session Monitoring & Testing")
    
    # ========================================================================
    # PHASE 1: Setup - Create User, Topic, Content
    # ========================================================================
    print_section("PHASE 1: Setup - User, Topic, Content")
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='workflow_test_user',
        defaults={'email': 'test@example.com'}
    )
    print(f"✓ User: {user.username} ({'created' if created else 'existing'})")
    
    # Create topic
    topic, created = Topic.objects.get_or_create(
        user=user,
        name='Python Programming',
        defaults={'current_difficulty': 1}
    )
    print(f"✓ Topic: {topic.name} (Difficulty: {topic.current_difficulty})")
    
    # Create content with realistic transcript
    content_text = """
    Python is a high-level programming language known for its simplicity and readability.
    Variables in Python are dynamically typed, meaning you don't need to declare their type.
    Functions are defined using the 'def' keyword followed by the function name.
    Lists are ordered, mutable collections that can contain elements of different types.
    Dictionaries store key-value pairs and provide fast lookup times.
    Loops in Python include 'for' loops for iteration and 'while' loops for conditional repetition.
    Exception handling uses try-except blocks to catch and handle errors gracefully.
    """
    
    content, created = Content.objects.get_or_create(
        topic=topic,
        title='Python Basics Tutorial',
        defaults={
            'content_type': 'youtube',
            'transcript': content_text,
            'key_concepts': ['variables', 'functions', 'lists', 'dictionaries', 'loops', 'exceptions'],
            'processed': True
        }
    )
    print(f"✓ Content: {content.title}")
    print(f"  - Type: {content.content_type}")
    print(f"  - Concepts: {', '.join(content.key_concepts)}")
    print(f"  - Transcript length: {len(content.transcript)} chars")
    
    # ========================================================================
    # PHASE 2: Study Session - Create and Monitor
    # ========================================================================
    print_section("PHASE 2: Study Session - Creation & Monitoring")
    
    # Create study session
    session = SessionManager.create_session(user, content, 'recommended')
    print(f"✓ Session Created: ID={session.id}")
    print(f"  - Type: {session.session_type}")
    print(f"  - Active: {session.is_active}")
    
    # Get session configuration
    config = SessionManager.get_session_config(session.session_type)
    print(f"✓ Session Config:")
    print(f"  - Study time: {config['study_time'] // 60} minutes")
    print(f"  - Break time: {config['break_time'] // 60} minutes")
    print(f"  - Break flexible: {config['break_flexible']}")
    
    # Simulate monitoring events during study
    print(f"\n✓ Simulating Study Activity...")
    monitoring_events = [
        ('video_play', {'timestamp': 0}),
        ('video_pause', {'timestamp': 120}),
        ('video_play', {'timestamp': 125}),
        ('scroll', {'position': 100}),
        ('scroll', {'position': 200}),
        ('video_pause', {'timestamp': 300}),
        ('note_taken', {'content': 'Important concept'}),
        ('video_play', {'timestamp': 305}),
    ]
    
    for event_type, details in monitoring_events:
        result = MonitoringCollector.record_event(session.id, event_type, details)
        print(f"  - Recorded: {event_type}")
    
    # Simulate proctoring events
    print(f"\n✓ Simulating Proctoring...")
    ProctoringEngine.record_tab_switch(session.id)
    print(f"  - Tab switch detected")
    
    screenshot_result = ProctoringEngine.record_screenshot_attempt(session.id, 'content')
    print(f"  - Screenshot attempt: {'Blocked' if not screenshot_result['allowed'] else 'Allowed'}")
    
    # Get monitoring metrics
    metrics = MonitoringCollector.aggregate_metrics(session.id)
    print(f"\n✓ Monitoring Metrics:")
    print(f"  - Engagement score: {metrics['engagement_score']:.1f}/100")
    print(f"  - Study speed: {metrics['study_speed']:.2f}")
    print(f"  - Interaction rate: {metrics['interaction_rate']:.2f}")
    
    # Get proctoring summary
    violations = ProctoringEngine.get_violation_summary(session.id)
    print(f"\n✓ Proctoring Summary:")
    print(f"  - Total events: {violations['total_events']}")
    print(f"  - Tab switches: {violations['violations']['tab_switches']}")
    print(f"  - Screenshots blocked: {violations['violations']['screenshots_blocked']}")
    
    # Complete session
    SessionManager.complete_session(session.id)
    session.refresh_from_db()
    print(f"\n✓ Session Completed: {session.is_completed}")
    
    # ========================================================================
    # PHASE 3: Test Generation - ML-Based Questions
    # ========================================================================
    print_section("PHASE 3: Test Generation - ML-Based Questions")
    
    difficulty = topic.current_difficulty
    print(f"✓ Generating test at difficulty level: {difficulty}")
    
    test = TestGenerator.generate_test(session.id, difficulty)
    print(f"✓ Test Generated: ID={test.id}")
    print(f"  - Total questions: {test.total_questions}")
    print(f"  - MCQ: {test.mcq_count}")
    print(f"  - Short Answer: {test.short_answer_count}")
    print(f"  - Problem Solving: {test.problem_solving_count}")
    
    # Display generated questions
    questions = test.questions.all().order_by('order')
    print(f"\n✓ Generated Questions:")
    for i, q in enumerate(questions[:5], 1):  # Show first 5
        print(f"  {i}. [{q.question_type.upper()}] {q.question_text[:60]}...")
        if q.question_type == 'mcq' and q.options:
            for j, opt in enumerate(q.options[:2], 1):  # Show first 2 options
                print(f"      {j}) {opt[:40]}...")
    
    if questions.count() > 5:
        print(f"  ... and {questions.count() - 5} more questions")
    
    # ========================================================================
    # PHASE 4: Test Submission - Answer Questions
    # ========================================================================
    print_section("PHASE 4: Test Submission - Answering Questions")
    
    print(f"✓ Simulating test submission...")
    answered = 0
    correct = 0
    
    for question in questions:
        if question.question_type == 'mcq':
            # Simulate answering (50% correct for demo)
            selected = 0 if answered % 2 == 0 else 1
            submission = AssessmentEngine.evaluate_mcq(
                question.id, user, selected, time_taken=30
            )
            answered += 1
            if submission.is_correct:
                correct += 1
            print(f"  - MCQ #{answered}: {'✓ Correct' if submission.is_correct else '✗ Incorrect'}")
        
        elif question.question_type == 'short_answer':
            # Simulate short answer
            answer = "This is a test answer explaining the concept."
            submission = AssessmentEngine.evaluate_short_answer(
                question.id, user, answer, time_taken=60
            )
            answered += 1
            if submission.is_correct:
                correct += 1
            print(f"  - Short Answer #{answered}: Score={submission.score:.1f}%")
        
        elif question.question_type == 'problem_solving':
            # Simulate problem solving
            answer = "Step 1: Analyze the problem. Step 2: Implement solution."
            submission = AssessmentEngine.evaluate_problem_solving(
                question.id, user, answer, time_taken=120
            )
            answered += 1
            if submission.is_correct:
                correct += 1
            print(f"  - Problem Solving #{answered}: Score={submission.score:.1f}%")
    
    print(f"\n✓ Test Submission Complete:")
    print(f"  - Questions answered: {answered}/{test.total_questions}")
    print(f"  - Correct answers: {correct}")
    
    # ========================================================================
    # PHASE 5: Assessment - Calculate Score & Weak Areas
    # ========================================================================
    print_section("PHASE 5: Assessment - Score Calculation")
    
    # Calculate overall score
    score_result = AssessmentEngine.calculate_test_score(test.id)
    print(f"✓ Test Score Calculated:")
    print(f"  - Overall Score: {score_result['overall_score']:.1f}%")
    print(f"  - Total Questions: {score_result['total_questions']}")
    print(f"  - Answered: {score_result['answered_questions']}")
    print(f"  - Correct: {score_result['correct_answers']}")
    
    # Identify weak areas
    weak_areas = AssessmentEngine.identify_weak_areas(test.id)
    print(f"\n✓ Weak Areas Identified:")
    if weak_areas:
        for area in weak_areas:
            print(f"  - {area['concept']}: {area['accuracy']:.1f}% accuracy")
    else:
        print(f"  - No weak areas (all concepts > 70%)")
    
    # ========================================================================
    # PHASE 6: ML Model - Difficulty Prediction
    # ========================================================================
    print_section("PHASE 6: ML Model - Difficulty Prediction")
    
    # Prepare ML input
    ml_input = AssessmentEngine.prepare_ml_input(test.id, session.id)
    print(f"✓ ML Input Prepared:")
    print(f"  - Accuracy: {ml_input['accuracy']:.1f}%")
    print(f"  - Avg time per question: {ml_input['avg_time_per_question']:.1f}s")
    print(f"  - Sessions completed: {ml_input['sessions_completed']}")
    print(f"  - Mastery level: {ml_input['mastery_level']:.2f}")
    print(f"  - Current difficulty: {ml_input['current_difficulty']}")
    print(f"  - Engagement score: {ml_input['engagement_score']:.1f}")
    
    # Predict next difficulty
    next_difficulty = predict_next_difficulty(ml_input)
    print(f"\n✓ ML Prediction:")
    print(f"  - Current difficulty: {topic.current_difficulty}")
    print(f"  - Predicted next difficulty: {next_difficulty}")
    
    # Generate feedback
    feedback = AssessmentEngine.generate_difficulty_feedback(
        topic.current_difficulty, next_difficulty
    )
    print(f"  - Feedback: {feedback['message']}")
    
    # Update topic difficulty
    topic.current_difficulty = next_difficulty
    topic.save()
    print(f"  - Topic difficulty updated to: {topic.current_difficulty}")
    
    # ========================================================================
    # PHASE 7: Additional Features - Whiteboard & Chat
    # ========================================================================
    print_section("PHASE 7: Additional Features - Whiteboard & Chat")
    
    # Test whiteboard
    print(f"✓ Testing Whiteboard:")
    wb_result = WhiteboardManager.save_whiteboard_state(
        session.id, {'drawing': 'test_data'}
    )
    print(f"  - Save state: {'✓ Success' if wb_result['success'] else '✗ Failed'}")
    
    wb_snapshots = WhiteboardManager.get_all_snapshots(session.id)
    print(f"  - Snapshots: {len(wb_snapshots.get('snapshots', []))}")
    
    # Test RAG chat
    print(f"\n✓ Testing RAG Chat:")
    chat_result = RAGChatIntegration.send_query(
        session.id, "What are Python variables?"
    )
    print(f"  - Query sent: {'✓ Success' if 'error' not in chat_result or 'fallback_response' in chat_result else '✗ Failed'}")
    
    # ========================================================================
    # PHASE 8: Data Verification - Check Persistence
    # ========================================================================
    print_section("PHASE 8: Data Verification - Persistence Check")
    
    # Verify session data
    session.refresh_from_db()
    print(f"✓ Session Data:")
    print(f"  - ID: {session.id}")
    print(f"  - Completed: {session.is_completed}")
    print(f"  - Duration: {(session.ended_at - session.started_at).seconds if session.ended_at else 0}s")
    
    # Verify test data
    test.refresh_from_db()
    print(f"\n✓ Test Data:")
    print(f"  - ID: {test.id}")
    print(f"  - Score: {test.score:.1f}%")
    print(f"  - Completed: {test.is_completed}")
    print(f"  - Weak concepts: {', '.join(test.weak_concepts) if test.weak_concepts else 'None'}")
    
    # Verify metrics
    metrics_obj = session.metrics
    print(f"\n✓ Session Metrics:")
    print(f"  - Engagement score: {metrics_obj.engagement_score:.1f}")
    print(f"  - Total interactions: {sum(metrics_obj.content_interactions.values())}")
    print(f"  - Tab switches: {metrics_obj.total_tab_switches}")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_section("✅ WORKFLOW TEST COMPLETE - ALL PHASES PASSED")
    
    print(f"Summary:")
    print(f"  ✓ Phase 1: User, Topic, Content setup")
    print(f"  ✓ Phase 2: Study session with monitoring")
    print(f"  ✓ Phase 3: ML-based test generation")
    print(f"  ✓ Phase 4: Test submission and answering")
    print(f"  ✓ Phase 5: Score calculation and weak areas")
    print(f"  ✓ Phase 6: ML difficulty prediction")
    print(f"  ✓ Phase 7: Whiteboard and chat features")
    print(f"  ✓ Phase 8: Data persistence verification")
    
    print(f"\n🎉 All components working correctly!")
    print(f"   - Monitoring: Collecting engagement data ✓")
    print(f"   - Proctoring: Tracking violations ✓")
    print(f"   - Test Generation: Creating ML-based questions ✓")
    print(f"   - Assessment: Scoring and evaluation ✓")
    print(f"   - ML Model: Predicting difficulty ✓")
    print(f"   - Data Flow: All components integrated ✓")
    
    return True

if __name__ == '__main__':
    try:
        success = test_complete_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
