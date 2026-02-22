"""
Quick test script to verify YouTube transcript fetching and Gemini MCQ generation
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/adaptive"

# Test YouTube URL (the 3D avatar builder video from the transcript)
YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with actual video ID

def test_upload_youtube_content():
    """Test uploading YouTube content"""
    print("=" * 60)
    print("TEST 1: Upload YouTube Content")
    print("=" * 60)
    
    payload = {
        "title": "Test 3D Avatar Builder",
        "content_type": "youtube",
        "url": YOUTUBE_URL
    }
    
    try:
        response = requests.post(f"{BASE_URL}/content/upload/", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Content uploaded successfully!")
            print(f"Content ID: {data.get('id')}")
            print(f"Title: {data.get('title')}")
            print(f"Transcript length: {len(data.get('transcript', ''))} characters")
            return data.get('id')
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_generate_mcqs(content_id, user_state=4):
    """Test generating MCQs for content"""
    print("\n" + "=" * 60)
    print(f"TEST 2: Generate MCQs (User State: {user_state})")
    print("=" * 60)
    
    payload = {
        "user_state": user_state
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/content/{content_id}/generate_gemini_mcqs/",
            json=payload
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MCQs generated successfully!")
            print(f"User State: {data.get('user_state')}")
            print(f"Difficulty: {data.get('difficulty')}")
            print(f"Number of Questions: {data.get('num_questions')}")
            print(f"Take Break Suggestion: {data.get('take_break_suggestion')}")
            
            # Show first 2 questions
            questions = data.get('questions', [])
            print(f"\nFirst 2 questions:")
            for i, q in enumerate(questions[:2], 1):
                print(f"\nQ{i}: {q.get('question')}")
                print(f"Options: {q.get('options')}")
                print(f"Answer: {q.get('answer')}")
                print(f"Explanation: {q.get('explanation')}")
            
            return data
        else:
            print(f"❌ MCQ generation failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("\n🚀 Starting Integration Test\n")
    
    # Test 1: Upload YouTube content
    content_id = test_upload_youtube_content()
    
    if not content_id:
        print("\n❌ Test failed at content upload stage")
        return
    
    # Test 2: Generate MCQs
    mcq_data = test_generate_mcqs(content_id, user_state=4)
    
    if mcq_data:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nIntegration is working correctly:")
        print("1. YouTube transcript fetching ✅")
        print("2. Gemini MCQ generation ✅")
        print("3. API endpoints responding ✅")
    else:
        print("\n❌ Test failed at MCQ generation stage")

if __name__ == "__main__":
    main()
