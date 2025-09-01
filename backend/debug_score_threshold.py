#!/usr/bin/env python3
"""
Debug script to test different score thresholds
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.semantic_search_service import semantic_search_service
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_score_thresholds():
    """
    Test different score thresholds to find the right one
    """
    
    print("=== Testing Different Score Thresholds ===")
    
    message = "Saya merasa sangat stres dengan pekerjaan saya akhir-akhir ini"
    
    print(f"\nTesting message: '{message}'")
    
    # Test different thresholds
    thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    
    for threshold in thresholds:
        print(f"\n--- Testing threshold: {threshold} ---")
        
        problems_search = await semantic_search_service.search_problems(
            query=message,
            limit=5,
            score_threshold=threshold
        )
        
        print(f"Success: {problems_search.success}")
        print(f"Results count: {len(problems_search.results) if problems_search.results else 0}")
        print(f"Error: {problems_search.error}")
        
        if problems_search.success and problems_search.results:
            print(f"Top 3 results:")
            for i, result in enumerate(problems_search.results[:3]):
                payload = result.payload
                print(f"  {i+1}. Score: {result.score:.4f} | Category: {payload.get('category', 'N/A')} | Text: {payload.get('text', 'N/A')[:50]}...")
        else:
            print("  No results found")

if __name__ == "__main__":
    asyncio.run(test_score_thresholds())