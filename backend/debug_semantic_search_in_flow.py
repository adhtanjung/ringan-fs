#!/usr/bin/env python3
"""
Debug script to test semantic search service within conversation flow context
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

async def test_semantic_search_in_flow():
    """
    Test semantic search exactly as it's called in conversation flow
    """
    
    print("=== Testing Semantic Search in Flow Context ===")
    
    message = "Saya merasa sangat stres dengan pekerjaan saya akhir-akhir ini"
    
    print(f"\nTesting message: '{message}'")
    
    # Call semantic search exactly as in conversation flow
    problems_search = await semantic_search_service.search_problems(
        query=message,
        limit=3,
        score_threshold=0.2  # Lower threshold for cross-language matching
    )
    
    print(f"\nSearch result object: {problems_search}")
    print(f"Search success: {problems_search.success}")
    print(f"Search results count: {len(problems_search.results) if problems_search.results else 0}")
    print(f"Search error: {problems_search.error}")
    
    if problems_search.success and problems_search.results:
        print(f"\nProcessing {len(problems_search.results)} results:")
        
        identified_problems = []
        for i, result in enumerate(problems_search.results):
            print(f"\nResult {i+1}:")
            print(f"  ID: {result.id}")
            print(f"  Score: {result.score}")
            print(f"  Payload: {result.payload}")
            
            payload = result.payload
            problem_data = {
                "problem_id": payload.get("problem_id", ""),
                "sub_category_id": payload.get("sub_category_id", ""),
                "category": payload.get("category", ""),
                "problem_text": payload.get("text", ""),
                "domain": payload.get("domain", ""),
                "score": result.score,
                "suggestions_available": True
            }
            
            identified_problems.append(problem_data)
            print(f"  Processed problem data: {problem_data}")
        
        print(f"\nFinal identified_problems list: {identified_problems}")
        print(f"Length: {len(identified_problems)}")
        
        if identified_problems:
            print(f"\nTop problem: {identified_problems[0]}")
        
    else:
        print("\n❌ No problems found or search failed")
        print(f"Success: {problems_search.success}")
        print(f"Results: {problems_search.results}")
        print(f"Error: {problems_search.error}")

if __name__ == "__main__":
    asyncio.run(test_semantic_search_in_flow())