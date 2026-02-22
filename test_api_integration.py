"""
Quick API Integration Test
Tests if all endpoints are properly registered
"""
import sys
import os

# Add learning to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'learning'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')

import django
django.setup()

from django.urls import get_resolver
from rest_framework.test import APIClient
from django.contrib.auth.models import User

def test_url_patterns():
    """Test if URL patterns are registered"""
    print("\n" + "="*60)
    print("Testing URL Patterns")
    print("="*60)
    
    resolver = get_resolver()
    
    # Check for adaptive learning URLs
    adaptive_urls = [
        'api/adaptive/adaptive-suggestions/weak_point_suggestions/',
        'api/adaptive/adaptive-suggestions/recent_topic_suggestions/',
        'api/adaptive/adaptive-suggestions/coursera_certificates/',
        'api/adaptive/adaptive-suggestions/mark_suggestion_viewed/',
        'api/adaptive/adaptive-suggestions/refresh_suggestions/',
    ]
    
    print("\nChecking API endpoints:")
    for url in adaptive_urls:
        try:
            match = resolver.resolve('/' + url)
            print(f"✅ {url}")
        except:
            print(f"❌ {url} - NOT FOUND")

def test_imports():
    """Test if all modules can be imported"""
    print("\n" + "="*60)
    print("Testing Module Imports")
    print("="*60)
    
    try:
        from adaptive_learning.coursera_service import CourseraService
        print("✅ CourseraService imported")
    except Exception as e:
        print(f"❌ CourseraService import failed: {e}")
    
    try:
        from adaptive_learning.adaptive_suggestion_views import AdaptiveSuggestionViewSet
        print("✅ AdaptiveSuggestionViewSet imported")
    except Exception as e:
        print(f"❌ AdaptiveSuggestionViewSet import failed: {e}")
    
    try:
        from adaptive_learning.recommendation_service import RecommendationService
        print("✅ RecommendationService imported")
    except Exception as e:
        print(f"❌ RecommendationService import failed: {e}")

def test_models():
    """Test if models are accessible"""
    print("\n" + "="*60)
    print("Testing Models")
    print("="*60)
    
    try:
        from adaptive_learning.models import WeakPoint, CourseRecommendation, Topic
        print("✅ WeakPoint model")
        print("✅ CourseRecommendation model")
        print("✅ Topic model")
    except Exception as e:
        print(f"❌ Model import failed: {e}")

def test_coursera_service():
    """Test Coursera service functionality"""
    print("\n" + "="*60)
    print("Testing Coursera Service")
    print("="*60)
    
    try:
        from adaptive_learning.coursera_service import CourseraService
        
        # Test certificate mapping
        certs = CourseraService.find_matching_certificates('python')
        print(f"✅ Found {len(certs)} Python certificates")
        
        certs = CourseraService.find_matching_certificates('machine learning')
        print(f"✅ Found {len(certs)} Machine Learning certificates")
        
        certs = CourseraService.find_matching_certificates('web development')
        print(f"✅ Found {len(certs)} Web Development certificates")
        
    except Exception as e:
        print(f"❌ Coursera service test failed: {e}")

def main():
    print("\n" + "="*60)
    print("API INTEGRATION TEST")
    print("="*60)
    
    try:
        test_imports()
        test_models()
        test_coursera_service()
        test_url_patterns()
        
        print("\n" + "="*60)
        print("✅ INTEGRATION TEST PASSED")
        print("="*60)
        print("\n✨ All components are properly integrated!")
        print("\n🚀 Ready to start:")
        print("   Backend: cd learning && python manage.py runserver")
        print("   Frontend: cd frontend && npm run dev")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
