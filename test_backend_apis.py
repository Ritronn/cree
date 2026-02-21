#!/usr/bin/env python
"""
Backend API Testing Script
Tests all major endpoints of the Velocity adaptive learning platform
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/adaptive"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def test_endpoint(method, endpoint, data=None, files=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        elif method == "PATCH":
            response = requests.patch(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print_error(f"Unknown method: {method}")
            return None
        
        if response.status_code == expected_status:
            print_success(f"{method} {endpoint} - Status {response.status_code}")
            return response.json() if response.content else None
        else:
            print_error(f"{method} {endpoint} - Status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed - Is the server running on {BASE_URL}?")
        return None
    except Exception as e:
        print_error(f"{method} {endpoint} - Error: {str(e)}")
        return None

def main():
    print("\n" + "="*60)
    print("Velocity Backend API Testing")
    print("="*60 + "\n")
    
    # Test 1: Topics
    print_info("Testing Topics API...")
    
    # Create topic
    topic_data = {
        "name": "Test Topic",
        "description": "Testing the API"
    }
    topic = test_endpoint("POST", "/topics/", data=topic_data, expected_status=201)
    
    if topic:
        topic_id = topic.get('id')
        print(f"  Created topic ID: {topic_id}")
        
        # List topics
        topics = test_endpoint("GET", "/topics/")
        if topics:
            print(f"  Found {len(topics)} topics")
        
        # Get topic progress
        progress = test_endpoint("GET", f"/topics/{topic_id}/progress/")
        
        # Get concept mastery
        concepts = test_endpoint("GET", f"/topics/{topic_id}/concepts/")
    
    print()
    
    # Test 2: Content
    print_info("Testing Content API...")
    
    if topic:
        # Upload YouTube content
        content_data = {
            "topic": topic_id,
            "title": "Test Video",
            "content_type": "youtube",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        content = test_endpoint("POST", "/content/upload/", data=content_data, expected_status=201)
        
        if content:
            content_id = content.get('id')
            print(f"  Created content ID: {content_id}")
            
            # List content
            contents = test_endpoint("GET", "/content/")
            if contents:
                print(f"  Found {len(contents)} content items")
            
            # Generate assessment (may fail if content not processed)
            print_warning("  Attempting to generate assessment (may fail if content not processed)")
            assessment = test_endpoint("POST", f"/content/{content_id}/generate_assessment/")
    
    print()
    
    # Test 3: Assessments
    print_info("Testing Assessment API...")
    
    if content and assessment:
        assessment_id = assessment.get('id')
        print(f"  Created assessment ID: {assessment_id}")
        
        # Get questions
        questions = test_endpoint("GET", f"/assessments/{assessment_id}/questions/")
        
        if questions and len(questions) > 0:
            question_id = questions[0].get('id')
            
            # Submit answer
            answer_data = {
                "question_id": question_id,
                "selected_answer_index": 0,
                "time_taken_seconds": 30
            }
            answer = test_endpoint("POST", f"/assessments/{assessment_id}/submit_answer/", data=answer_data)
            
            # Complete assessment
            results = test_endpoint("POST", f"/assessments/{assessment_id}/complete/")
            if results:
                print(f"  Score: {results.get('score', 0)}%")
    
    print()
    
    # Test 4: Study Sessions
    print_info("Testing Study Session API...")
    
    if content:
        # Create session
        session_data = {
            "content_id": content_id,
            "session_type": "recommended"
        }
        session_response = test_endpoint("POST", "/study-sessions/", data=session_data, expected_status=201)
        
        if session_response:
            session = session_response.get('session', {})
            session_id = session.get('id')
            print(f"  Created session ID: {session_id}")
            
            # Get session status
            status = test_endpoint("GET", f"/study-sessions/{session_id}/status/")
            
            # Update camera
            camera_data = {"enabled": True}
            test_endpoint("POST", f"/study-sessions/{session_id}/update_camera/", data=camera_data)
            
            # Start break
            test_endpoint("POST", f"/study-sessions/{session_id}/start_break/")
            
            # End break
            test_endpoint("POST", f"/study-sessions/{session_id}/end_break/")
            
            # Complete session
            completion = test_endpoint("POST", f"/study-sessions/{session_id}/complete/")
            if completion and completion.get('test'):
                test_id = completion['test'].get('id')
                print(f"  Generated test ID: {test_id}")
    
    print()
    
    # Test 5: Monitoring
    print_info("Testing Monitoring API...")
    
    if session_id:
        # Record event
        event_data = {
            "session_id": session_id,
            "event_type": "video_pause",
            "event_data": {"position": 120}
        }
        test_endpoint("POST", "/session-monitoring/", data=event_data)
        
        # Update metrics
        metrics_data = {"session_id": session_id}
        test_endpoint("POST", "/session-monitoring/update_metrics/", data=metrics_data)
    
    print()
    
    # Test 6: Proctoring
    print_info("Testing Proctoring API...")
    
    if session_id:
        # Record tab switch
        proctoring_data = {
            "session_id": session_id,
            "event_type": "tab_switch"
        }
        test_endpoint("POST", "/proctoring/", data=proctoring_data)
        
        # Record copy attempt
        proctoring_data["event_type"] = "copy_attempt"
        test_endpoint("POST", "/proctoring/", data=proctoring_data)
    
    print()
    
    # Test 7: Tests
    print_info("Testing Test API...")
    
    if session_id:
        # Generate test
        test_data = {
            "session_id": session_id,
            "difficulty": 1
        }
        test_obj = test_endpoint("POST", "/tests/generate/", data=test_data, expected_status=201)
        
        if test_obj:
            test_id = test_obj.get('id')
            print(f"  Generated test ID: {test_id}")
            
            # Start test
            test_endpoint("POST", f"/tests/{test_id}/start/")
            
            # Get test details
            test_details = test_endpoint("GET", f"/tests/{test_id}/")
            
            if test_details and test_details.get('questions'):
                questions = test_details['questions']
                if len(questions) > 0:
                    question = questions[0]
                    
                    # Submit answer
                    answer_data = {
                        "question_id": question['id'],
                        "answer_text": "Test answer",
                        "selected_index": 0 if question['question_type'] == 'mcq' else None,
                        "time_taken_seconds": 45
                    }
                    test_endpoint("POST", f"/tests/{test_id}/submit_answer/", data=answer_data)
                    
                    # Complete test
                    results = test_endpoint("POST", f"/tests/{test_id}/complete/")
                    if results:
                        print(f"  Test score: {results.get('overall_score', 0)}%")
    
    print()
    
    # Test 8: Chat
    print_info("Testing Chat API...")
    
    if session_id:
        # Send query
        chat_data = {
            "session_id": session_id,
            "query": "What is Python?",
            "context": "Python Programming"
        }
        response = test_endpoint("POST", "/chat/", data=chat_data)
        if response:
            print(f"  Response: {response.get('response', '')[:100]}...")
        
        # Get history
        history = test_endpoint("GET", f"/chat/history/?session_id={session_id}")
    
    print()
    
    # Test 9: Progress
    print_info("Testing Progress API...")
    
    # List progress
    progress_list = test_endpoint("GET", "/progress/")
    if progress_list:
        print(f"  Found {len(progress_list)} progress records")
    
    # Get overview
    overview = test_endpoint("GET", "/progress/overview/")
    if overview:
        print(f"  Total topics: {overview.get('total_topics', 0)}")
        print(f"  Average mastery: {overview.get('average_mastery', 0):.2f}")
    
    print()
    
    # Summary
    print("="*60)
    print("Testing Complete!")
    print("="*60)
    print()
    print_info("Check the output above for any errors")
    print_info("All green checkmarks mean the API is working correctly")
    print()

if __name__ == "__main__":
    main()
