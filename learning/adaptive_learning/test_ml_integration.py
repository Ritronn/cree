"""
Test ML Integration with Gemini MCQ Service
Demonstrates the full workflow from session monitoring to adaptive question generation
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import Topic, Content, StudySession, SessionMetrics
from adaptive_learning.gemini_mcq_service import (
    learning_state_detector,
    create_assessment_from_session,
    create_test_from_session,
    generate_adaptive_questions_for_user,
    update_user_progress_from_assessment
)


def test_learning_state_detection():
    """Test learning state detection with different metrics"""
    print("\n" + "="*70)
    print("TEST 1: Learning State Detection")
    print("="*70)
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'Focused Student',
            'metrics': {
                'engagement_score': 85.0,
                'tab_switches': 3,
                'focus_losses': 2,
                'active_time_ratio': 0.9,
                'avg_focus_duration': 400,
                'interaction_rate': 0.6,
                'study_speed': 1.2,
            }
        },
        {
            'name': 'Confused Student',
            'metrics': {
                'engagement_score': 45.0,
                'tab_switches': 8,
                'focus_losses': 12,
                'active_time_ratio': 0.5,
                'avg_focus_duration': 150,
                'interaction_rate': 0.3,
                'study_speed': 0.6,
            }
        },
        {
            'name': 'Bored Student',
            'metrics': {
                'engagement_score': 75.0,
                'tab_switches': 10,
                'focus_losses': 6,
                'active_time_ratio': 0.7,
                'avg_focus_duration': 160,
                'interaction_rate': 0.4,
                'study_speed': 1.8,
            }
        },
        {
            'name': 'Overloaded Student',
            'metrics': {
                'engagement_score': 55.0,
                'tab_switches': 20,
                'focus_losses': 15,
                'active_time_ratio': 0.4,
                'avg_focus_duration': 90,
                'interaction_rate': 0.2,
                'study_speed': 0.4,
            }
        }
    ]
    
    for scenario in scenarios:
        state = learning_state_detector.detect_learning_state(metrics_data=scenario['metrics'])
        state_labels = {1: 'Confused', 2: 'Bored', 3: 'Overloaded', 4: 'Focused'}
        print(f"\n{scenario['name']}:")
        print(f"  Detected State: {state_labels[state]} (state={state})")
        print(f"  Engagement: {scenario['metrics']['engagement_score']:.1f}%")
        print(f"  Tab Switches: {scenario['metrics']['tab_switches']}")
        print(f"  Focus Duration: {scenario['metrics']['avg_focus_duration']}s")


def test_adaptive_question_generation():
    """Test question generation for different learning states"""
    print("\n" + "="*70)
    print("TEST 2: Adaptive Question Generation")
    print("="*70)
    
    sample_transcript = """
    Python functions are reusable blocks of code that perform specific tasks.
    They are defined using the 'def' keyword followed by the function name and parentheses.
    Functions can accept parameters and return values using the 'return' statement.
    
    For example:
    def greet(name):
        return f"Hello, {name}!"
    
    Lambda functions are anonymous functions defined using the 'lambda' keyword.
    They are useful for short, simple operations.
    
    Example: square = lambda x: x ** 2
    
    Decorators are a powerful feature that allows you to modify function behavior.
    They use the @ symbol and are placed above function definitions.
    """
    
    from adaptive_learning.gemini_mcq_service import process_content_and_generate_mcqs
    
    states = [
        (1, 'Confused'),
        (2, 'Bored'),
        (3, 'Overloaded'),
        (4, 'Focused')
    ]
    
    for state_num, state_name in states:
        print(f"\n--- {state_name} State (state={state_num}) ---")
        result = process_content_and_generate_mcqs(sample_transcript, state_num)
        
        if result.get('success'):
            print(f"✅ Generated {result['num_questions']} questions")
            print(f"   Difficulty: {result['difficulty']}")
            print(f"   Take Break: {result['take_break_suggestion']}")
            print(f"\n   Sample Question:")
            if result['questions']:
                q = result['questions'][0]
                print(f"   Q: {q['question'][:80]}...")
                print(f"   Answer: {q['answer']}")
        else:
            print(f"❌ Failed: {result.get('error')}")


def test_full_workflow_with_models():
    """Test complete workflow with Django models"""
    print("\n" + "="*70)
    print("TEST 3: Full Workflow with Django Models")
    print("="*70)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='test_student',
        defaults={'email': 'test@example.com'}
    )
    print(f"\n{'Created' if created else 'Using existing'} user: {user.username}")
    
    # Get or create topic
    topic, created = Topic.objects.get_or_create(
        user=user,
        name='Python Programming',
        defaults={
            'description': 'Learn Python fundamentals',
            'current_difficulty': 1,
            'mastery_level': 0.0
        }
    )
    print(f"{'Created' if created else 'Using existing'} topic: {topic.name}")
    
    # Create content with transcript
    content, created = Content.objects.get_or_create(
        topic=topic,
        title='Python Functions Tutorial',
        defaults={
            'content_type': 'youtube',
            'url': 'https://youtube.com/example',
            'transcript': """
            Python functions are essential building blocks of any program.
            They allow you to organize code into reusable pieces.
            
            To define a function, use the 'def' keyword:
            def my_function():
                print("Hello!")
            
            Functions can take parameters:
            def greet(name):
                return f"Hello, {name}!"
            
            You can also use default parameters:
            def greet(name="World"):
                return f"Hello, {name}!"
            
            Lambda functions provide a shorthand for simple functions:
            square = lambda x: x ** 2
            
            Decorators modify function behavior:
            @timer
            def slow_function():
                time.sleep(1)
            """,
            'processed': True
        }
    )
    print(f"{'Created' if created else 'Using existing'} content: {content.title}")
    
    # Create study session with metrics
    session, created = StudySession.objects.get_or_create(
        user=user,
        content=content,
        workspace_name='Python Functions Study',
        defaults={
            'session_type': 'recommended',
            'is_active': False,
            'is_completed': True
        }
    )
    print(f"{'Created' if created else 'Using existing'} session: {session.workspace_name}")
    
    # Create or update session metrics (simulating a focused student)
    metrics, created = SessionMetrics.objects.get_or_create(
        session=session,
        defaults={
            'engagement_score': 82.0,
            'total_tab_switches': 4,
            'total_focus_losses': 2,
            'active_time_ratio': 0.85,
            'average_focus_duration_seconds': 380,
            'interaction_rate': 0.55,
            'study_speed': 1.1,
            'total_active_time_seconds': 3600,
            'chat_queries_count': 3,
        }
    )
    print(f"Session metrics: Engagement={metrics.engagement_score:.1f}%")
    
    # Generate adaptive assessment
    print("\n--- Generating Adaptive Assessment ---")
    try:
        assessment = create_assessment_from_session(session.id, user, content)
        print(f"✅ Created assessment with {assessment.total_questions} questions")
        print(f"   Difficulty Level: {assessment.difficulty_level}")
        print(f"   Questions: {assessment.questions.count()}")
        
        # Show sample questions
        print("\n   Sample Questions:")
        for q in assessment.questions.all()[:3]:
            print(f"\n   Q{q.order + 1}: {q.question_text[:70]}...")
            print(f"   Concept: {q.concept}")
            print(f"   Difficulty: {q.difficulty}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Generate test
    print("\n--- Generating Post-Session Test ---")
    try:
        test = create_test_from_session(session.id, user)
        print(f"✅ Created test with {test.total_questions} questions")
        print(f"   Time Limit: {test.time_limit_seconds}s ({test.time_limit_seconds // 60} minutes)")
        print(f"   MCQ Count: {test.mcq_count}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_weak_concept_detection():
    """Test weak concept prediction"""
    print("\n" + "="*70)
    print("TEST 4: Weak Concept Detection")
    print("="*70)
    
    try:
        user = User.objects.get(username='test_student')
        topic = Topic.objects.get(user=user, name='Python Programming')
        
        weak_concepts = learning_state_detector.predict_weak_concepts(user, topic)
        
        if weak_concepts:
            print(f"\nFound {len(weak_concepts)} weak concepts:")
            for wc in weak_concepts:
                print(f"  - {wc['concept']}: {wc['mastery']:.2f} mastery, {wc['accuracy']:.1f}% accuracy")
        else:
            print("\nNo weak concepts found (or no data yet)")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("ML INTEGRATION TEST SUITE")
    print("="*70)
    
    try:
        test_learning_state_detection()
        test_adaptive_question_generation()
        test_full_workflow_with_models()
        test_weak_concept_detection()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
