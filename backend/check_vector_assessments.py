#!/usr/bin/env python3
"""
Check vector database assessment data to verify scale questions exist
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service

async def check_vector_assessments():
    """Check assessment data in vector database"""
    print("🔍 Checking vector database assessment data...")

    try:
        # Initialize services
        await vector_service.initialize()
        await embedding_service.initialize()

        # Search for assessment questions
        print("📊 Searching for assessment questions...")

        # Generate a simple embedding for search
        search_embedding = await embedding_service.generate_embedding("anxiety assessment questions")

        if not search_embedding:
            print("❌ Failed to generate search embedding")
            return False

        # Search in assessments collection
        search_results = await vector_service.search_similar(
            collection_name="mental-health-assessments",
            vector=search_embedding,
            limit=20,
            score_threshold=0.1
        )

        print(f"📊 Found {len(search_results)} assessment questions")

        # Analyze response types
        scale_count = 0
        text_count = 0
        unknown_count = 0

        print("\n🔍 Sample questions:")
        for i, result in enumerate(search_results[:10], 1):
            payload = result.get('payload', {})
            response_type = payload.get('response_type', 'unknown')

            if response_type == 'scale':
                scale_count += 1
            elif response_type == 'text':
                text_count += 1
            else:
                unknown_count += 1

            print(f"  {i}. Type: {response_type}")
            print(f"     ID: {payload.get('question_id', 'N/A')}")
            print(f"     Text: {payload.get('text', 'N/A')[:80]}...")

            if response_type == 'scale':
                print(f"     Scale: {payload.get('scale_min', 'N/A')}-{payload.get('scale_max', 'N/A')}")
            print()

        print(f"📊 Summary:")
        print(f"   Scale questions: {scale_count}")
        print(f"   Text questions: {text_count}")
        print(f"   Unknown type: {unknown_count}")

        return True

    except Exception as e:
        print(f"❌ Error checking vector assessments: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🚀 Vector Database Assessment Data Checker")
    print("=" * 50)

    success = await check_vector_assessments()

    if success:
        print("\n✅ Check completed successfully!")
    else:
        print("\n❌ Check failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())















