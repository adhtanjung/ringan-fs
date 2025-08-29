import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Database connections
mongodb_client = None
redis_client = None

async def init_db():
    """Initialize database connections"""
    global mongodb_client, redis_client

    try:
        # Try to initialize MongoDB (optional)
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
            await mongodb_client.admin.command('ping')
            logger.info("✅ MongoDB connected successfully")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB connection failed (optional): {str(e)}")
            mongodb_client = None

        # Try to initialize Redis (optional)
        try:
            from redis import asyncio as aioredis
            redis_client = aioredis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed (optional): {str(e)}")
            redis_client = None

    except Exception as e:
        logger.error(f"❌ Database initialization error: {str(e)}")
        # Don't raise - make databases optional

async def close_db():
    """Close database connections"""
    global mongodb_client, redis_client

    if mongodb_client:
        try:
            mongodb_client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.warning(f"Error closing MongoDB: {str(e)}")

    if redis_client:
        try:
            await redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis: {str(e)}")

def get_mongodb():
    """Get MongoDB client"""
    return mongodb_client

def get_redis():
    """Get Redis client"""
    return redis_client

