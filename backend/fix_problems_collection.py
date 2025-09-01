#!/usr/bin/env python3
"""
Fix the problems collection by properly mapping problem names to categories
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Problem name to category mapping
PROBLEM_CATEGORY_MAPPING = {
    "Stress": "Stress",
    "Stress - panic atttack ?": "Stress", 
    "Workplace Stress": "Stress",
    "Exam Anxiety": "Anxiety",
    "Anxiety": "Anxiety",
    "Depression": "Depression",
    "Low Self-Esteem": "Depression",
    "Suicidal thoughts": "Depression",
    "Emotional Regulation": "General",
    "Trauma": "Trauma",
    "PTSD": "Trauma",
    "Grief": "General",
    "Relationship Issues": "General",
    "Social Anxiety": "Anxiety",
    "Panic Disorder": "Anxiety"
}

# Category to sub-category mapping
CATEGORY_SUBCATEGORY_MAPPING = {
    "Stress": {
        "Workplace Stress": "work_stress",
        "Exam Stress": "academic_stress",
        "General Stress": "general_stress"
    },
    "Anxiety": {
        "Social Anxiety": "social_anxiety",
        "Exam Anxiety": "academic_anxiety",
        "General Anxiety": "general_anxiety"
    },
    "Depression": {
        "Major Depression": "major_depression",
        "Low Self-Esteem": "self_esteem",
        "Suicidal Ideation": "suicidal_thoughts"
    },
    "Trauma": {
        "PTSD": "ptsd",
        "Acute Trauma": "acute_trauma"
    },
    "General": {
        "Emotional Regulation": "emotional_regulation",
        "Relationship Issues": "relationships",
        "Grief": "grief"
    }
}

async def fix_problems_collection():
    """
    Fix the problems collection by updating category and sub-category information
    """
    
    print("=== Fixing Problems Collection ===")
    
    # Initialize Qdrant client
    client = QdrantClient(
        url=settings.QDRANT_URL
    )
    
    collection_name = "mental-health-problems"
    
    try:
        # Get all points
        print("\n--- Getting all points ---")
        points = client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True,
            with_vectors=True
        )[0]
        
        print(f"Found {len(points)} points to update")
        
        updated_points = []
        
        for point in points:
            payload = point.payload
            problem_name = payload.get("problem_name", "")
            
            # Determine category
            category = PROBLEM_CATEGORY_MAPPING.get(problem_name, "General")
            
            # Determine sub-category
            sub_category_id = None
            if category in CATEGORY_SUBCATEGORY_MAPPING:
                # Try to find a matching sub-category
                for sub_name, sub_id in CATEGORY_SUBCATEGORY_MAPPING[category].items():
                    if sub_name.lower() in problem_name.lower() or problem_name.lower() in sub_name.lower():
                        sub_category_id = sub_id
                        break
                
                # Default sub-category if no specific match
                if not sub_category_id:
                    if category == "Stress":
                        sub_category_id = "general_stress"
                    elif category == "Anxiety":
                        sub_category_id = "general_anxiety"
                    elif category == "Depression":
                        sub_category_id = "major_depression"
                    elif category == "Trauma":
                        sub_category_id = "acute_trauma"
                    else:
                        sub_category_id = "general"
            
            # Generate category_id
            category_id = category.lower().replace(" ", "_")
            
            # Update payload
            updated_payload = payload.copy()
            updated_payload["category"] = category
            updated_payload["category_id"] = category_id
            updated_payload["sub_category_id"] = sub_category_id
            
            # Ensure problem_id exists
            if not updated_payload.get("problem_id"):
                updated_payload["problem_id"] = f"prob_{point.id}"
            
            print(f"\nUpdating point {point.id}:")
            print(f"  Problem: {problem_name}")
            print(f"  Category: {category} (ID: {category_id})")
            print(f"  Sub-category ID: {sub_category_id}")
            
            # Create updated point
            updated_point = PointStruct(
                id=point.id,
                vector=point.vector,
                payload=updated_payload
            )
            
            updated_points.append(updated_point)
        
        # Update all points in batch
        print(f"\n--- Updating {len(updated_points)} points ---")
        client.upsert(
            collection_name=collection_name,
            points=updated_points
        )
        
        print("✅ Successfully updated all points!")
        
        # Verify the updates
        print("\n--- Verifying updates ---")
        updated_points_check = client.scroll(
            collection_name=collection_name,
            limit=5,
            with_payload=True,
            with_vectors=False
        )[0]
        
        for point in updated_points_check:
            payload = point.payload
            print(f"\nPoint {point.id}:")
            print(f"  Problem: {payload.get('problem_name', 'N/A')}")
            print(f"  Category: {payload.get('category', 'N/A')}")
            print(f"  Category ID: {payload.get('category_id', 'N/A')}")
            print(f"  Sub-category ID: {payload.get('sub_category_id', 'N/A')}")
            print(f"  Problem ID: {payload.get('problem_id', 'N/A')}")
        
    except Exception as e:
        print(f"Error fixing collection: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_problems_collection())