#!/usr/bin/env python3
"""
Check MongoDB assessment data to verify scale questions exist
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_mongodb

async def check_assessments():
    """Check assessment data in MongoDB"""
    print("🔍 Checking MongoDB assessment data...")

    try:
        # Get MongoDB connection
        mongodb = get_mongodb()
        if not mongodb:
            print("❌ MongoDB connection failed")
            return False

        db = mongodb.mental_health_db
        assessments_collection = db.assessments

        # Count total assessments
        total_count = await assessments_collection.count_documents({"is_active": True})
        print(f"📊 Total active assessments: {total_count}")

        # Count by response type
        scale_count = await assessments_collection.count_documents({
            "is_active": True,
            "response_type": "scale"
        })
        text_count = await assessments_collection.count_documents({
            "is_active": True,
            "response_type": "text"
        })

        print(f"📊 Scale questions: {scale_count}")
        print(f"📊 Text questions: {text_count}")

        # Show sample scale questions
        if scale_count > 0:
            print("\n🔍 Sample scale questions:")
            scale_questions = await assessments_collection.find({
                "is_active": True,
                "response_type": "scale"
            }).limit(3).to_list(length=3)

            for i, q in enumerate(scale_questions, 1):
                print(f"  {i}. ID: {q.get('question_id', 'N/A')}")
                print(f"     Text: {q.get('question_text', 'N/A')[:80]}...")
                print(f"     Scale: {q.get('scale_min', 'N/A')}-{q.get('scale_max', 'N/A')}")
                print()

        # Show sample text questions
        if text_count > 0:
            print("🔍 Sample text questions:")
            text_questions = await assessments_collection.find({
                "is_active": True,
                "response_type": "text"
            }).limit(3).to_list(length=3)

            for i, q in enumerate(text_questions, 1):
                print(f"  {i}. ID: {q.get('question_id', 'N/A')}")
                print(f"     Text: {q.get('question_text', 'N/A')[:80]}...")
                print()

        return True

    except Exception as e:
        print(f"❌ Error checking assessments: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🚀 MongoDB Assessment Data Checker")
    print("=" * 50)

    success = await check_assessments()

    if success:
        print("\n✅ Check completed successfully!")
    else:
        print("\n❌ Check failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())















