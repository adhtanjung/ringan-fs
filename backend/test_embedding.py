#!/usr/bin/env python3
"""
Test script for embedding service
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.embedding_service import embedding_service

async def test_embedding():
    """Test the embedding service"""

    print("🧪 Testing embedding service...\n")

    try:
        # Initialize the service
        print("🔄 Initializing embedding service...")
        success = await embedding_service.initialize()
        if not success:
            print("❌ Failed to initialize embedding service")
            return

        print("✅ Embedding service initialized")

        # Test single embedding
        print("\n🔄 Testing single embedding...")
        test_text = "Hello, this is a test message for mental health support."
        embedding = await embedding_service.generate_embedding(test_text)

        if embedding:
            print(f"✅ Single embedding successful! Vector size: {len(embedding)}")
        else:
            print("❌ Single embedding failed")

        # Test batch embedding
        print("\n🔄 Testing batch embedding...")
        test_texts = [
            "Hello, this is a test message for mental health support.",
            "I'm feeling stressed and anxious today.",
            "Can you help me with my mental health concerns?",
            "I need someone to talk to about my problems."
        ]

        embeddings = await embedding_service.generate_embeddings_batch(test_texts)

        successful_count = sum(1 for emb in embeddings if emb is not None)
        print(f"✅ Batch embedding: {successful_count}/{len(test_texts)} successful")

        if successful_count > 0:
            print(f"   Vector size: {len(embeddings[0]) if embeddings[0] else 'N/A'}")

    except Exception as e:
        print(f"❌ Error during embedding test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_embedding())


