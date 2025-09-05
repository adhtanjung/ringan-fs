#!/usr/bin/env python3
import asyncio
from app.core.database import init_db, get_mongodb

async def check_collections():
    await init_db()
    client = get_mongodb()
    db = client.mental_health_db
    collections = await db.list_collection_names()
    print(f'Collections: {collections}')
    print(f'Number of collections: {len(collections)}')

if __name__ == "__main__":
    asyncio.run(check_collections())