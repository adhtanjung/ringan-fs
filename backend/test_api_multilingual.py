#!/usr/bin/env python3
"""
Test script for multilingual API functionality
Tests the chat endpoints with both English and Indonesian inputs
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"Health Status: {health_data.get('status', 'unknown')}")
            print("Services:")
            for service, status in health_data.get('services', {}).items():
                print(f"  - {service}: {status.get('status', 'unknown')}")
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"API: {data.get('message', 'unknown')}")
            print(f"Version: {data.get('version', 'unknown')}")
            print(f"Features: {len(data.get('features', []))} available")
            return True
        else:
            print(f"Root endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"Root endpoint error: {e}")
        return False

def test_chat_endpoint(message, language, test_name):
    """Test the chat endpoint with a specific message"""
    print(f"\n=== Testing Chat: {test_name} ===")
    print(f"Input ({language}): {message}")
    
    try:
        # Test the chat endpoint at /api/v1/chat/chat
        chat_data = {
            "message": message,
            "session_data": {
                "user_name": "Test User",
                "session_id": f"test_{int(time.time())}"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('message', 'No message')}")
            print(f"Detected Language: {result.get('detected_language', 'unknown')}")
            print(f"Sentiment: {result.get('sentiment', 'unknown')}")
            return True
        else:
            print(f"Chat request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Chat test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Multilingual Chat API")
    print("=" * 50)
    
    # Test basic endpoints first
    health_ok = test_health_endpoint()
    root_ok = test_root_endpoint()
    
    if not (health_ok and root_ok):
        print("\n❌ Basic endpoints failed. Skipping chat tests.")
        return
    
    # Test multilingual chat functionality
    test_cases = [
        {
            "message": "Hello, I'm feeling anxious today. Can you help me?",
            "language": "English",
            "test_name": "English Anxiety"
        },
        {
            "message": "Saya merasa stres dengan pekerjaan. Apa yang harus saya lakukan?",
            "language": "Indonesian",
            "test_name": "Indonesian Stress"
        },
        {
            "message": "I'm having trouble sleeping and feel overwhelmed.",
            "language": "English",
            "test_name": "English Sleep Issues"
        },
        {
            "message": "Saya sedang mengalami masalah dalam hubungan dan merasa sedih.",
            "language": "Indonesian",
            "test_name": "Indonesian Relationship"
        }
    ]
    
    chat_results = []
    for test_case in test_cases:
        result = test_chat_endpoint(
            test_case["message"],
            test_case["language"],
            test_case["test_name"]
        )
        chat_results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"Health Endpoint: {'✅' if health_ok else '❌'}")
    print(f"Root Endpoint: {'✅' if root_ok else '❌'}")
    print(f"Chat Tests: {sum(chat_results)}/{len(chat_results)} passed")
    
    if all([health_ok, root_ok] + chat_results):
        print("\n🎉 All tests passed! Multilingual functionality is working.")
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()