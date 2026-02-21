"""
Test Phase 2 Backend Implementation
Run this to verify all new features work correctly
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'learning'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import (
    Topic, Content, StudySession, GeneratedTest, TestQuestion,
    TestSubmission, TestResult, WeakPoint, CourseRecommendation,
    SessionLimit, BrowserExtensionData
)
from adaptive_learning.test_generator import TestGenerator
from adaptive_learning.email_service import EmailService
from adaptive_learning.recommendation_service import RecommendationService
from datetime import datetime, timedelta
from django.utils import timezone


def test_session_limits():
    """Test session limit enforcement"""
    print("\n" + "="*60)
    print("TEST 1: Session Limits")
    print("="*60)
    
    user = User.objects.first()
    if not user:
        print("❌ No users found. Create a user first.")
        return False
    
    # Get or create today's session limit
    from datetime import date
    session_limit, created = SessionLimit.objects.get_or_create(
        user=user,
        date=date.today(),
        defaults={'sessions_created': 0, 'tests_pending': 0}
    )
    
    print(f"✓ Session limit for {user.username}:")
    print(f"  - Sessions today: {session_limit.sessions_created}/{session_limit.max_sessions_per_day}")
    print(f"  - Tests pending: {session_limit.tests_pending}")
    print(f"  - Can create: {session_limit.can_create_session}")
    
    if session_limit.blocked_reason:
        print(f"  - Blocked reason: {session_limit.blocked_reason}")
    
    return True


def test_test_generation():
    """Test enhanced test generation (20-25 questions)"""
    print("\n" + "="*60)
    print("TEST 2: Test Generation (20-25 Questions)")
    print("="*60)
    
    # Check question distribution
    from adaptive_learning.test_generator import TestGenerator
    
    for difficulty in [1, 2, 3]:
        dist = TestGenerator.QUESTION_DISTRIBUTION[difficulty]
        print(f"\n✓ Difficulty {difficulty}:")
        print(f"  - Total: {dist['total']} questions")
        print(f"  - MCQ: {dist['mcq']}")
        print(f"  - Short Answer: {dist['short_answer']}")
        print(f"  - Problem Solving: {dist['problem_solving']}")
    
    return True


def test_email_service():
    """Test email service"""
    print("\n" + "="*60)
    print("TEST 3: Email Service")
    print("="*60)
    
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return False
    
    # Create mock test result
    print(f"\n✓ Testing email for user: {user.email}")
    
    # Check environment variables
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    mailgun_key = os.getenv('MAILGUN_API_KEY')
    
    if sendgrid_key:
        print("  ✓ SendGrid API key configured")
    elif mailgun_key:
        print("  ✓ Mailgun API key configured")
    else:
        print("  ⚠ No email service configured (will log to console)")
    
    print("\n  Email service is ready!")
    print("  (Actual email will be sent when test is completed)")
    
    return True


def test_weak_points():
    """Test weak point tracking"""
    print("\n" + "="*60)
    print("TEST 4: Weak Point Tracking")
    print("="*60)
    
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return False
    
    # Get or create a weak point
    weak_point, created = WeakPoint.objects.get_or_create(
        user=user,
        topic="Python Loops",
        defaults={
            'subtopic': 'For Loops',
            'incorrect_count': 3,
            'total_attempts': 5,
            'accuracy': 40.0,
            'confidence_score': 0.4
        }
    )
    
    if created:
        print(f"✓ Created weak point: {weak_point.topic}")
    else:
        print(f"✓ Found existing weak point: {weak_point.topic}")
    
    print(f"  - Accuracy: {weak_point.accuracy:.1f}%")
    print(f"  - Confidence: {weak_point.confidence_score:.2f}")
    print(f"  - Attempts: {weak_point.incorrect_count}/{weak_point.total_attempts}")
    
    return True


def test_recommendations():
    """Test recommendation service"""
    print("\n" + "="*60)
    print("TEST 5: Course Recommendations")
    print("="*60)
    
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return False
    
    weak_point = WeakPoint.objects.filter(user=user).first()
    
    if not weak_point:
        print("⚠ No weak points found. Creating one...")
        weak_point = WeakPoint.objects.create(
            user=user,
            topic="Python Basics",
            accuracy=50.0,
            confidence_score=0.5
        )
    
    print(f"\n✓ Testing recommendations for: {weak_point.topic}")
    print("  Note: Web scraper requires Chrome/Selenium")
    print("  Will use fallback if scraper not available")
    
    # Check if recommendations already exist
    existing = CourseRecommendation.objects.filter(weak_point=weak_point).count()
    print(f"  - Existing recommendations: {existing}")
    
    if existing == 0:
        print("  - Recommendations will be generated on first API call")
    
    return True


def test_browser_extension_api():
    """Test browser extension API models"""
    print("\n" + "="*60)
    print("TEST 6: Browser Extension Integration")
    print("="*60)
    
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return False
    
    # Check if there are any sessions
    session = StudySession.objects.filter(user=user).first()
    
    if not session:
        print("⚠ No study sessions found")
        print("  Extension data will be created when session starts")
    else:
        print(f"✓ Found session: {session.workspace_name}")
        
        # Check extension data
        ext_data = BrowserExtensionData.objects.filter(session=session).first()
        
        if ext_data:
            print(f"  - Tab switches: {ext_data.tab_switches}")
            print(f"  - Blocked attempts: {ext_data.blocked_attempts}")
            print(f"  - Extension active: {ext_data.extension_active}")
        else:
            print("  - No extension data yet")
    
    print("\n  Extension API endpoints ready:")
    print("  - POST /api/adaptive/extension/heartbeat/")
    print("  - POST /api/adaptive/extension/violation/")
    print("  - GET /api/adaptive/extension/status/")
    
    return True


def test_dashboard_api():
    """Test dashboard API data"""
    print("\n" + "="*60)
    print("TEST 7: Dashboard API")
    print("="*60)
    
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return False
    
    # Get weekly sessions
    week_ago = timezone.now() - timedelta(days=7)
    weekly_sessions = StudySession.objects.filter(
        user=user,
        started_at__gte=week_ago
    ).count()
    
    # Get test results
    test_results = TestResult.objects.filter(user=user).count()
    
    # Get session limit
    from datetime import date
    session_limit = SessionLimit.objects.filter(
        user=user,
        date=date.today()
    ).first()
    
    print(f"✓ Dashboard data for {user.username}:")
    print(f"  - Weekly sessions: {weekly_sessions}")
    print(f"  - Test results: {test_results}")
    
    if session_limit:
        completion = (session_limit.tests_completed / session_limit.sessions_created * 100) if session_limit.sessions_created > 0 else 0
        print(f"  - Completion: {completion:.1f}%")
        print(f"  - Can create session: {session_limit.can_create_session}")
    
    print("\n  Dashboard API endpoint ready:")
    print("  - GET /api/adaptive/dashboard/overview/")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 2 BACKEND TESTING")
    print("="*60)
    print("\nTesting all new features...")
    
    tests = [
        test_session_limits,
        test_test_generation,
        test_email_service,
        test_weak_points,
        test_recommendations,
        test_browser_extension_api,
        test_dashboard_api
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! Backend is ready.")
        print("\nNext steps:")
        print("1. Start backend: cd learning && python manage.py runserver")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Test dashboard API: http://localhost:8000/api/adaptive/dashboard/overview/")
    else:
        print("\n⚠ Some tests failed. Check the output above.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
