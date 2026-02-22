"""
Test Full Integration: ML Model + Gemini API + Django Models
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import Topic, Content, StudySession, SessionMetrics
from adaptive_learning.gemini_mcq_service import (
    learning_state_detector,
    create_assessment_from_session,
    USER_STATE_CONFIG
)


def test_full_workflow():
    """Test complete workflow with real ML model and Gemini API"""
    print("\n" + "="*70)
    print("FULL INTEGRATION TEST: ML + Gemini + Django")
    print("="*70)
    
    # Create test user
    user, _ = User.objects.get_or_create(
        username='integration_test_user',
        defaults={'email': 'test@example.com'}
    )
    print(f"\n✅ User: {user.username}")
    
    # Create topic
    topic, _ = Topic.objects.get_or_create(
        user=user,
        name='Python Functions',
        defaults={'description': 'Learn Python functions'}
    )
    print(f"✅ Topic: {topic.name}")
    
    # Create content with transcript
    content, _ = Content.objects.get_or_create(
        topic=topic,
        title='Python Functions Basics',
        defaults={
            'content_type': 'youtube',
            'transcript': """
            Python functions are reusable blocks of code that perform specific tasks.
            They are defined using the 'def' keyword followed by the function name.
            
            Example:
            def greet(name):
                return f"Hello, {name}!"
            
            Functions can have parameters and return values.
            You can also use default parameters:
            def greet(name="World"):
                return f"Hello, {name}!"
            
            Lambda functions are anonymous functions:
            square = lambda x: x ** 2
            
            Decorators modify function behavior:
            @timer
            def slow_function():
                time.sleep(1)
            """,
            'processed': True
        }
    )
    print(f"✅ Content: {content.title}")
    
    # Test different session scenarios
    scenarios = [
        {
            'name': 'Focused Student',
            'metrics': {
                'engagement_score': 85.0,
                'total_tab_switches': 3,
                'total_focus_losses': 2,
                'active_time_ratio': 0.9,
                'average_focus_duration_seconds': 400,
                'interaction_rate': 0.6,
                'study_speed': 1.2,
            }
        },
        {
            'name': 'Struggling Student',
            'metrics': {
                'engagement_score': 45.0,
                'total_tab_switches': 15,
                'total_focus_losses': 12,
                'active_time_ratio': 0.5,
                'average_focus_duration_seconds': 120,
                'interaction_rate': 0.3,
                'study_speed': 0.6,
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{'='*70}")
        print(f"Scenario: {scenario['name']}")
        print(f"{'='*70}")
        
        # Create session
        session = StudySession.objects.create(
            user=user,
            content=content,
            workspace_name=f"Test: {scenario['name']}",
            session_type='recommended',
            is_completed=True
        )
        
        # Create metrics
        SessionMetrics.objects.create(
            session=session,
            **scenario['metrics']
        )
        
        print(f"\n📊 Session Metrics:")
        print(f"   Engagement: {scenario['metrics']['engagement_score']:.1f}%")
        print(f"   Tab Switches: {scenario['metrics']['total_tab_switches']}")
        print(f"   Focus Losses: {scenario['metrics']['total_focus_losses']}")
        
        # Detect learning state using ML model
        state = learning_state_detector.detect_learning_state(session_id=session.id)
        state_config = USER_STATE_CONFIG[state]
        
        print(f"\n🤖 ML Detected State: {state_config['label'].upper()} (state={state})")
        print(f"   Will generate: {state_config['num_questions']} questions")
        print(f"   Difficulty: {state_config['difficulty']}")
        print(f"   Take break: {state_config['take_break']}")
        
        # Generate assessment with Gemini
        print(f"\n🔮 Generating adaptive questions with Gemini...")
        try:
            assessment = create_assessment_from_session(session.id, user, content)
            
            print(f"✅ Assessment created!")
            print(f"   ID: {assessment.id}")
            print(f"   Total questions: {assessment.total_questions}")
            print(f"   Difficulty level: {assessment.difficulty_level}")
            
            # Show sample questions
            questions = assessment.questions.all()[:3]
            print(f"\n📝 Sample Questions:")
            for q in questions:
                print(f"\n   Q{q.order + 1}: {q.question_text[:70]}...")
                print(f"   Concept: {q.concept}")
                print(f"   Correct answer: {q.options[q.correct_answer_index][:50]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    test_full_workflow()
    print("\n" + "="*70)
    print("✅ INTEGRATION TEST COMPLETE")
    print("="*70)
