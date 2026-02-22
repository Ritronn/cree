"""
Single API call test - verify integration works
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from django.contrib.auth.models import User
from adaptive_learning.models import Topic, Content
from adaptive_learning.gemini_mcq_service import generate_adaptive_questions_for_user

# Get or create test user
user, _ = User.objects.get_or_create(username='test_user', defaults={'email': 'test@test.com'})
topic, _ = Topic.objects.get_or_create(user=user, name='Python Basics')
content, _ = Content.objects.get_or_create(
    topic=topic,
    title='Python Variables',
    defaults={
        'content_type': 'youtube',
        'transcript': 'Python variables store data. Use = to assign values. Example: x = 5',
        'processed': True
    }
)

print("Testing single MCQ generation...")
print(f"User: {user.username}")
print(f"Content: {content.title}")

try:
    assessment = generate_adaptive_questions_for_user(user, content)
    print(f"\n✅ SUCCESS!")
    print(f"Assessment ID: {assessment.id}")
    print(f"Questions: {assessment.total_questions}")
    print(f"Difficulty: {assessment.difficulty_level}")
    
    # Show first question
    q = assessment.questions.first()
    if q:
        print(f"\nSample Question:")
        print(f"Q: {q.question_text}")
        print(f"Options: {q.options}")
        print(f"Answer: {q.options[q.correct_answer_index]}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
