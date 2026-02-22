"""
Test Grok AI Integration
Run this to verify Grok AI is working correctly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

from adaptive_learning.question_generator import QuestionGenerator
from adaptive_learning.rag_chat_integration import RAGChatIntegration
from adaptive_learning.models import StudySession


def test_api_key():
    """Test if API key is configured"""
    print("\n" + "="*60)
    print("TEST 1: API Key Configuration")
    print("="*60)
    
    api_key = os.environ.get('XAI_API_KEY')
    if not api_key:
        print("❌ XAI_API_KEY not found in environment")
        print("   Please add it to learning/.env file")
        return False
    elif api_key == 'your_grok_api_key_here':
        print("⚠️  XAI_API_KEY is placeholder")
        print("   Please replace with your actual Grok API key")
        return False
    else:
        print(f"✅ XAI_API_KEY configured: {api_key[:10]}...")
        return True


def test_question_generation():
    """Test question generation with Grok AI"""
    print("\n" + "="*60)
    print("TEST 2: Question Generation")
    print("="*60)
    
    try:
        qg = QuestionGenerator()
        
        print("Generating MCQ questions...")
        questions = qg.generate_mcq_questions(
            content="Python is a high-level programming language known for its simplicity and readability.",
            concepts=["Python", "Programming"],
            difficulty=1,
            count=2
        )
        
        if questions:
            print(f"✅ Generated {len(questions)} questions")
            for i, q in enumerate(questions, 1):
                print(f"\n   Question {i}:")
                print(f"   Type: {q.get('type')}")
                print(f"   Question: {q.get('question', '')[:80]}...")
                if q.get('type') == 'mcq':
                    print(f"   Options: {len(q.get('options', []))} choices")
            return True
        else:
            print("⚠️  No questions generated (using fallback)")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_answer_assessment():
    """Test answer assessment with Grok AI"""
    print("\n" + "="*60)
    print("TEST 3: Answer Assessment")
    print("="*60)
    
    try:
        qg = QuestionGenerator()
        
        print("Assessing a sample answer...")
        result = qg.assess_answer(
            question="What is Python?",
            expected_answer="Python is a high-level programming language",
            user_answer="Python is a programming language used for coding",
            question_type="short_answer"
        )
        
        if result:
            print(f"✅ Assessment completed")
            print(f"   Score: {result.get('score')}/100")
            print(f"   Correct: {result.get('is_correct')}")
            print(f"   Feedback: {result.get('feedback', '')[:80]}...")
            print(f"   Confidence: {result.get('confidence')}")
            return True
        else:
            print("⚠️  Assessment failed (using fallback)")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_chat_integration():
    """Test RAG chat with Grok AI"""
    print("\n" + "="*60)
    print("TEST 4: RAG Chat Integration")
    print("="*60)
    
    try:
        # Try to get a session
        session = StudySession.objects.first()
        
        if not session:
            print("⚠️  No study sessions found in database")
            print("   Create a study session first to test chat")
            return False
        
        print(f"Using session ID: {session.id}")
        print("Sending test query...")
        
        response = RAGChatIntegration.send_query(
            session_id=session.id,
            query="Can you explain the main concept?",
            context="Python is a programming language"
        )
        
        if response.get('success'):
            print(f"✅ Chat response received")
            print(f"   Response: {response.get('response', '')[:100]}...")
            print(f"   Confidence: {response.get('confidence')}")
            return True
        else:
            print(f"⚠️  Chat failed: {response.get('error', 'Unknown error')}")
            print(f"   Fallback: {response.get('fallback_response', '')[:80]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("GROK AI INTEGRATION TEST SUITE")
    print("="*60)
    
    results = {
        'API Key': test_api_key(),
        'Question Generation': test_question_generation(),
        'Answer Assessment': test_answer_assessment(),
        'Chat Integration': test_chat_integration()
    }
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Grok AI is working correctly.")
    elif passed > 0:
        print("\n⚠️  Some tests passed. Check failed tests above.")
    else:
        print("\n❌ All tests failed. Please check your configuration.")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
