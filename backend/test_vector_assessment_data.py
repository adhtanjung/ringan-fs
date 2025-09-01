#!/usr/bin/env python3
"""
Test script to check assessment question data in vector database
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.semantic_search_service import semantic_search_service

async def test_assessment_questions():
    """Test assessment questions retrieval from vector database"""
    try:
        print("Initializing semantic search service...")
        await semantic_search_service.initialize()
        
        print("\nSearching for stress-related assessment questions...")
        result = await semantic_search_service.search_assessment_questions(
            problem_description='stress anxiety work pressure',
            limit=5,
            score_threshold=0.3
        )
        
        if result.success:
            print(f"\nFound {len(result.results)} assessment questions:")
            print("=" * 60)
            
            for i, r in enumerate(result.results, 1):
                payload = r.payload
                print(f"\nQuestion {i}:")
                print(f"  Question ID: {payload.get('question_id', 'N/A')}")
                print(f"  Question Text: {payload.get('text', 'N/A')}")
                print(f"  Response Type: {payload.get('response_type', 'N/A')}")
                print(f"  Sub Category: {payload.get('sub_category_id', 'N/A')}")
                print(f"  Domain: {payload.get('domain', 'N/A')}")
                print(f"  Score: {r.score:.3f}")
                print(f"  Full Payload Keys: {list(payload.keys())}")
                print("-" * 40)
        else:
            print(f"Search failed: {result.error}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_assessment_questions())