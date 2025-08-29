#!/usr/bin/env python3
"""
Test script for semantic search integration
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.semantic_search_service import semantic_search_service

async def test_semantic_integration():
    """Test the semantic search integration"""

    print("🧪 Testing semantic search integration...\n")

    try:
        # Initialize the service
        print("🔄 Initializing semantic search service...")
        success = await semantic_search_service.initialize()
        if not success:
            print("❌ Failed to initialize semantic search service")
            return

        print("✅ Semantic search service initialized")

        # Test problem search
        print("\n🔄 Testing problem search...")
        problems_result = await semantic_search_service.search_problems(
            query="Saya sedang stress dengan pekerjaan",
            limit=2,
            score_threshold=0.4
        )

        print(f"📊 Problem search result: {problems_result.success}")
        if problems_result.success and problems_result.results:
            print(f"   Found {len(problems_result.results)} problems")
            for i, result in enumerate(problems_result.results):
                print(f"   {i+1}. {result.payload.get('problem_name', 'Unknown')} (score: {result.score:.3f})")

        # Test suggestions search
        print("\n🔄 Testing suggestions search...")
        suggestions_result = await semantic_search_service.search_therapeutic_suggestions(
            problem_description="Saya sedang stress dengan pekerjaan",
            limit=2,
            score_threshold=0.4
        )

        print(f"📊 Suggestions search result: {suggestions_result.success}")
        if suggestions_result.success and suggestions_result.results:
            print(f"   Found {len(suggestions_result.results)} suggestions")
            for i, result in enumerate(suggestions_result.results):
                print(f"   {i+1}. {result.payload.get('suggestion_text', 'Unknown')[:50]}... (score: {result.score:.3f})")

        # Test assessment search
        print("\n🔄 Testing assessment search...")
        assessments_result = await semantic_search_service.search_assessment_questions(
            problem_description="Saya sedang stress dengan pekerjaan",
            limit=2,
            score_threshold=0.4
        )

        print(f"📊 Assessment search result: {assessments_result.success}")
        if assessments_result.success and assessments_result.results:
            print(f"   Found {len(assessments_result.results)} assessment questions")
            for i, result in enumerate(assessments_result.results):
                print(f"   {i+1}. {result.payload.get('text', 'Unknown')[:50]}... (score: {result.score:.3f})")

        print("\n✅ Semantic search integration test completed!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_semantic_integration())


