#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_import_service import DataImportService

def test_transformation():
    print("🧪 Testing current ID transformation logic...")
    
    # Create service instance
    service = DataImportService()
    
    # Test sub_category_id transformations for different domains
    test_cases = [
        ('P004-1', 'stress'),
        ('P001-1', 'anxiety'),
        ('P005-1', 'trauma'),
        ('P004-8', 'stress'),
        ('P001-9', 'anxiety'),
        ('P005-8', 'trauma')
    ]
    
    print("\n📊 Testing sub_category_id transformations:")
    for original_id, domain in test_cases:
        transformed = service._transform_sub_category_id(original_id, domain)
        print(f"  {original_id} ({domain}) -> {transformed}")
    
    # Test category_id transformations
    print("\n📊 Testing category_id transformations:")
    category_test_cases = [
        ('P004', 'stress'),
        ('P001', 'anxiety'),
        ('P005', 'trauma')
    ]
    
    for original_id, domain in category_test_cases:
        transformed = service._transform_category_id(original_id, domain)
        print(f"  {original_id} ({domain}) -> {transformed}")
    
    print("\n✅ Transformation test completed!")

if __name__ == "__main__":
    test_transformation()