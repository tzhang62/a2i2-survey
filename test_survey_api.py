#!/usr/bin/env python3
"""
Test script for the survey API
Run this to verify the backend is working correctly
"""

import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8001"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_survey_submission():
    """Test survey submission"""
    print("\nTesting survey submission...")
    
    # Sample survey data
    survey_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "background": {
            "email": "test@example.com",
            "nickname": "TestUser",
            "age": "25",
            "gender": "male",
            "education": "college-graduate",
            "occupation": "Researcher",
            "ideology": "4"
        },
        "personality": {
            f"q{i}": str((i % 5) + 1) for i in range(1, 11)
        },
        "moral": {
            f"q{i}": str((i % 6) + 1) for i in range(1, 13)
        },
        "specialNeeds": {
            "condition": "no",
            "responsible": "yes",
            "vehicle": "no",
            "details": "I have a small dog"
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/survey",
            json=survey_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Survey submission passed")
            print(f"   Participant ID: {result.get('participantId')}")
            print(f"   Success: {result.get('success')}")
            return result.get('participantId')
        else:
            print(f"❌ Survey submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Survey submission error: {e}")
        return None

def test_survey_retrieval(participant_id):
    """Test retrieving survey data"""
    if not participant_id:
        print("\n⚠️  Skipping retrieval test (no participant ID)")
        return False
        
    print(f"\nTesting survey retrieval for {participant_id}...")
    
    try:
        response = requests.get(f"{API_URL}/api/survey/{participant_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Survey retrieval passed")
            print(f"   Nickname: {data.get('background', {}).get('nickname')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Survey retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Survey retrieval error: {e}")
        return False

def test_existing_endpoints():
    """Test existing chatbot endpoints"""
    print("\nTesting existing chatbot endpoints...")
    
    # Test persona endpoint
    try:
        response = requests.get(f"{API_URL}/persona/bob")
        if response.status_code == 200:
            print("✅ Persona endpoint working")
        else:
            print(f"⚠️  Persona endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Persona endpoint error: {e}")

def main():
    print("=" * 60)
    print("Survey API Test Suite")
    print("=" * 60)
    print(f"Testing API at: {API_URL}")
    print()
    
    # Run tests
    tests_passed = []
    
    # Test 1: Health check
    tests_passed.append(test_health_check())
    
    # Test 2: Survey submission
    participant_id = test_survey_submission()
    tests_passed.append(participant_id is not None)
    
    # Test 3: Survey retrieval
    tests_passed.append(test_survey_retrieval(participant_id))
    
    # Test 4: Existing endpoints
    test_existing_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(tests_passed)
    total = len(tests_passed)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("\nNext steps:")
    print("1. Open frontend/landing.html in your browser")
    print("2. Complete the survey")
    print("3. Check survey_responses/ directory for saved data")
    print()

if __name__ == "__main__":
    main()

