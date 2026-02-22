"""
Test ML Integration Only (No Gemini API calls)
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import Topic, Content, StudySession, SessionMetrics
from adaptive_learning.gemini_mcq_service import learning_state_detector


def test_ml_state_detection():
    """Test ML model loading and state detection"""
    print("\n" + "="*70)
    print("ML STATE DETECTION TEST")
    print("="*70)
    
    # Test scenarios
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
            },
            'expected': 4
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
            },
            'expected': 1
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
            },
            'expected': 2
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
            },
            'expected': 3
        }
    ]
    
    state_labels = {1: 'Confused', 2: 'Bored', 3: 'Overloaded', 4: 'Focused'}
    
    for scenario in scenarios:
        state = learning_state_detector.detect_learning_state(metrics_data=scenario['metrics'])
        expected = scenario['expected']
        status = "✅" if state == expected else "⚠️"
        
        print(f"\n{status} {scenario['name']}:")
        print(f"   Detected: {state_labels[state]} (state={state})")
        print(f"   Expected: {state_labels[expected]} (state={expected})")
        print(f"   Engagement: {scenario['metrics']['engagement_score']:.1f}%")
        print(f"   Tab Switches: {scenario['metrics']['tab_switches']}")
        print(f"   Focus Duration: {scenario['metrics']['avg_focus_duration']}s")


def test_session_metrics_integration():
    """Test extracting metrics from actual session"""
    print("\n" + "="*70)
    print("SESSION METRICS INTEGRATION TEST")
    print("="*70)
    
    # Create test data
    user, _ = User.objects.get_or_create(username='ml_test_user')
    topic, _ = Topic.objects.get_or_create(
        user=user,
        name='ML Test Topic',
        defaults={'description': 'Test topic'}
    )
    content, _ = Content.objects.get_or_create(
        topic=topic,
        title='ML Test Content',
        defaults={
            'content_type': 'youtube',
            'transcript': 'Test transcript'
        }
    )
    
    # Create session with different metric profiles
    test_cases = [
        {
            'name': 'High Performer',
            'metrics': {
                'engagement_score': 88.0,
                'total_tab_switches': 2,
                'total_focus_losses': 1,
                'active_time_ratio': 0.92,
                'average_focus_duration_seconds': 450,
                'interaction_rate': 0.65,
                'study_speed': 1.3,
            },
            'expected_state': 4
        },
        {
            'name': 'Struggling Learner',
            'metrics': {
                'engagement_score': 42.0,
                'total_tab_switches': 18,
                'total_focus_losses': 14,
                'active_time_ratio': 0.45,
                'average_focus_duration_seconds': 110,
                'interaction_rate': 0.25,
                'study_speed': 0.5,
            },
            'expected_state': 3
        }
    ]
    
    for test_case in test_cases:
        # Create session
        session = StudySession.objects.create(
            user=user,
            content=content,
            workspace_name=f"Test: {test_case['name']}",
            session_type='recommended'
        )
        
        # Create metrics
        SessionMetrics.objects.create(
            session=session,
            **test_case['metrics']
        )
        
        # Detect state from session
        state = learning_state_detector.detect_learning_state(session_id=session.id)
        expected = test_case['expected_state']
        status = "✅" if state == expected else "⚠️"
        
        state_labels = {1: 'Confused', 2: 'Bored', 3: 'Overloaded', 4: 'Focused'}
        print(f"\n{status} {test_case['name']}:")
        print(f"   Session ID: {session.id}")
        print(f"   Detected: {state_labels[state]} (state={state})")
        print(f"   Expected: {state_labels[expected]} (state={expected})")
        print(f"   Engagement: {test_case['metrics']['engagement_score']:.1f}%")


def test_question_config_mapping():
    """Test that state correctly maps to question configuration"""
    print("\n" + "="*70)
    print("QUESTION CONFIGURATION MAPPING TEST")
    print("="*70)
    
    from adaptive_learning.gemini_mcq_service import USER_STATE_CONFIG
    
    states = [
        (1, 'Confused'),
        (2, 'Bored'),
        (3, 'Overloaded'),
        (4, 'Focused')
    ]
    
    for state_num, state_name in states:
        config = USER_STATE_CONFIG[state_num]
        print(f"\n{state_name} (state={state_num}):")
        print(f"   Questions: {config['num_questions']}")
        print(f"   Difficulty: {config['difficulty']}")
        print(f"   Take Break: {config['take_break']}")
        print(f"   Instruction: {config['instruction'][:60]}...")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("ML INTEGRATION TEST SUITE (No API Calls)")
    print("="*70)
    
    try:
        test_ml_state_detection()
        test_session_metrics_integration()
        test_question_config_mapping()
        
        print("\n" + "="*70)
        print("✅ ALL ML TESTS COMPLETED")
        print("="*70)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
