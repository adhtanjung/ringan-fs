#!/usr/bin/env python3
"""
Simple test runner for Master Tables endpoints

This script runs a subset of the most important tests to verify
that the master tables endpoints are working correctly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1/admin/dataset"
PROBLEM_TYPES_URL = f"{BASE_URL}/problem_types"
DOMAIN_TYPES_URL = f"{BASE_URL}/domain_types"

def make_request(method, url, data=None, params=None):
    """Make HTTP request and return response"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return response
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Make sure the backend server is running on {BASE_URL}")
        return None
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def test_problem_types_crud():
    """Test Problem Types CRUD operations"""
    print("\n🧪 Testing Problem Types CRUD...")

    # Test data
    test_data = {
        "type_name": "Test Anxiety",
        "description": "Test anxiety disorder for testing",
        "is_active": True
    }

    updated_data = {
        "type_name": "Updated Test Anxiety",
        "description": "Updated test anxiety disorder",
        "is_active": False
    }

    # CREATE
    print("  📝 Testing CREATE...")
    response = make_request("POST", PROBLEM_TYPES_URL, data=test_data)
    if not response:
        return False

    if response.status_code == 201:
        print("    ✅ CREATE successful")
        created_id = response.json()["data"]["id"]
    else:
        print(f"    ❌ CREATE failed: {response.status_code} - {response.text}")
        return False

    # READ (by ID)
    print("  📖 Testing READ by ID...")
    response = make_request("GET", f"{PROBLEM_TYPES_URL}/{created_id}")
    if response and response.status_code == 200:
        print("    ✅ READ by ID successful")
    else:
        print(f"    ❌ READ by ID failed: {response.status_code if response else 'No response'}")
        return False

    # UPDATE
    print("  ✏️  Testing UPDATE...")
    response = make_request("PUT", f"{PROBLEM_TYPES_URL}/{created_id}", data=updated_data)
    if response and response.status_code == 200:
        print("    ✅ UPDATE successful")
    else:
        print(f"    ❌ UPDATE failed: {response.status_code if response else 'No response'}")
        return False

    # READ (list)
    print("  📋 Testing READ list...")
    response = make_request("GET", PROBLEM_TYPES_URL)
    if response and response.status_code == 200:
        data = response.json()
        if "data" in data and "items" in data["data"]:
            print(f"    ✅ READ list successful ({len(data['data']['items'])} items)")
        else:
            print("    ❌ READ list failed: Invalid response structure")
            return False
    else:
        print(f"    ❌ READ list failed: {response.status_code if response else 'No response'}")
        return False

    # DELETE
    print("  🗑️  Testing DELETE...")
    response = make_request("DELETE", f"{PROBLEM_TYPES_URL}/{created_id}")
    if response and response.status_code == 200:
        print("    ✅ DELETE successful")
    else:
        print(f"    ❌ DELETE failed: {response.status_code if response else 'No response'}")
        return False

    # Verify deletion
    response = make_request("GET", f"{PROBLEM_TYPES_URL}/{created_id}")
    if response and response.status_code == 404:
        print("    ✅ Deletion verified")
    else:
        print(f"    ❌ Deletion verification failed: {response.status_code if response else 'No response'}")
        return False

    return True

