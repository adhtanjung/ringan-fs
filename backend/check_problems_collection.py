#!/usr/bin/env python3
"""
Check the structure and content of the mental-health-problems collection
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_problems_collection():
    """
    Check the problems collection structure and content
    """
    
    print("=== Checking Problems Collection ===")
    
    # Initialize Qdrant client
    client = QdrantClient(
        url=settings.QDRANT_URL
    )
    
    collection_name = "mental-health-problems"
    
    try:
        # Get collection info
        collection_info = client.get_collection(collection_name)
        print(f"Collection: {collection_name}")
        print(f"Points count: {collection_info.points_count}")
        print(f"Vector size: {collection_info.config.params.vectors.size}")
        
        # Get some sample points
        print("\n--- Sample Points ---")
        points = client.scroll(
            collection_name=collection_name,
            limit=10,
            with_payload=True,
            with_vectors=False
        )[0]
        
        for i, point in enumerate(points):
            print(f"\nPoint {i+1} (ID: {point.id}):")
            payload = point.payload
            print(f"  Payload keys: {list(payload.keys()) if payload else 'None'}")
            
            if payload:
                for key, value in payload.items():
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    else:
                        print(f"  {key}: {value}")
        
        # Check for specific fields
        print("\n--- Field Analysis ---")
        field_stats = {}
        
        # Get more points for analysis
        all_points = client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True,
            with_vectors=False
        )[0]
        
        for point in all_points:
            if point.payload:
                for key, value in point.payload.items():
                    if key not in field_stats:
                        field_stats[key] = {'count': 0, 'null_count': 0, 'sample_values': set()}
                    
                    field_stats[key]['count'] += 1
                    
                    if value is None or str(value).lower() in ['nan', 'null', '']:
                        field_stats[key]['null_count'] += 1
                    else:
                        if len(field_stats[key]['sample_values']) < 5:
                            field_stats[key]['sample_values'].add(str(value)[:50])
        
        for field, stats in field_stats.items():
            print(f"\nField '{field}':")
            print(f"  Total occurrences: {stats['count']}")
            print(f"  Null/NaN values: {stats['null_count']}")
            print(f"  Sample values: {list(stats['sample_values'])}")
        
        # Search for stress-related problems specifically
        print("\n--- Stress-related Problems ---")
        stress_points = client.scroll(
            collection_name=collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="text",
                        match=MatchValue(value="stress")
                    )
                ]
            ),
            limit=5,
            with_payload=True,
            with_vectors=False
        )[0]
        
        for i, point in enumerate(stress_points):
            print(f"\nStress Point {i+1}:")
            payload = point.payload
            if payload:
                for key, value in payload.items():
                    print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error checking collection: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_problems_collection())