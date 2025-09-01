#!/usr/bin/env python3
"""
Debug script to test problem search functionality
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

async def test_problem_search():
    """
    Test the problem search functionality
    """
    
    print("=== Testing Problem Search Debug ===")
    
    # Test messages
    test_messages = [
        "Saya merasa sangat stres dengan pekerjaan saya akhir-akhir ini",
        "I feel very stressed with my work lately",
        "work stress",
        "stress",
        "anxiety",
        "depression"
    ]
    
    for message in test_messages:
        print(f"\n--- Testing message: '{message}' ---")
        
        # Search for problems
        problems_search = await semantic_search_service.search_problems(
            query=message,
            limit=5,
            score_threshold=0.2
        )
        
        print(f"Search success: {problems_search.success}")
        print(f"Number of results: {len(problems_search.results) if problems_search.results else 0}")
        
        if problems_search.success and problems_search.results:
            for i, result in enumerate(problems_search.results):
                payload = result.payload
                print(f"  Result {i+1}:")
                print(f"    Score: {result.score:.4f}")
                print(f"    Category: {payload.get('category', 'N/A')}")
                print(f"    Domain: {payload.get('domain', 'N/A')}")
                print(f"    Text: {payload.get('text', 'N/A')[:100]}...")
                print(f"    Problem ID: {payload.get('problem_id', 'N/A')}")
                print(f"    Sub-category ID: {payload.get('sub_category_id', 'N/A')}")
        else:
            print("  No results found or search failed")
            if hasattr(problems_search, 'error'):
                print(f"  Error: {problems_search.error}")

if __name__ == "__main__":
    asyncio.run(test_problem_search())