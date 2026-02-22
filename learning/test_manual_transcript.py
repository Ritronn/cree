"""
Test MCQ generation with manual transcript (bypass YouTube block)
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

# PASTE YOUR TRANSCRIPT HERE (get from YouTube manually)
MANUAL_TRANSCRIPT = """
We're no strangers to love
You know the rules and so do I
A full commitment's what I'm thinking of
You wouldn't get this from any other guy
I just wanna tell you how I'm feeling
Gotta make you understand
Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
"""

print("Testing MCQ generation with manual transcript...")
print(f"Transcript length: {len(MANUAL_TRANSCRIPT)} chars")

# Create test data
user, _ = User.objects.get_or_create(username='manual_test_user')
topic, _ = Topic.objects.get_or_create(user=user, name='Test Topic')
content, _ = Content.objects.get_or_create(
    topic=topic,
    title='Manual Transcript Test',
    defaults={
        'content_type': 'youtube',
        'transcript': MANUAL_TRANSCRIPT,  # Use manual transcript
        'processed': True
    }
)

# Update transcript if content exists
if content.transcript != MANUAL_TRANSCRIPT:
    content.transcript = MANUAL_TRANSCRIPT
    content.save()

print(f"\nGenerating questions...")

try:
    assessment = generate_adaptive_questions_for_user(user, content)
    
    print(f"\n✅ SUCCESS!")
    print(f"Assessment ID: {assessment.id}")
    print(f"Questions: {assessment.total_questions}")
    print(f"Difficulty: {assessment.difficulty_level}")
    
    print(f"\nGenerated Questions:")
    for q in assessment.questions.all()[:3]:
        print(f"\nQ{q.order + 1}: {q.question_text}")
        print(f"Options: {q.options}")
        print(f"Answer: {q.options[q.correct_answer_index]}")
        print(f"Concept: {q.concept}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("HOW TO GET TRANSCRIPT MANUALLY:")
print("="*70)
print("1. Go to YouTube video")
print("2. Click '...' (More) below video")
print("3. Click 'Show transcript'")
print("4. Copy all text")
print("5. Paste into MANUAL_TRANSCRIPT variable above")
print("="*70)
