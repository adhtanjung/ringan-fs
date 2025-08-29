#!/usr/bin/env python3
"""
Test script for Ollama service
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ollama_service import OllamaService

async def test_ollama():
    """Test the Ollama service"""

    print("🧪 Testing Ollama service...\n")

    try:
        # Initialize the service
        ollama_service = OllamaService()
        print(f"✅ Ollama service initialized with model: {ollama_service.model}")

        # Test simple response generation
        print("\n🔄 Testing response generation...")
        messages = [
            {"role": "user", "content": "Halo, bagaimana kabarmu?"}
        ]

        response = await ollama_service.generate_response(messages)
        print(f"📝 Response: {response[:100]}...")

        print("\n✅ Ollama service test completed!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ollama())


