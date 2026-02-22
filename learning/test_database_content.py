"""
Check what's actually in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import WeakPoint, StudySession, Topic

print("\n" + "="*60)
print("DATABASE CONTENT CHECK")
print("="*60)

# Get first user
users = User.objects.all()
print(f"\nTotal Users: {users.count()}")

if users.exists():
    user = users.first()
    print(f"Checking data for user: {user.username}")
    
    # Check weak points
    weak_points = WeakPoint.objects.filter(user=user)
    print(f"\n1. Weak Points: {weak_points.count()}")
    for wp in weak_points[:5]:
        print(f"   - {wp.topic} ({wp.accuracy}% accuracy)")
    
    # Check study sessions
    all_sessions = StudySession.objects.filter(user=user)
    completed_sessions = all_sessions.filter(is_completed=True)
    sessions_with_names = completed_sessions.exclude(workspace_name__isnull=True).exclude(workspace_name__exact='')
    
    print(f"\n2. Study Sessions:")
    print(f"   - Total: {all_sessions.count()}")
    print(f"   - Completed: {completed_sessions.count()}")
    print(f"   - With workspace names: {sessions_with_names.count()}")
    
    for session in sessions_with_names[:5]:
        print(f"   - '{session.workspace_name}' (completed: {session.ended_at})")
    
    # Check topics
    topics = Topic.objects.filter(user=user)
    print(f"\n3. Topics: {topics.count()}")
    for topic in topics[:5]:
        print(f"   - {topic.name} (mastery: {topic.mastery_level*100:.0f}%)")
    
    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)
    
    if weak_points.exists():
        print("✅ User has weak points - suggestions will show")
    elif sessions_with_names.exists():
        print("✅ User has completed sessions - suggestions will show")
    elif topics.exists():
        print("✅ User has topics - suggestions will show")
    else:
        print("❌ No data found - user needs to:")
        print("   1. Complete a test (to create weak points), OR")
        print("   2. Complete a study session (with workspace name), OR")
        print("   3. Create a topic")
else:
    print("\n❌ No users in database!")
    print("   Create a user first")

print("\n" + "="*60)
