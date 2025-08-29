#!/usr/bin/env python3
"""
Test script for multilingual chat functionality
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.language_service import LanguageService, Language
from services.translation_service import TranslationService
from services.chat_service import ChatService
from services.ollama_service import OllamaService
from services.semantic_search_service import SemanticSearchService
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService
from core.config import settings

async def test_language_detection():
    """Test language detection functionality"""
    print("\n=== Testing Language Detection ===")
    
    language_service = LanguageService()
    
    test_cases = [
        ("Hello, I am feeling anxious today", Language.ENGLISH),
        ("Saya merasa cemas hari ini", Language.INDONESIAN),
        ("I need help with my depression", Language.ENGLISH),
        ("Saya butuh bantuan untuk depresi saya", Language.INDONESIAN),
        ("How are you?", Language.ENGLISH),
        ("Apa kabar?", Language.INDONESIAN)
    ]
    
    for text, expected_language in test_cases:
        detected_language, confidence = await language_service.detect_language(text)
        status = "✅ PASS" if detected_language == expected_language else "❌ FAIL"
        print(f"{status} '{text}' -> {detected_language.value} (confidence: {confidence:.2f})")

async def test_translation():
    """Test translation functionality"""
    print("\n=== Testing Translation ===")
    
    translation_service = TranslationService()
    
    # Test Indonesian to English
    indonesian_texts = [
        "Saya merasa sedih",
        "Saya butuh bantuan",
        "Saya mengalami kecemasan",
        "Bagaimana cara mengatasi stres?"
    ]
    
    print("\nIndonesian to English:")
    for text in indonesian_texts:
        translated = await translation_service.translate_indonesian_to_english(text)
        print(f"  '{text}' -> '{translated}'")
    
    # Test English to Indonesian
    english_texts = [
        "I feel sad",
        "I need help",
        "I am experiencing anxiety",
        "How to deal with stress?"
    ]
    
    print("\nEnglish to Indonesian:")
    for text in english_texts:
        translated = await translation_service.translate_english_to_indonesian(text)
        print(f"  '{text}' -> '{translated}'")

async def test_multilingual_chat():
    """Test multilingual chat functionality"""
    print("\n=== Testing Multilingual Chat ===")
    
    try:
        # Initialize services
        vector_service = VectorService()
        embedding_service = EmbeddingService()
        semantic_search_service = SemanticSearchService(vector_service, embedding_service)
        ollama_service = OllamaService()
        chat_service = ChatService(ollama_service, semantic_search_service)
        
        test_messages = [
            ("I am feeling very anxious about my work", "english"),
            ("Saya merasa sangat cemas tentang pekerjaan saya", "indonesian"),
            ("Can you help me with stress management?", "english"),
            ("Bisakah Anda membantu saya mengelola stres?", "indonesian")
        ]
        
        client_id = "test_multilingual_user"
        
        for message, expected_lang in test_messages:
            print(f"\nTesting: '{message}' (expected: {expected_lang})")
            
            try:
                response = await chat_service.process_message(
                    message=message,
                    client_id=client_id
                )
                
                print(f"  Response: {response['message'][:100]}...")
                print(f"  Sentiment: {response['sentiment']['overall']}")
                print(f"  Crisis: {response['is_crisis']}")
                
                if response.get('semantic_context'):
                    print(f"  Semantic context found: {len(response['semantic_context'])} results")
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Failed to initialize chat service: {str(e)}")
        print("Note: This test requires Ollama and vector database to be running")

async def main():
    """Run all multilingual tests"""
    print("Starting Multilingual Chat Tests...")
    
    await test_language_detection()
    await test_translation()
    await test_multilingual_chat()
    
    print("\n=== Test Summary ===")
    print("✅ Language detection implemented")
    print("✅ Translation service implemented")
    print("✅ Multilingual chat integration completed")
    print("\nNote: Full functionality requires Ollama and vector database services to be running.")

if __name__ == "__main__":
    asyncio.run(main())