def test_domain_types_crud():
    """Test Domain Types CRUD operations"""
    print("\n🧪 Testing Domain Types CRUD...")

    # Test data
    test_data = {
        "domain_name": "Test Stress",
        "domain_code": "TST",
        "description": "Test stress domain for testing",
        "is_active": True
    }

    updated_data = {
        "domain_name": "Updated Test Stress",
        "domain_code": "UTS",
        "description": "Updated test stress domain",
        "is_active": False
    }

    # CREATE
    print("  📝 Testing CREATE...")
    response = make_request("POST", DOMAIN_TYPES_URL, data=test_data)
    if not response:
        return False

    if response.status_code == 201:
        print("    ✅ CREATE successful")
        created_id = response.json()["data"]["id"]
    else:
        print(f"    ❌ CREATE failed: {response.status_code} - {response.text}")
        return False

    # READ (by ID)
    print("  📖 Testing READ by ID...")
    response = make_request("GET", f"{DOMAIN_TYPES_URL}/{created_id}")
    if response and response.status_code == 200:
        print("    ✅ READ by ID successful")
    else:
        print(f"    ❌ READ by ID failed: {response.status_code if response else 'No response'}")
        return False

    # UPDATE
    print("  ✏️  Testing UPDATE...")
    response = make_request("PUT", f"{DOMAIN_TYPES_URL}/{created_id}", data=updated_data)
    if response and response.status_code == 200:
        print("    ✅ UPDATE successful")
    else:
        print(f"    ❌ UPDATE failed: {response.status_code if response else 'No response'}")
        return False

    # READ (list)
    print("  📋 Testing READ list...")
    response = make_request("GET", DOMAIN_TYPES_URL)
    if response and response.status_code == 200:
        data = response.json()
        if "data" in data and "items" in data["data"]:
            print(f"    ✅ READ list successful ({len(data['data']['items'])} items)")
        else:
            print("    ❌ READ list failed: Invalid response structure")
            return False
    else:
        print(f"    ❌ READ list failed: {response.status_code if response else 'No response'}")
        return False

    # DELETE
    print("  🗑️  Testing DELETE...")
    response = make_request("DELETE", f"{DOMAIN_TYPES_URL}/{created_id}")
    if response and response.status_code == 200:
        print("    ✅ DELETE successful")
    else:
        print(f"    ❌ DELETE failed: {response.status_code if response else 'No response'}")
        return False

    # Verify deletion
    response = make_request("GET", f"{DOMAIN_TYPES_URL}/{created_id}")
    if response and response.status_code == 404:
        print("    ✅ Deletion verified")
    else:
        print(f"    ❌ Deletion verification failed: {response.status_code if response else 'No response'}")
        return False

    return True

def test_filtering_and_pagination():
    """Test filtering and pagination functionality"""
    print("\n🧪 Testing Filtering and Pagination...")

    # Test pagination
    print("  📄 Testing pagination...")
    response = make_request("GET", PROBLEM_TYPES_URL, params={"skip": 0, "limit": 5})
    if response and response.status_code == 200:
        data = response.json()
        if "data" in data and "items" in data["data"]:
            print(f"    ✅ Pagination successful ({len(data['data']['items'])} items)")
        else:
            print("    ❌ Pagination failed: Invalid response structure")
            return False
    else:
        print(f"    ❌ Pagination failed: {response.status_code if response else 'No response'}")
        return False

    # Test filtering by active status
    print("  🔍 Testing filtering by active status...")
    response = make_request("GET", PROBLEM_TYPES_URL, params={"is_active": True})
    if response and response.status_code == 200:
        data = response.json()
        if "data" in data and "items" in data["data"]:
            print(f"    ✅ Active filtering successful ({len(data['data']['items'])} active items)")
        else:
            print("    ❌ Active filtering failed: Invalid response structure")
            return False
    else:
        print(f"    ❌ Active filtering failed: {response.status_code if response else 'No response'}")
        return False

    return True

def test_error_handling():
    """Test error handling"""
    print("\n🧪 Testing Error Handling...")

    # Test invalid ID
    print("  🚫 Testing invalid ID...")
    response = make_request("GET", f"{PROBLEM_TYPES_URL}/invalid-id")
    if response and response.status_code in [404, 422]:
        print("    ✅ Invalid ID handled correctly")
    else:
        print(f"    ❌ Invalid ID handling failed: {response.status_code if response else 'No response'}")
        return False

    # Test validation error
    print("  📝 Testing validation error...")
    invalid_data = {
        "type_name": "",  # Empty name should fail validation
        "description": "Test description"
    }
    response = make_request("POST", PROBLEM_TYPES_URL, data=invalid_data)
    if response and response.status_code == 422:
        print("    ✅ Validation error handled correctly")
    else:
        print(f"    ❌ Validation error handling failed: {response.status_code if response else 'No response'}")
        return False

    return True

def main():
    """Run all tests"""
    print("🧪 Master Tables Endpoints Test Suite")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing endpoints at: {BASE_URL}")

    # Check if server is running
    print("\n🔍 Checking server connectivity...")
    response = make_request("GET", PROBLEM_TYPES_URL)
    if not response:
        print("❌ Cannot connect to server. Make sure the backend is running on http://localhost:8000")
        sys.exit(1)
    print("✅ Server is running")

    # Run tests
    tests = [
        ("Problem Types CRUD", test_problem_types_crud),
        ("Domain Types CRUD", test_domain_types_crud),
        ("Filtering and Pagination", test_filtering_and_pagination),
        ("Error Handling", test_error_handling)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"\n❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"\n💥 {test_name}: ERROR - {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results:")
    print(f"   Total Tests: {len(tests)}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Success Rate: {(passed/len(tests))*100:.1f}%")

    if failed == 0:
        print("\n🎉 All tests passed! Master tables endpoints are working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



