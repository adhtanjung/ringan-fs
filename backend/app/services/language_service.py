"""\nLanguage Detection and Translation Service\nHandles language detection and translation for multilingual chat support\n"""

import logging
import re
from typing import Dict, Optional, Tuple
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    INDONESIAN = "id"
    UNKNOWN = "unknown"

class LanguageService:
    """Service for language detection and translation"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Indonesian language indicators
        self.indonesian_keywords = {
            # Common Indonesian words
            'saya', 'aku', 'kamu', 'anda', 'dia', 'mereka', 'kita', 'kami',
            'yang', 'dan', 'atau', 'dengan', 'untuk', 'dari', 'ke', 'di', 'pada',
            'tidak', 'bukan', 'belum', 'sudah', 'akan', 'sedang', 'telah',
            'ini', 'itu', 'tersebut', 'adalah', 'ada', 'menjadi', 'dapat',
            
            # Mental health related Indonesian terms
            'cemas', 'khawatir', 'takut', 'sedih', 'depresi', 'stres', 'stress',
            'gelisah', 'panik', 'trauma', 'kesedihan', 'kecemasan', 'kekhawatiran',
            'perasaan', 'emosi', 'hati', 'pikiran', 'jiwa', 'mental',
            'masalah', 'kesulitan', 'bantuan', 'dukungan', 'konseling',
            'terapi', 'psikolog', 'psikiater', 'kesehatan', 'jiwa',
            
            # Common Indonesian expressions
            'bagaimana', 'mengapa', 'kenapa', 'dimana', 'kapan', 'siapa',
            'apa', 'berapa', 'mana', 'seperti', 'kalau', 'jika', 'bila',
            'tolong', 'mohon', 'silakan', 'terima', 'kasih', 'maaf',
            
            # Indonesian specific particles and affixes
            'lah', 'kah', 'pun', 'nya', 'mu', 'ku'
        }
        
        # English language indicators
        self.english_keywords = {
            # Common English words
            'the', 'and', 'or', 'but', 'with', 'for', 'from', 'to', 'at', 'in', 'on',
            'not', 'no', 'yes', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
            'will', 'would', 'could', 'should', 'can', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'what', 'where', 'when', 'why', 'how',
            
            # Mental health related English terms
            'anxiety', 'anxious', 'worried', 'fear', 'afraid', 'sad', 'depression',
            'depressed', 'stress', 'stressed', 'panic', 'trauma', 'feeling', 'emotion',
            'mental', 'health', 'problem', 'issue', 'help', 'support', 'counseling',
            'therapy', 'psychologist', 'psychiatrist', 'treatment',
            
            # Common English question words and expressions
            'please', 'thank', 'sorry', 'excuse', 'hello', 'hi', 'goodbye', 'bye'
        }
        
        # Indonesian language patterns
        self.indonesian_patterns = [
            r'\b(me|ber|ter|pe|per|se)\w+',  # Indonesian prefixes
            r'\w+(an|kan|nya|lah|kah)\b',    # Indonesian suffixes
            r'\bdi\s+\w+',                   # "di" + word pattern
            r'\bke\s+\w+',                   # "ke" + word pattern
        ]
        
        # English language patterns
        self.english_patterns = [
            r'\b(ing|ed|er|est|ly|tion|sion)\b',  # English suffixes
            r'\b(un|re|pre|dis|mis|over|under)\w+',  # English prefixes
            r'\b(a|an|the)\s+\w+',  # Articles + word
        ]
    
    def _calculate_language_score(self, text: str, keywords: set, patterns: list) -> float:
        """Calculate language score based on keywords and patterns"""
        if not text:
            return 0.0
            
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        # Keyword matching score
        keyword_matches = sum(1 for word in words if word in keywords)
        keyword_score = keyword_matches / len(words)
        
        # Pattern matching score
        pattern_matches = 0
        for pattern in patterns:
            pattern_matches += len(re.findall(pattern, text.lower()))
        pattern_score = min(pattern_matches / len(words), 1.0)
        
        # Combined score (weighted)
        total_score = (keyword_score * 0.7) + (pattern_score * 0.3)
        return total_score
    
    async def detect_language(self, text: str) -> Tuple[Language, float]:
        """\n        Detect the language of input text\n        Returns: (Language, confidence_score)\n        """
        try:
            if not text or not text.strip():
                return Language.UNKNOWN, 0.0
            
            # Run language detection in thread to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._detect_language_sync,
                text
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return Language.UNKNOWN, 0.0
    
    def _detect_language_sync(self, text: str) -> Tuple[Language, float]:
        """Synchronous language detection"""
        # Calculate scores for both languages
        indonesian_score = self._calculate_language_score(
            text, self.indonesian_keywords, self.indonesian_patterns
        )
        english_score = self._calculate_language_score(
            text, self.english_keywords, self.english_patterns
        )
        
        # Determine language based on scores
        if indonesian_score > english_score and indonesian_score > 0.1:
            return Language.INDONESIAN, indonesian_score
        elif english_score > indonesian_score and english_score > 0.1:
            return Language.ENGLISH, english_score
        else:
            # If both scores are low, try to make an educated guess
            # based on character patterns
            if self._has_indonesian_characteristics(text):
                return Language.INDONESIAN, 0.5
            elif self._has_english_characteristics(text):
                return Language.ENGLISH, 0.5
            else:
                return Language.UNKNOWN, 0.0
    
    def _has_indonesian_characteristics(self, text: str) -> bool:
        """Check for Indonesian language characteristics"""
        # Check for common Indonesian letter combinations
        indonesian_patterns = ['ng', 'ny', 'sy', 'kh', 'dh', 'th']
        text_lower = text.lower()
        
        for pattern in indonesian_patterns:
            if pattern in text_lower:
                return True
        
        # Check for Indonesian-specific words that are commonly used
        common_id_words = ['saya', 'aku', 'kamu', 'tidak', 'yang', 'dan']
        words = re.findall(r'\b\w+\b', text_lower)
        
        for word in common_id_words:
            if word in words:
                return True
                
        return False
    
    def _has_english_characteristics(self, text: str) -> bool:
        """Check for English language characteristics"""
        # Check for common English letter combinations
        english_patterns = ['th', 'ch', 'sh', 'ck', 'ng']
        text_lower = text.lower()
        
        # Check for English articles and common words
        common_en_words = ['the', 'and', 'or', 'is', 'are', 'have', 'has']
        words = re.findall(r'\b\w+\b', text_lower)
        
        for word in common_en_words:
            if word in words:
                return True
                
        return False
    
    async def is_indonesian(self, text: str, confidence_threshold: float = 0.3) -> bool:
        """Check if text is in Indonesian language"""
        language, confidence = await self.detect_language(text)
        return language == Language.INDONESIAN and confidence >= confidence_threshold
    
    async def is_english(self, text: str, confidence_threshold: float = 0.3) -> bool:
        """Check if text is in English language"""
        language, confidence = await self.detect_language(text)
        return language == Language.ENGLISH and confidence >= confidence_threshold
    
    async def get_language_info(self, text: str) -> Dict[str, any]:
        """Get comprehensive language information"""
        language, confidence = await self.detect_language(text)
        
        return {
            "language": language.value,
            "confidence": confidence,
            "is_indonesian": language == Language.INDONESIAN,
            "is_english": language == Language.ENGLISH,
            "is_unknown": language == Language.UNKNOWN,
            "text_length": len(text),
            "word_count": len(re.findall(r'\b\w+\b', text))
        }

# Global instance
language_service = LanguageService()