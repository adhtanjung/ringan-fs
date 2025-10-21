#!/usr/bin/env python3
"""
Simple test script for Master Tables endpoints

This script performs basic CRUD operations to verify that the
master tables endpoints are working correctly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1/admin/dataset"
PROBLEM_TYPES_URL = f"{BASE_URL}/problem_types"
DOMAIN_TYPES_URL = f"{BASE_URL}/domain_types"

def test_problem_types():
    """Test Problem Types CRUD operations"""
    print("\n🧪 Testing Problem Types...")

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

    try:
        # CREATE
        print("  📝 Testing CREATE...")
        response = requests.post(PROBLEM_TYPES_URL, json=test_data)
        if response.status_code == 201:
            print("    ✅ CREATE successful")
            created_id = response.json()["data"]["id"]
        else:
            print(f"    ❌ CREATE failed: {response.status_code} - {response.text}")
            return False

        # READ (by ID)
        print("  📖 Testing READ by ID...")
        response = requests.get(f"{PROBLEM_TYPES_URL}/{created_id}")
        if response.status_code == 200:
            print("    ✅ READ by ID successful")
        else:
            print(f"    ❌ READ by ID failed: {response.status_code}")
            return False

        # UPDATE
        print("  ✏️  Testing UPDATE...")
        response = requests.put(f"{PROBLEM_TYPES_URL}/{created_id}", json=updated_data)
        if response.status_code == 200:
            print("    ✅ UPDATE successful")
        else:
            print(f"    ❌ UPDATE failed: {response.status_code}")
            return False

        # READ (list)
        print("  📋 Testing READ list...")
        response = requests.get(PROBLEM_TYPES_URL)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "items" in data["data"]:
                print(f"    ✅ READ list successful ({len(data['data']['items'])} items)")
            else:
                print("    ❌ READ list failed: Invalid response structure")
                return False
        else:
            print(f"    ❌ READ list failed: {response.status_code}")
            return False

        # DELETE
        print("  🗑️  Testing DELETE...")
        response = requests.delete(f"{PROBLEM_TYPES_URL}/{created_id}")
        if response.status_code == 200:
            print("    ✅ DELETE successful")
        else:
            print(f"    ❌ DELETE failed: {response.status_code}")
            return False

        # Verify deletion
        print("  🔍 Verifying deletion...")
        response = requests.get(f"{PROBLEM_TYPES_URL}/{created_id}")
        if response.status_code == 404:
            print("    ✅ Deletion verified")
        else:
            print(f"    ❌ Deletion verification failed: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"    💥 Error during testing: {e}")
        return False

def test_domain_types():
    """Test Domain Types CRUD operations"""
    print("\n🧪 Testing Domain Types...")

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

    try:
        # CREATE
        print("  📝 Testing CREATE...")
        response = requests.post(DOMAIN_TYPES_URL, json=test_data)
        if response.status_code == 201:
            print("    ✅ CREATE successful")
            created_id = response.json()["data"]["id"]
        else:
            print(f"    ❌ CREATE failed: {response.status_code} - {response.text}")
            return False

        # READ (by ID)
        print("  📖 Testing READ by ID...")
        response = requests.get(f"{DOMAIN_TYPES_URL}/{created_id}")
        if response.status_code == 200:
            print("    ✅ READ by ID successful")
        else:
            print(f"    ❌ READ by ID failed: {response.status_code}")
            return False

        # UPDATE
        print("  ✏️  Testing UPDATE...")
        response = requests.put(f"{DOMAIN_TYPES_URL}/{created_id}", json=updated_data)
        if response.status_code == 200:
            print("    ✅ UPDATE successful")
        else:
            print(f"    ❌ UPDATE failed: {response.status_code}")
            return False

        # READ (list)
        print("  📋 Testing READ list...")
        response = requests.get(DOMAIN_TYPES_URL)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "items" in data["data"]:
                print(f"    ✅ READ list successful ({len(data['data']['items'])} items)")
            else:
                print("    ❌ READ list failed: Invalid response structure")
                return False
        else:
            print(f"    ❌ READ list failed: {response.status_code}")
            return False

        # DELETE
        print("  🗑️  Testing DELETE...")
        response = requests.delete(f"{DOMAIN_TYPES_URL}/{created_id}")
        if response.status_code == 200:
            print("    ✅ DELETE successful")
        else:
            print(f"    ❌ DELETE failed: {response.status_code}")
            return False

        # Verify deletion
        print("  🔍 Verifying deletion...")
        response = requests.get(f"{DOMAIN_TYPES_URL}/{created_id}")
        if response.status_code == 404:
            print("    ✅ Deletion verified")
        else:
            print(f"    ❌ Deletion verification failed: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"    💥 Error during testing: {e}")
        return False

def test_filtering():
    """Test filtering and pagination"""
    print("\n🧪 Testing Filtering and Pagination...")

    try:
        # Test pagination
        print("  📄 Testing pagination...")
        response = requests.get(f"{PROBLEM_TYPES_URL}?skip=0&limit=5")
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "items" in data["data"]:
                print(f"    ✅ Pagination successful ({len(data['data']['items'])} items)")
            else:
                print("    ❌ Pagination failed: Invalid response structure")
                return False
        else:
            print(f"    ❌ Pagination failed: {response.status_code}")
            return False

        # Test filtering by active status
        print("  🔍 Testing filtering by active status...")
        response = requests.get(f"{PROBLEM_TYPES_URL}?is_active=true")
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "items" in data["data"]:
                print(f"    ✅ Active filtering successful ({len(data['data']['items'])} active items)")
            else:
                print("    ❌ Active filtering failed: Invalid response structure")
                return False
        else:
            print(f"    ❌ Active filtering failed: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"    💥 Error during testing: {e}")
        return False

def test_validation():
    """Test validation and error handling"""
    print("\n🧪 Testing Validation and Error Handling...")

    try:
        # Test validation error
        print("  📝 Testing validation error...")
        invalid_data = {
            "type_name": "",  # Empty name should fail validation
            "description": "Test description"
        }
        response = requests.post(PROBLEM_TYPES_URL, json=invalid_data)
        if response.status_code in [400, 422]:
            print("    ✅ Validation error handled correctly")
        else:
            print(f"    ❌ Validation error handling failed: {response.status_code}")
            return False

        # Test invalid ID
        print("  🚫 Testing invalid ID...")
        response = requests.get(f"{PROBLEM_TYPES_URL}/invalid-id")
        if response.status_code in [404, 422]:
            print("    ✅ Invalid ID handled correctly")
        else:
            print(f"    ❌ Invalid ID handling failed: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"    💥 Error during testing: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Simple Master Tables Endpoints Test")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing endpoints at: {BASE_URL}")

    # Check if server is running
    print("\n🔍 Checking server connectivity...")
    try:
        response = requests.get(PROBLEM_TYPES_URL)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

    # Run tests
    tests = [
        ("Problem Types CRUD", test_problem_types),
        ("Domain Types CRUD", test_domain_types),
        ("Filtering and Pagination", test_filtering),
        ("Validation and Error Handling", test_validation)
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
