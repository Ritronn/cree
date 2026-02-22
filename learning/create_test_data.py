"""
Create test data for specific user
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import WeakPoint, StudySession, Topic, Content
from datetime import datetime, timedelta

print("\n" + "="*60)
print("CREATING TEST DATA")
print("="*60)

# Get or create user
email = "rutvikkale2006666@gmail.com"
username = email.split('@')[0]

try:
    user = User.objects.get(email=email)
    print(f"\n✅ Found user: {user.username} ({user.email})")
except User.DoesNotExist:
    user = User.objects.create_user(
        username=username,
        email=email,
        password='123456'
    )
    print(f"\n✅ Created user: {user.username} ({user.email})")

# Create some topics
topics_to_create = [
    ('Python Programming', 'Learn Python basics and advanced concepts'),
    ('JavaScript', 'Modern JavaScript and ES6+'),
    ('React', 'React framework for building UIs'),
]

print("\n📚 Creating Topics...")
for topic_name, description in topics_to_create:
    topic, created = Topic.objects.get_or_create(
        user=user,
        name=topic_name,
        defaults={
            'description': description,
            'mastery_level': 0.5,
            'current_difficulty': 2,
            'sessions_completed': 1
        }
    )
    if created:
        print(f"  ✅ Created: {topic_name}")
    else:
        print(f"  ℹ️  Exists: {topic_name}")

# Create some completed study sessions with workspace names
sessions_to_create = [
    'Python',
    'JavaScript',
    'React',
    'Machine Learning',
    'Web Development'
]

print("\n🎓 Creating Study Sessions...")

# First, create a dummy content for sessions
from django.utils import timezone

for workspace_name in sessions_to_create:
    # Create content first
    topic_obj = Topic.objects.filter(user=user).first()
    if not topic_obj:
        topic_obj = Topic.objects.create(
            user=user,
            name=workspace_name,
            description=f"Study {workspace_name}"
        )
    
    content, _ = Content.objects.get_or_create(
        topic=topic_obj,
        title=f"{workspace_name} Content",
        defaults={
            'content_type': 'youtube',
            'url': f'https://youtube.com/watch?v={workspace_name}',
            'processed': True
        }
    )
    
    # Now create session
    session, created = StudySession.objects.get_or_create(
        user=user,
        workspace_name=workspace_name,
        content=content,
        is_completed=True,
        defaults={
            'started_at': timezone.now() - timedelta(days=2),
            'ended_at': timezone.now() - timedelta(days=2, hours=-2),
            'study_duration_seconds': 7200,
            'session_type': 'recommended'
        }
    )
    if created:
        print(f"  ✅ Created: {workspace_name}")
    else:
        print(f"  ℹ️  Exists: {workspace_name}")

# Create some weak points
weak_points_to_create = [
    ('Python Loops', 'For Loops', 45.5, 6, 11),
    ('JavaScript Arrays', 'Array Methods', 52.0, 5, 10),
    ('React Hooks', 'useState', 38.0, 7, 12),
]

print("\n⚠️  Creating Weak Points...")
for topic, subtopic, accuracy, incorrect, total in weak_points_to_create:
    wp, created = WeakPoint.objects.get_or_create(
        user=user,
        topic=topic,
        defaults={
            'subtopic': subtopic,
            'accuracy': accuracy,
            'confidence_score': accuracy / 100,
            'incorrect_count': incorrect,
            'total_attempts': total
        }
    )
    if created:
        print(f"  ✅ Created: {topic} ({accuracy}% accuracy)")
    else:
        print(f"  ℹ️  Exists: {topic} ({wp.accuracy}% accuracy)")

print("\n" + "="*60)
print("TEST DATA CREATED SUCCESSFULLY!")
print("="*60)

# Summary
print(f"\n📊 Summary for {user.username}:")
print(f"  - Topics: {Topic.objects.filter(user=user).count()}")
print(f"  - Completed Sessions: {StudySession.objects.filter(user=user, is_completed=True).count()}")
print(f"  - Weak Points: {WeakPoint.objects.filter(user=user).count()}")

print("\n🚀 Now you can:")
print(f"  1. Login with: {email} / 123456")
print(f"  2. Go to Dashboard")
print(f"  3. Click 'Adaptive Suggestions'")
print(f"  4. See suggestions for weak points and study topics!")

print("\n" + "="*60)
