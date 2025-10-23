#!/usr/bin/env python3
"""
Migration script to update existing assessment questions to use 1-4 scale with labels.

This script:
1. Updates all scale questions to use scale_min=1, scale_max=4
2. Adds default scale_labels if missing
3. Updates corresponding vector database entries
4. Logs migration results
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any
import json

# Add the backend directory to the Python path
sys.path.append('/Users/adhitanjung/Documents/AITech/ringan-fs/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_scale_1_4.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Default scale labels
DEFAULT_SCALE_LABELS = {
    "1": "Not at all",
    "2": "A little",
    "3": "Quite a bit",
    "4": "Very much"
}

class ScaleMigrationService:
    def __init__(self):
        self.client = None
        self.db = None
        self.migration_stats = {
            'total_assessments': 0,
            'scale_questions_found': 0,
            'updated_mongodb': 0,
            'updated_vector_db': 0,
            'errors': []
        }

    async def initialize(self):
        """Initialize database connections"""
        try:
            # MongoDB connection - try different connection strings
            connection_strings = [
                "mongodb://admin:password123@localhost:27017/mental_health_chat",
                "mongodb://admin:password123@localhost:27017",
                "mongodb://localhost:27017",
                "mongodb://localhost:27017/mental_health_db"
            ]

            self.client = None
            self.db = None

            for conn_str in connection_strings:
                try:
                    logger.info(f"🔄 Trying connection: {conn_str}")
                    self.client = AsyncIOMotorClient(conn_str)
                    # Try different database names
                    for db_name in ['mental_health_chat', 'mental_health_db', 'mental-health-chat']:
                        try:
                            self.db = self.client[db_name]
                            await self.db.list_collection_names()
                            logger.info(f"✅ Connected to database: {db_name}")
                            logger.info(f"✅ Connected successfully with: {conn_str}")
                            break
                        except Exception as db_e:
                            logger.warning(f"⚠️ Database {db_name} failed: {str(db_e)}")
                            continue

                    if self.db is not None:
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Connection failed: {conn_str} - {str(e)}")
                    if self.client:
                        self.client.close()
                    continue

            if self.db is None:
                raise Exception("Failed to connect to MongoDB with any connection string")

            # Initialize vector service (optional for migration)
            try:
                await vector_service.connect()
                await vector_service.create_collections()
                await embedding_service.initialize()
                logger.info("✅ Vector service initialized")
            except Exception as e:
                logger.warning(f"⚠️ Vector service initialization failed (continuing without it): {str(e)}")

            logger.info("✅ Database connections initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize database connections: {str(e)}")
            return False

    async def migrate_assessments(self):
        """Migrate all assessment questions to 1-4 scale"""
        try:
            logger.info("🔄 Starting assessment migration to 1-4 scale...")

            # First, check if assessments collection exists
            collections = await self.db.list_collection_names()
            logger.info(f"📋 Available collections: {collections}")

            if 'assessments' not in collections:
                logger.warning("⚠️ No 'assessments' collection found. Creating it...")
                # Create empty collection
                await self.db.create_collection('assessments')
                logger.info("✅ Created 'assessments' collection")

            # Find all assessments with response_type="scale"
            assessments_cursor = self.db.assessments.find({"response_type": "scale"})
            assessments = await assessments_cursor.to_list(length=None)

            self.migration_stats['total_assessments'] = len(assessments)
            self.migration_stats['scale_questions_found'] = len(assessments)

            logger.info(f"📊 Found {len(assessments)} scale questions to migrate")

            if len(assessments) == 0:
                logger.info("ℹ️ No scale questions found to migrate. This is normal if no assessments exist yet.")
                return

            for assessment in assessments:
                try:
                    await self.migrate_single_assessment(assessment)
                except Exception as e:
                    error_msg = f"Failed to migrate assessment {assessment.get('question_id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)

            logger.info("✅ Assessment migration completed")

        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            self.migration_stats['errors'].append(f"Migration failed: {str(e)}")

    async def migrate_single_assessment(self, assessment: Dict[str, Any]):
        """Migrate a single assessment question"""
        question_id = assessment.get('question_id', 'unknown')

        try:
            # Update MongoDB document
            update_data = {
                'scale_min': 1,
                'scale_max': 4,
                'scale_labels': DEFAULT_SCALE_LABELS,
                'updated_at': datetime.utcnow()
            }

            result = await self.db.assessments.update_one(
                {"_id": assessment["_id"]},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                self.migration_stats['updated_mongodb'] += 1
                logger.info(f"✅ Updated MongoDB: {question_id}")
            else:
                logger.warning(f"⚠️ No changes made to MongoDB: {question_id}")

            # Update vector database (optional)
            try:
                await self.update_vector_database(assessment, update_data)
            except Exception as e:
                logger.warning(f"⚠️ Vector DB update failed for {question_id} (continuing): {str(e)}")

        except Exception as e:
            raise Exception(f"Failed to migrate {question_id}: {str(e)}")

    async def update_vector_database(self, assessment: Dict[str, Any], update_data: Dict[str, Any]):
        """Update the corresponding vector database entry"""
        try:
            question_id = assessment.get('question_id', 'unknown')

            # Generate new embedding with updated data
            question_text = assessment.get('question_text', '')
            embedding = await embedding_service.generate_embedding(question_text)

            if not embedding:
                logger.warning(f"⚠️ Failed to generate embedding for {question_id}")
                return

            # Create updated payload
            payload = {
                'question_id': question_id,
                'sub_category_id': assessment.get('sub_category_id', ''),
                'question_text': question_text,
                'response_type': 'scale',
                'scale_min': update_data['scale_min'],
                'scale_max': update_data['scale_max'],
                'scale_labels': update_data['scale_labels'],
                'type': 'assessment'
            }

            # Convert MongoDB ObjectId to UUID format for Qdrant
            import uuid
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(assessment['_id'])))

            point = {
                'id': point_id,
                'vector': embedding,
                'payload': payload
            }

            # Update in vector database
            collection_name = vector_service.collections.get('assessments', 'mental-health-assessments')
            await vector_service.upsert_points(collection_name, [point])

            self.migration_stats['updated_vector_db'] += 1
            logger.info(f"✅ Updated vector DB: {question_id}")

        except Exception as e:
            logger.error(f"❌ Failed to update vector DB for {question_id}: {str(e)}")
            raise

    async def verify_migration(self):
        """Verify the migration was successful"""
        try:
            logger.info("🔍 Verifying migration...")

            # Check MongoDB
            mongo_count = await self.db.assessments.count_documents({
                "response_type": "scale",
                "scale_min": 1,
                "scale_max": 4,
                "scale_labels": {"$exists": True}
            })

            logger.info(f"📊 MongoDB: {mongo_count} scale questions with 1-4 range and labels")

            # Check for any remaining old scale questions
            old_scale_count = await self.db.assessments.count_documents({
                "response_type": "scale",
                "$or": [
                    {"scale_min": {"$ne": 1}},
                    {"scale_max": {"$ne": 4}},
                    {"scale_labels": {"$exists": False}}
                ]
            })

            if old_scale_count > 0:
                logger.warning(f"⚠️ Found {old_scale_count} scale questions that may need manual review")
            else:
                logger.info("✅ All scale questions successfully migrated to 1-4 range")

        except Exception as e:
            logger.error(f"❌ Verification failed: {str(e)}")

    def print_migration_summary(self):
        """Print migration summary"""
        logger.info("\n" + "="*60)
        logger.info("MIGRATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total assessments processed: {self.migration_stats['total_assessments']}")
        logger.info(f"Scale questions found: {self.migration_stats['scale_questions_found']}")
        logger.info(f"MongoDB documents updated: {self.migration_stats['updated_mongodb']}")
        logger.info(f"Vector DB entries updated: {self.migration_stats['updated_vector_db']}")
        logger.info(f"Errors encountered: {len(self.migration_stats['errors'])}")

        if self.migration_stats['errors']:
            logger.info("\nErrors:")
            for error in self.migration_stats['errors']:
                logger.info(f"  - {error}")

        logger.info("="*60)

    async def cleanup(self):
        """Clean up database connections"""
        if self.client:
            self.client.close()
        logger.info("🧹 Database connections closed")

async def main():
    """Main migration function"""
    migration_service = ScaleMigrationService()

    try:
        # Initialize
        if not await migration_service.initialize():
            logger.error("❌ Failed to initialize migration service")
            return

        # Run migration
        await migration_service.migrate_assessments()

        # Verify migration
        await migration_service.verify_migration()

        # Print summary
        migration_service.print_migration_summary()

        logger.info("🎉 Migration completed successfully!")

    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

    finally:
        await migration_service.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

