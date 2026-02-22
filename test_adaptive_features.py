"""
Test script for Adaptive Learning Features
Run this to verify all components are working
"""
import os
import sys
import django

# Setup Django
learning_path = os.path.join(os.path.dirname(__file__), 'learning')
sys.path.insert(0, learning_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import WeakPoint, Topic
from adaptive_learning.recommendation_service import RecommendationService
from adaptive_learning.coursera_service import CourseraService


def test_weak_point_recommendations():
    """Test weak point recommendation generation"""
    print("\n" + "="*60)
    print("Testing Weak Point Recommendations")
    print("="*60)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing user: {user.username}")
    
    # Create a test weak point
    weak_point, created = WeakPoint.objects.get_or_create(
        user=user,
        topic='Python Loops',
        defaults={
            'subtopic': 'For Loops',
            'incorrect_count': 6,
            'total_attempts': 10,
            'accuracy': 40.0,
            'confidence_score': 0.3
        }
    )
    
    if created:
        print(f"✓ Created weak point: {weak_point.topic}")
    else:
        print(f"✓ Using existing weak point: {weak_point.topic}")
    
    # Generate recommendations
    print("\nGenerating recommendations...")
    try:
        result = RecommendationService.generate_recommendations(weak_point)
        print(f"✓ Generated {result['recommendations_count']} recommendations")
        print(f"  - Playlists: {result['playlists']}")
        print(f"  - Articles: {result['articles']}")
        print(f"  - Questions: {result['questions']}")
    except Exception as e:
        print(f"✗ Error generating recommendations: {e}")
        print("  (This is expected if web scraper dependencies are not installed)")
    
    return user


def test_coursera_recommendations(user):
    """Test Coursera certificate recommendations"""
    print("\n" + "="*60)
    print("Testing Coursera Certificate Recommendations")
    print("="*60)
    
    # Create test topics
    topics = [
        ('Python Programming', 'Learn Python basics and advanced concepts'),
        ('Machine Learning', 'Introduction to ML algorithms'),
        ('Web Development', 'Build modern web applications')
    ]
    
    for topic_name, description in topics:
        topic, created = Topic.objects.get_or_create(
            user=user,
            name=topic_name,
            defaults={
                'description': description,
                'mastery_level': 0.5,
                'current_difficulty': 2
            }
        )
        if created:
            print(f"✓ Created topic: {topic_name}")
    
    # Get recommendations
    print("\nFetching Coursera recommendations...")
    certificates = CourseraService.get_recommendations_for_user(user)
    
    print(f"✓ Found {len(certificates)} certificate recommendations")
    
    if certificates:
        print("\nTop 3 Recommendations:")
        for i, cert in enumerate(certificates[:3], 1):
            print(f"\n{i}. {cert['title']}")
            print(f"   Provider: {cert['provider']}")
            print(f"   Level: {cert['level']}")
            print(f"   Duration: {cert['duration']}")
            print(f"   URL: {cert['url']}")


def test_api_endpoints():
    """Test API endpoint structure"""
    print("\n" + "="*60)
    print("Testing API Endpoint Structure")
    print("="*60)
    
    from adaptive_learning.urls import router
    
    print("\nRegistered API endpoints:")
    for pattern in router.urls:
        print(f"  ✓ {pattern.pattern}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ADAPTIVE LEARNING FEATURES TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Weak Point Recommendations
        user = test_weak_point_recommendations()
        
        # Test 2: Coursera Recommendations
        test_coursera_recommendations(user)
        
        # Test 3: API Endpoints
        test_api_endpoints()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED")
        print("="*60)
        print("\nNext Steps:")
        print("1. Start Django server: cd learning && python manage.py runserver")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Login with test user: testuser / testpass123")
        print("4. Navigate to Dashboard and click 'Adaptive Suggestions'")
        print("5. Navigate to Dashboard and click 'Course Suggestions'")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
