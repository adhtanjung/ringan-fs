import asyncio
from app.services.vector_service import vector_service
from app.services.data_import_service import DataImportService

async def check_vector_db():
    try:
        # Connect to vector database
        await vector_service.connect()
        print("✓ Connected to vector database")
        
        # Check health
        health = await vector_service.health_check()
        print(f"✓ Vector DB Health: {health}")
        
        # Get collections and their counts
        collections = vector_service.client.get_collections()
        print("\nCollections:")
        for collection in collections.collections:
            count = vector_service.client.count(collection.name).count
            print(f"  {collection.name}: {count} points")
        
        # Check if data needs to be imported
        if not collections.collections:
            print("\n⚠️  No collections found. Data import may be needed.")
            return False
        
        # Check for expected collections
        expected_collections = [
            "mental-health-problems",
            "mental-health-assessments", 
            "mental-health-suggestions"
        ]
        
        existing_names = [c.name for c in collections.collections]
        missing = [name for name in expected_collections if name not in existing_names]
        
        if missing:
            print(f"\n⚠️  Missing collections: {missing}")
            return False
        
        # Check if collections have data
        empty_collections = []
        for collection in collections.collections:
            count = vector_service.client.count(collection.name).count
            if count == 0:
                empty_collections.append(collection.name)
        
        if empty_collections:
            print(f"\n⚠️  Empty collections: {empty_collections}")
            return False
        
        print("\n✓ All expected collections exist and contain data")
        return True
        
    except Exception as e:
        print(f"❌ Error checking vector database: {e}")
        return False

async def import_data_if_needed():
    """Import data if vector database is empty or missing collections"""
    try:
        data_service = DataImportService()
        print("\n🔄 Starting data import...")
        
        # Import all datasets
        await data_service.import_all_data()
        print("✓ Data import completed")
        
        return True
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        return False

async def main():
    print("=== Vector Database Status Check ===")
    
    # Check current status
    db_ready = await check_vector_db()
    
    if not db_ready:
        print("\n=== Importing Data ===")
        import_success = await import_data_if_needed()
        
        if import_success:
            print("\n=== Re-checking Vector Database ===")
            await check_vector_db()
        else:
            print("❌ Failed to import data")
    
    print("\n=== Check Complete ===")

if __name__ == "__main__":
    asyncio.run(main())