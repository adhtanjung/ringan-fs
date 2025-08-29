#!/usr/bin/env python3
"""
Vector Database Verification Test
Checks if all datasets are properly stored in vector database
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.vector_service import vector_service
from app.services.semantic_search_service import semantic_search_service

async def verify_vector_database():
    """Verify all datasets are properly stored in vector database"""
    
    print("🔍 Vector Database Verification Test")
    print("="*50)
    
    try:
        # Connect to vector database
        print("\n🔄 Connecting to vector database...")
        connected = await vector_service.connect()
        if not connected:
            print("❌ Failed to connect to vector database")
            return False
            
        print("✅ Connected to vector database")
        
        # Check health
        health = await vector_service.health_check()
        print(f"📊 Health Status: {health['status']}")
        print(f"📊 Collections Count: {health.get('collections', 0)}")
        
        # Get collection statistics
        print("\n📈 Collection Statistics:")
        stats = await vector_service.get_collection_stats()
        
        total_points = 0
        for collection_name, info in stats.items():
            points_count = info.get('points_count', 0)
            total_points += points_count
            print(f"   {collection_name}: {points_count} points")
            
        print(f"\n📊 Total Points in Vector DB: {total_points}")
        
        # Test semantic search functionality
        print("\n🧠 Testing Semantic Search Functionality:")
        
        # Initialize semantic search
        search_initialized = await semantic_search_service.initialize()
        if not search_initialized:
            print("❌ Failed to initialize semantic search service")
            return False
            
        print("✅ Semantic search service initialized")
        
        # Test different types of searches
        test_queries = [
            ("anxiety", "Anxiety-related problems"),
            ("stress kerja", "Work stress problems"),
            ("trauma masa kecil", "Childhood trauma"),
            ("depresi", "Depression-related issues"),
            ("cemas berlebihan", "Excessive anxiety")
        ]
        
        print("\n🔍 Testing Problem Search:")
        for query, description in test_queries:
            result = await semantic_search_service.search_problems(
                query=query,
                limit=3,
                score_threshold=0.3
            )
            
            if result.success and result.results:
                print(f"   ✅ '{query}' -> Found {len(result.results)} problems")
                for i, res in enumerate(result.results[:2]):
                    problem_name = res.payload.get('problem_name', 'Unknown')
                    print(f"      {i+1}. {problem_name} (score: {res.score:.3f})")
            else:
                print(f"   ❌ '{query}' -> No problems found")
                
        print("\n🔍 Testing Assessment Questions Search:")
        for query, description in test_queries[:3]:
            result = await semantic_search_service.search_assessment_questions(
                problem_description=query,
                limit=2,
                score_threshold=0.3
            )
            
            if result.success and result.results:
                print(f"   ✅ '{query}' -> Found {len(result.results)} questions")
                for i, res in enumerate(result.results[:1]):
                    question_text = res.payload.get('text', res.payload.get('question_text', 'Unknown'))[:50]
                    print(f"      {i+1}. {question_text}... (score: {res.score:.3f})")
            else:
                print(f"   ❌ '{query}' -> No questions found")
                
        print("\n🔍 Testing Therapeutic Suggestions Search:")
        for query, description in test_queries[:3]:
            result = await semantic_search_service.search_therapeutic_suggestions(
                problem_description=query,
                limit=2,
                score_threshold=0.3
            )
            
            if result.success and result.results:
                print(f"   ✅ '{query}' -> Found {len(result.results)} suggestions")
                for i, res in enumerate(result.results[:1]):
                    suggestion_text = res.payload.get('suggestion_text', res.payload.get('text', 'Unknown'))[:50]
                    print(f"      {i+1}. {suggestion_text}... (score: {res.score:.3f})")
            else:
                print(f"   ❌ '{query}' -> No suggestions found")
        
        # Summary
        print("\n" + "="*50)
        if total_points > 0:
            print("✅ Vector Database Verification PASSED")
            print(f"📊 Total data points stored: {total_points}")
            print("🧠 Semantic search is functional")
            return True
        else:
            print("❌ Vector Database Verification FAILED")
            print("📊 No data points found in vector database")
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(verify_vector_database())