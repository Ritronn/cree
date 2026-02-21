"""
Quick test script for Adaptive Learning API
Run after starting Django server: python manage.py runserver
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/adaptive"

def test_api():
    print("=" * 60)
    print("Testing Adaptive Learning API")
    print("=" * 60)
    
    # Note: You need to be logged in for these to work
    # For testing, you can temporarily disable authentication
    # or use Django admin to create a session
    
    print("\n1. Testing Topics Endpoint")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/topics/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Topics: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Testing Content Endpoint")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/content/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Content: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Testing Assessments Endpoint")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/assessments/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Assessments: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n4. Testing Progress Endpoint")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/progress/overview/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Progress: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNote: If you see 403 Forbidden errors, you need to:")
    print("1. Create a user: python manage.py createsuperuser")
    print("2. Login via Django admin: http://localhost:8000/admin")
    print("3. Or temporarily disable authentication in views.py")

if __name__ == "__main__":
    test_api()
