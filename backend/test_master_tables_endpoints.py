#!/usr/bin/env python3
"""
Comprehensive tests for Master Tables endpoints (Problem Types and Domain Types)

Tests all CRUD operations for both problem_types and domain_types endpoints
including validation, error handling, and edge cases.
"""

import pytest
import asyncio
from datetime import datetime
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from app.models.dataset_models import ProblemTypeModel, DomainTypeModel
from app.core.config import settings

# Test client
client = TestClient(app)

class TestProblemTypesEndpoints:
    """Test suite for Problem Types CRUD endpoints"""

    def setup_method(self):
        """Setup test data before each test method"""
        self.base_url = "/api/v1/admin/dataset/problem_types"
        self.valid_problem_type = {
            "type_name": "Test Anxiety",
            "description": "Test anxiety disorder for testing purposes",
            "is_active": True
        }
        self.updated_problem_type = {
            "type_name": "Updated Anxiety",
            "description": "Updated description for testing",
            "is_active": False
        }
        self.created_id = None

    def test_create_problem_type_success(self):
        """Test successful creation of a problem type"""
        response = client.post(self.base_url, json=self.valid_problem_type)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data

        # Store the created ID for cleanup
        self.created_id = data["data"]["id"]

        # Verify the created data
        created_data = data["data"]
        assert created_data["type_name"] == self.valid_problem_type["type_name"]
        assert created_data["description"] == self.valid_problem_type["description"]
        assert created_data["is_active"] == self.valid_problem_type["is_active"]
        assert "created_at" in created_data
        assert "updated_at" in created_data

    def test_create_problem_type_validation_error(self):
        """Test creation with validation errors"""
        invalid_data = {
            "type_name": "",  # Empty name should fail validation
            "description": "Test description"
        }

        response = client.post(self.base_url, json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_problem_type_missing_required_fields(self):
        """Test creation with missing required fields"""
        incomplete_data = {
            "description": "Test description"
            # Missing type_name
        }

        response = client.post(self.base_url, json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_get_problem_types_list(self):
        """Test retrieving list of problem types"""
        response = client.get(self.base_url)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

        # Verify response structure
        response_data = data["data"]
        assert "items" in response_data
        assert "total" in response_data
        assert "skip" in response_data
        assert "limit" in response_data
        assert "has_more" in response_data

    def test_get_problem_types_with_filters(self):
        """Test retrieving problem types with filters"""
        # Test with is_active filter
        response = client.get(f"{self.base_url}?is_active=true")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

        # Test with pagination
        response = client.get(f"{self.base_url}?skip=0&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

    def test_get_problem_type_by_id(self):
        """Test retrieving a specific problem type by ID"""
        # First create a problem type
        create_response = client.post(self.base_url, json=self.valid_problem_type)
        assert create_response.status_code == 201
        created_id = create_response.json()["data"]["id"]

        # Then retrieve it
        response = client.get(f"{self.base_url}/{created_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == created_id
        assert data["data"]["type_name"] == self.valid_problem_type["type_name"]

    def test_get_problem_type_not_found(self):
        """Test retrieving a non-existent problem type"""
        fake_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but non-existent
        response = client.get(f"{self.base_url}/{fake_id}")
        assert response.status_code == 404

    def test_update_problem_type_success(self):
        """Test successful update of a problem type"""
        # First create a problem type
        create_response = client.post(self.base_url, json=self.valid_problem_type)
        assert create_response.status_code == 201
        created_id = create_response.json()["data"]["id"]

        # Then update it
        response = client.put(f"{self.base_url}/{created_id}", json=self.updated_problem_type)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["type_name"] == self.updated_problem_type["type_name"]
        assert data["data"]["description"] == self.updated_problem_type["description"]
        assert data["data"]["is_active"] == self.updated_problem_type["is_active"]

    def test_update_problem_type_not_found(self):
        """Test updating a non-existent problem type"""
        fake_id = "507f1f77bcf86cd799439011"
        response = client.put(f"{self.base_url}/{fake_id}", json=self.updated_problem_type)
        assert response.status_code == 404

    def test_delete_problem_type_success(self):
        """Test successful deletion of a problem type"""
        # First create a problem type
        create_response = client.post(self.base_url, json=self.valid_problem_type)
        assert create_response.status_code == 201
        created_id = create_response.json()["data"]["id"]

        # Then delete it
        response = client.delete(f"{self.base_url}/{created_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "message" in data

        # Verify it's actually deleted
        get_response = client.get(f"{self.base_url}/{created_id}")
        assert get_response.status_code == 404

    def test_delete_problem_type_not_found(self):
        """Test deleting a non-existent problem type"""
        fake_id = "507f1f77bcf86cd799439011"
        response = client.delete(f"{self.base_url}/{fake_id}")
        assert response.status_code == 404


class TestDomainTypesEndpoints:
    """Test suite for Domain Types CRUD endpoints"""

    def setup_method(self):
        """Setup test data before each test method"""
        self.base_url = "/api/v1/admin/dataset/domain_types"
        self.valid_domain_type = {
            "domain_name": "Test Stress",
            "domain_code": "TST",
            "description": "Test stress domain for testing purposes",
            "is_active": True
        }
        self.updated_domain_type = {
            "domain_name": "Updated Stress",
            "domain_code": "UST",
            "description": "Updated description for testing",
            "is_active": False
        }
        self.created_id = None

    def test_create_domain_type_success(self):
        """Test successful creation of a domain type"""
        response = client.post(self.base_url, json=self.valid_domain_type)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data

        # Store the created ID for cleanup
        self.created_id = data["data"]["id"]

        # Verify the created data
        created_data = data["data"]
        assert created_data["domain_name"] == self.valid_domain_type["domain_name"]
        assert created_data["domain_code"] == self.valid_domain_type["domain_code"]
        assert created_data["description"] == self.valid_domain_type["description"]
        assert created_data["is_active"] == self.valid_domain_type["is_active"]
        assert "created_at" in created_data
        assert "updated_at" in created_data

    def test_create_domain_type_validation_error(self):
        """Test creation with validation errors"""
        invalid_data = {
            "domain_name": "",  # Empty name should fail validation
            "domain_code": "TST",
            "description": "Test description"
        }

        response = client.post(self.base_url, json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_domain_type_missing_required_fields(self):
        """Test creation with missing required fields"""
        incomplete_data = {
            "domain_name": "Test Domain"
            # Missing domain_code
        }

        response = client.post(self.base_url, json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_get_domain_types_list(self):
        """Test retrieving list of domain types"""
        response = client.get(self.base_url)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

        # Verify response structure
        response_data = data["data"]
        assert "items" in response_data
        assert "total" in response_data
        assert "skip" in response_data
        assert "limit" in response_data
        assert "has_more" in response_data

    def test_get_domain_types_with_filters(self):
        """Test retrieving domain types with filters"""
        # Test with is_active filter
        response = client.get(f"{self.base_url}?is_active=true")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

        # Test with pagination
        response = client.get(f"{self.base_url}?skip=0&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

    def test_get_domain_type_by_id(self):
        """Test retrieving a specific domain type by ID"""
        # First create a domain type
        create_response = client.post(self.base_url, json=self.valid_domain_type)
        assert create_response.status_code == 201
        created_id = create_response.json()["data"]["id"]

        # Then retrieve it
        response = client.get(f"{self.base_url}/{created_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == created_id
        assert data["data"]["domain_name"] == self.valid_domain_type["domain_name"]
        assert data["data"]["domain_code"] == self.valid_domain_type["domain_code"]

    def test_get_domain_type_not_found(self):
        """Test retrieving a non-existent domain type"""
        fake_id = "507f1f77bcf86cd799439011"
        response = client.get(f"{self.base_url}/{fake_id}")
        assert response.status_code == 404

    def test_update_domain_type_success(self):
        """Test successful update of a domain type"""
        # First create a domain type
        create_response = client.post(self.base_url, json=self.valid_domain_type)
        assert create_response.status_code == 201
        created_id = create_response.json()["data"]["id"]

        # Then update it
        response = client.put(f"{self.base_url}/{created_id}", json=self.updated_domain_type)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["domain_name"] == self.updated_domain_type["domain_name"]
        assert data["data"]["domain_code"] == self.updated_domain_type["domain_code"]
        assert data["data"]["description"] == self.updated_domain_type["description"]
        assert data["data"]["is_active"] == self.updated_domain_type["is_active"]

    def test_update_domain_type_not_found(self):
        """Test updating a non-existent domain type"""
        fake_id = "507f1f77bcf86cd799439011"
        response = client.put(f"{self.base_url}/{fake_id}", json=self.updated_domain_type)
        assert response.status_code == 404

    def test_delete_domain_type_success(self):
        """Test successful deletion of a domain type"""
        # First create a domain type
        create_response = client.post(self.base_url, json=self.valid_domain_type)
        assert create_response.status_code == 201
        created_id = create_response.json()["data"]["id"]

        # Then delete it
        response = client.delete(f"{self.base_url}/{created_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "message" in data

        # Verify it's actually deleted
        get_response = client.get(f"{self.base_url}/{created_id}")
        assert get_response.status_code == 404

    def test_delete_domain_type_not_found(self):
        """Test deleting a non-existent domain type"""
        fake_id = "507f1f77bcf86cd799439011"
        response = client.delete(f"{self.base_url}/{fake_id}")
        assert response.status_code == 404


class TestMasterTablesIntegration:
    """Integration tests for master tables functionality"""

    def test_problem_types_crud_workflow(self):
        """Test complete CRUD workflow for problem types"""
        base_url = "/api/v1/admin/dataset/problem_types"

        # Create
        problem_type_data = {
            "type_name": "Integration Test Anxiety",
            "description": "Integration test problem type",
            "is_active": True
        }

        create_response = client.post(base_url, json=problem_type_data)
        assert create_response.status_code == 201
        created_id = create_response.json()["data"]["id"]

        # Read
        get_response = client.get(f"{base_url}/{created_id}")
        assert get_response.status_code == 200
        assert get_response.json()["data"]["type_name"] == problem_type_data["type_name"]

        # Update
        updated_data = {
            "type_name": "Updated Integration Test",
            "description": "Updated integration test",
            "is_active": False
        }

        update_response = client.put(f"{base_url}/{created_id}", json=updated_data)
        assert update_response.status_code == 200
        assert update_response.json()["data"]["type_name"] == updated_data["type_name"]

        # Delete
        delete_response = client.delete(f"{base_url}/{created_id}")
        assert delete_response.status_code == 200

        # Verify deletion
        final_get_response = client.get(f"{base_url}/{created_id}")
        assert final_get_response.status_code == 404

    def test_domain_types_crud_workflow(self):
        """Test complete CRUD workflow for domain types"""
        base_url = "/api/v1/admin/dataset/domain_types"

        # Create
        domain_type_data = {
            "domain_name": "Integration Test Domain",
            "domain_code": "ITD",
            "description": "Integration test domain type",
            "is_active": True
        }

        create_response = client.post(base_url, json=domain_type_data)
        assert create_response.status_code == 201
        created_id = create_response.json()["data"]["id"]

        # Read
        get_response = client.get(f"{base_url}/{created_id}")
        assert get_response.status_code == 200
        assert get_response.json()["data"]["domain_name"] == domain_type_data["domain_name"]

        # Update
        updated_data = {
            "domain_name": "Updated Integration Test",
            "domain_code": "UIT",
            "description": "Updated integration test",
            "is_active": False
        }

        update_response = client.put(f"{base_url}/{created_id}", json=updated_data)
        assert update_response.status_code == 200
        assert update_response.json()["data"]["domain_name"] == updated_data["domain_name"]

        # Delete
        delete_response = client.delete(f"{base_url}/{created_id}")
        assert delete_response.status_code == 200

        # Verify deletion
        final_get_response = client.get(f"{base_url}/{created_id}")
        assert final_get_response.status_code == 404

    def test_pagination_and_filtering(self):
        """Test pagination and filtering functionality"""
        # Test problem types pagination
        problem_types_url = "/api/v1/admin/dataset/problem_types"

        # Create multiple test records
        for i in range(5):
            data = {
                "type_name": f"Test Problem Type {i}",
                "description": f"Test description {i}",
                "is_active": i % 2 == 0  # Alternate active/inactive
            }
            response = client.post(problem_types_url, json=data)
            assert response.status_code == 201

        # Test pagination
        response = client.get(f"{problem_types_url}?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) <= 3

        # Test filtering by active status
        response = client.get(f"{problem_types_url}?is_active=true")
        assert response.status_code == 200
        data = response.json()
        for item in data["data"]["items"]:
            assert item["is_active"] is True

        # Test domain types pagination
        domain_types_url = "/api/v1/admin/dataset/domain_types"

        # Create multiple test records
        for i in range(5):
            data = {
                "domain_name": f"Test Domain {i}",
                "domain_code": f"TD{i}",
                "description": f"Test description {i}",
                "is_active": i % 2 == 0  # Alternate active/inactive
            }
            response = client.post(domain_types_url, json=data)
            assert response.status_code == 201

        # Test pagination
        response = client.get(f"{domain_types_url}?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) <= 3

        # Test filtering by active status
        response = client.get(f"{domain_types_url}?is_active=false")
        assert response.status_code == 200
        data = response.json()
        for item in data["data"]["items"]:
            assert item["is_active"] is False


class TestMasterTablesErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_json_payload(self):
        """Test handling of invalid JSON payloads"""
        # Test with malformed JSON
        response = client.post(
            "/api/v1/admin/dataset/problem_types",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_invalid_object_id_format(self):
        """Test handling of invalid ObjectId formats"""
        invalid_ids = [
            "invalid-id",
            "123",
            "not-an-object-id",
            ""
        ]

        for invalid_id in invalid_ids:
            # Test GET
            response = client.get(f"/api/v1/admin/dataset/problem_types/{invalid_id}")
            assert response.status_code in [404, 422]  # Either not found or validation error

            # Test PUT
            response = client.put(
                f"/api/v1/admin/dataset/problem_types/{invalid_id}",
                json={"type_name": "Test", "description": "Test"}
            )
            assert response.status_code in [404, 422]

            # Test DELETE
            response = client.delete(f"/api/v1/admin/dataset/problem_types/{invalid_id}")
            assert response.status_code in [404, 422]

    def test_large_payload_handling(self):
        """Test handling of large payloads"""
        # Test with very long strings
        large_data = {
            "type_name": "A" * 1000,  # Very long name
            "description": "B" * 10000,  # Very long description
            "is_active": True
        }

        response = client.post("/api/v1/admin/dataset/problem_types", json=large_data)
        # Should either succeed or fail gracefully with validation error
        assert response.status_code in [201, 422]

    def test_special_characters_in_data(self):
        """Test handling of special characters in data"""
        special_data = {
            "type_name": "Test with émojis 🎉 and spëcial chars",
            "description": "Description with unicode: αβγδε and symbols: @#$%^&*()",
            "is_active": True
        }

        response = client.post("/api/v1/admin/dataset/problem_types", json=special_data)
        assert response.status_code == 201

        # Verify the data was stored correctly
        data = response.json()
        assert data["data"]["type_name"] == special_data["type_name"]
        assert data["data"]["description"] == special_data["description"]


def run_tests():
    """Run all tests"""
    print("🧪 Running Master Tables Endpoints Tests...")
    print("=" * 60)

    # Test classes to run
    test_classes = [
        TestProblemTypesEndpoints,
        TestDomainTypesEndpoints,
        TestMasterTablesIntegration,
        TestMasterTablesErrorHandling
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}...")

        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]

        for test_method in test_methods:
            total_tests += 1
            try:
                # Create instance and run test
                instance = test_class()
                instance.setup_method()
                getattr(instance, test_method)()
                print(f"  ✅ {test_method}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {test_method}: {str(e)}")
                failed_tests += 1

    print("\n" + "=" * 60)
    print(f"📊 Test Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    if failed_tests == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed_tests} tests failed!")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)



