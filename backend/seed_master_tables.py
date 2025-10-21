#!/usr/bin/env python3
"""
Seed script to populate initial master table data for Problem Types and Domain Types.
Run this script to populate the database with initial data for the master tables.
"""

import sys
import os
from datetime import datetime
from pymongo import MongoClient

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def seed_master_tables():
    """Seed the master tables with initial data"""

    # Initial domain types
    domain_types = [
        {
            "domain_name": "Stress",
            "domain_code": "STR",
            "description": "Stress-related problems and conditions",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "domain_name": "Anxiety",
            "domain_code": "ANX",
            "description": "Anxiety-related problems and disorders",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "domain_name": "Trauma",
            "domain_code": "TRA",
            "description": "Trauma-related problems and PTSD",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "domain_name": "General",
            "domain_code": "GEN",
            "description": "General mental health concerns and wellness",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    # Initial problem types
    problem_types = [
        {
            "type_name": "Anxiety",
            "description": "General anxiety disorders and anxiety-related conditions",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "type_name": "Depression",
            "description": "Depressive disorders and mood-related conditions",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "type_name": "Stress",
            "description": "Stress-related conditions and work-life balance issues",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "type_name": "Trauma",
            "description": "Trauma and PTSD-related conditions",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "type_name": "Relationship Issues",
            "description": "Relationship and interpersonal problems",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "type_name": "Sleep Problems",
            "description": "Sleep disorders and insomnia-related issues",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "type_name": "Self-Esteem",
            "description": "Self-esteem and confidence-related issues",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "type_name": "Grief and Loss",
            "description": "Grief, loss, and bereavement-related issues",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    try:
        # Connect to MongoDB
        print("🔌 Connecting to MongoDB...")
        client = MongoClient(settings.MONGODB_URL)
        db = client.mental_health_db

        # Check if collections exist and clear them if they do
        if 'domain_types' in db.list_collection_names():
            print("🗑️  Clearing existing domain_types collection...")
            db.domain_types.drop()

        if 'problem_types' in db.list_collection_names():
            print("🗑️  Clearing existing problem_types collection...")
            db.problem_types.drop()

        # Insert domain types
        print("📝 Inserting domain types...")
        domain_result = db.domain_types.insert_many(domain_types)
        print(f"✅ Inserted {len(domain_result.inserted_ids)} domain types")

        # Insert problem types
        print("📝 Inserting problem types...")
        problem_result = db.problem_types.insert_many(problem_types)
        print(f"✅ Inserted {len(problem_result.inserted_ids)} problem types")

        # Verify the data
        print("\n📊 Verification:")
        domain_count = db.domain_types.count_documents({})
        problem_count = db.problem_types.count_documents({})
        print(f"   Domain Types: {domain_count}")
        print(f"   Problem Types: {problem_count}")

        # Show sample data
        print("\n📋 Sample Domain Types:")
        for domain in db.domain_types.find().limit(3):
            print(f"   - {domain['domain_name']} ({domain['domain_code']})")

        print("\n📋 Sample Problem Types:")
        for problem in db.problem_types.find().limit(3):
            print(f"   - {problem['type_name']}")

        print("\n🎉 Master tables seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding master tables: {str(e)}")
        return False
    finally:
        client.close()

    return True

if __name__ == "__main__":
    print("🌱 Starting master tables seeding...")
    success = seed_master_tables()
    if success:
        print("✅ Seeding completed successfully!")
        sys.exit(0)
    else:
        print("❌ Seeding failed!")
        sys.exit(1)



