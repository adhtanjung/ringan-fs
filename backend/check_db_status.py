import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.mongodb_client import MongoDBClient

def check_collections():
    try:
        client = MongoDBClient()
        db = client.get_database()
        
        collections = ['problems', 'assessments', 'suggestions', 'feedback_prompts', 'training_examples', 'next_actions']
        
        print("📊 Database Collection Status:")
        for col in collections:
            count = db[col].count_documents({})
            print(f"  {col}: {count} documents")
            
        # Check if any collections have data
        total_docs = sum(db[col].count_documents({}) for col in collections)
        print(f"\n📈 Total documents: {total_docs}")
        
        if total_docs > 0:
            print("⚠️  Database is not empty - this may cause duplicate key errors")
        else:
            print("✅ Database is clean")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_collections()