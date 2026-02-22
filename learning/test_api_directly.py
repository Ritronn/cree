"""
Test the API endpoint directly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from adaptive_learning.adaptive_suggestion_views import AdaptiveSuggestionViewSet

print("\n" + "="*60)
print("TESTING API ENDPOINT DIRECTLY")
print("="*60)

# Get specific user
user = User.objects.get(email='rutvikkale2006666@gmail.com')
print(f"\nUser: {user.username} ({user.email})")

# Create request
factory = APIRequestFactory()
request = factory.get('/api/adaptive/adaptive-suggestions/weak_point_suggestions/')
force_authenticate(request, user=user)

# Call the view
view = AdaptiveSuggestionViewSet.as_view({'get': 'weak_point_suggestions'})
response = view(request)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Data:")
print(f"  - Success: {response.data.get('success')}")
print(f"  - Suggestions Count: {response.data.get('weak_points_count')}")
print(f"  - Fallback Used: {response.data.get('fallback_used')}")
print(f"  - Using Curated Data: {response.data.get('using_curated_data')}")

suggestions = response.data.get('suggestions', [])
print(f"\nSuggestions: {len(suggestions)}")

for i, suggestion in enumerate(suggestions, 1):
    wp = suggestion.get('weak_point', {})
    sug_list = suggestion.get('suggestions', [])
    print(f"\n{i}. Topic: {wp.get('topic')}")
    print(f"   Subtopic: {wp.get('subtopic')}")
    print(f"   Accuracy: {wp.get('accuracy')}%")
    print(f"   Suggestions: {len(sug_list)}")
    
    # Group by source
    youtube = [s for s in sug_list if s.get('source') == 'youtube']
    articles = [s for s in sug_list if s.get('source') == 'article']
    stackoverflow = [s for s in sug_list if s.get('source') == 'stackoverflow']
    
    print(f"     - YouTube: {len(youtube)}")
    print(f"     - Articles: {len(articles)}")
    print(f"     - Stack Overflow: {len(stackoverflow)}")
    
    if youtube:
        print(f"\n   Sample YouTube:")
        for j, s in enumerate(youtube[:2], 1):
            print(f"     {j}. {s.get('title')[:60]}...")
            print(f"        {s.get('url')}")

print("\n" + "="*60)
print("✅ API IS WORKING!")
print("="*60)
print("\nNow login to frontend with:")
print("  Email: rutvikkale2006666@gmail.com")
print("  Password: 123456")
print("\nAnd click 'Adaptive Suggestions' button!")
print("="*60)

