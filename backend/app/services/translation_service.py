"""\nTranslation Service for Multilingual Support\nHandles translation between Indonesian and English for vector database compatibility\n"""

import logging
import asyncio
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor
import re

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for translating text between Indonesian and English"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Mental health terminology mapping (Indonesian -> English)
        self.mental_health_terms = {
            # Emotions and feelings
            'cemas': 'anxious',
            'kecemasan': 'anxiety',
            'khawatir': 'worried',
            'kekhawatiran': 'worry',
            'takut': 'afraid',
            'ketakutan': 'fear',
            'sedih': 'sad',
            'kesedihan': 'sadness',
            'depresi': 'depression',
            'tertekan': 'depressed',
            'stres': 'stress',
            'stress': 'stress',
            'gelisah': 'restless',
            'panik': 'panic',
            'trauma': 'trauma',
            'marah': 'angry',
            'kemarahan': 'anger',
            'frustrasi': 'frustration',
            'putus asa': 'hopeless',
            'keputusasaan': 'hopelessness',
            'lelah': 'tired',
            'kelelahan': 'fatigue',
            'bingung': 'confused',
            'kebingungan': 'confusion',
            
            # Mental health concepts
            'kesehatan mental': 'mental health',
            'kesehatan jiwa': 'mental health',
            'gangguan mental': 'mental disorder',
            'penyakit mental': 'mental illness',
            'masalah psikologis': 'psychological problems',
            'kondisi mental': 'mental condition',
            
            # Symptoms and experiences
            'sulit tidur': 'difficulty sleeping',
            'insomnia': 'insomnia',
            'mimpi buruk': 'nightmares',
            'jantung berdebar': 'heart racing',
            'sesak napas': 'shortness of breath',
            'berkeringat': 'sweating',
            'gemetar': 'trembling',
            'pusing': 'dizzy',
            'mual': 'nauseous',
            'sakit kepala': 'headache',
            'kehilangan nafsu makan': 'loss of appetite',
            'makan berlebihan': 'overeating',
            'sulit konsentrasi': 'difficulty concentrating',
            'pelupa': 'forgetful',
            'mudah tersinggung': 'easily irritated',
            'mood swing': 'mood swings',
            'perubahan suasana hati': 'mood changes',
            
            # Treatment and support
            'bantuan': 'help',
            'dukungan': 'support',
            'konseling': 'counseling',
            'terapi': 'therapy',
            'psikolog': 'psychologist',
            'psikiater': 'psychiatrist',
            'dokter': 'doctor',
            'pengobatan': 'treatment',
            'obat': 'medication',
            'rehabilitasi': 'rehabilitation',
            'pemulihan': 'recovery',
            
            # Common expressions
            'merasa': 'feel',
            'perasaan': 'feeling',
            'emosi': 'emotion',
            'pikiran': 'thoughts',
            'hati': 'heart',
            'jiwa': 'soul',
            'mental': 'mental',
            'fisik': 'physical',
            'tubuh': 'body',
            'masalah': 'problem',
            'kesulitan': 'difficulty',
            'tantangan': 'challenge',
            'situasi': 'situation',
            'kondisi': 'condition',
            'keadaan': 'state',
            
            # Time expressions
            'hari ini': 'today',
            'kemarin': 'yesterday',
            'besok': 'tomorrow',
            'minggu ini': 'this week',
            'bulan ini': 'this month',
            'tahun ini': 'this year',
            'sekarang': 'now',
            'saat ini': 'currently',
            'belakangan ini': 'lately',
            'akhir-akhir ini': 'recently',
            
            # Intensity and frequency
            'sangat': 'very',
            'sekali': 'very',
            'agak': 'somewhat',
            'sedikit': 'a little',
            'kadang': 'sometimes',
            'kadang-kadang': 'sometimes',
            'sering': 'often',
            'selalu': 'always',
            'tidak pernah': 'never',
            'jarang': 'rarely',
            'biasanya': 'usually',
        }
        
        # Common word translations
        self.common_words = {
            'saya': 'I',
            'aku': 'I',
            'kamu': 'you',
            'anda': 'you',
            'dia': 'he/she',
            'mereka': 'they',
            'kita': 'we',
            'kami': 'we',
            'yang': 'that/which',
            'dan': 'and',
            'atau': 'or',
            'dengan': 'with',
            'untuk': 'for',
            'dari': 'from',
            'ke': 'to',
            'di': 'in/at',
            'pada': 'on/at',
            'tidak': 'not',
            'bukan': 'not',
            'belum': 'not yet',
            'sudah': 'already',
            'akan': 'will',
            'sedang': 'currently',
            'telah': 'have',
            'ini': 'this',
            'itu': 'that',
            'adalah': 'is',
            'ada': 'there is/are',
            'menjadi': 'become',
            'dapat': 'can',
            'bisa': 'can',
            'bagaimana': 'how',
            'mengapa': 'why',
            'kenapa': 'why',
            'dimana': 'where',
            'kapan': 'when',
            'siapa': 'who',
            'apa': 'what',
            'berapa': 'how many',
            'mana': 'which',
            'seperti': 'like',
            'kalau': 'if',
            'jika': 'if',
            'bila': 'if',
            'tolong': 'please',
            'mohon': 'please',
            'terima kasih': 'thank you',
            'maaf': 'sorry',
        }
    
    def _translate_word_by_word(self, text: str) -> str:
        """Translate text word by word using dictionary mapping"""
        words = text.lower().split()
        translated_words = []
        
        i = 0
        while i < len(words):
            # Try to match multi-word phrases first
            matched = False
            
            # Check for 3-word phrases
            if i + 2 < len(words):
                phrase = ' '.join(words[i:i+3])
                if phrase in self.mental_health_terms:
                    translated_words.append(self.mental_health_terms[phrase])
                    i += 3
                    matched = True
                elif phrase in self.common_words:
                    translated_words.append(self.common_words[phrase])
                    i += 3
                    matched = True
            
            # Check for 2-word phrases
            if not matched and i + 1 < len(words):
                phrase = ' '.join(words[i:i+2])
                if phrase in self.mental_health_terms:
                    translated_words.append(self.mental_health_terms[phrase])
                    i += 2
                    matched = True
                elif phrase in self.common_words:
                    translated_words.append(self.common_words[phrase])
                    i += 2
                    matched = True
            
            # Check for single words
            if not matched:
                word = words[i]
                if word in self.mental_health_terms:
                    translated_words.append(self.mental_health_terms[word])
                elif word in self.common_words:
                    translated_words.append(self.common_words[word])
                else:
                    # Keep the original word if no translation found
                    translated_words.append(word)
                i += 1
        
        return ' '.join(translated_words)
    
    def _clean_translation(self, text: str) -> str:
        """Clean and improve the translated text"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Basic grammar improvements
        text = re.sub(r'\bi am\b', 'I am', text, flags=re.IGNORECASE)
        text = re.sub(r'\bi\s+', 'I ', text)
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    async def translate_indonesian_to_english(self, text: str) -> str:
        """\n        Translate Indonesian text to English\n        Focuses on mental health terminology and common expressions\n        """
        try:
            if not text or not text.strip():
                return text
            
            # Run translation in thread to avoid blocking
            loop = asyncio.get_event_loop()
            translated = await loop.run_in_executor(
                self.executor,
                self._translate_word_by_word,
                text
            )
            
            # Clean the translation
            cleaned = self._clean_translation(translated)
            
            logger.info(f"Translated: '{text}' -> '{cleaned}'")
            return cleaned
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return text  # Return original text if translation fails
    
    async def translate_english_to_indonesian(self, text: str) -> str:
        """\n        Translate English text to Indonesian\n        Uses reverse mapping of the dictionary\n        """
        try:
            if not text or not text.strip():
                return text
            
            # Create reverse mapping
            reverse_mental_health = {v: k for k, v in self.mental_health_terms.items()}
            reverse_common = {v: k for k, v in self.common_words.items()}
            
            words = text.lower().split()
            translated_words = []
            
            for word in words:
                if word in reverse_mental_health:
                    translated_words.append(reverse_mental_health[word])
                elif word in reverse_common:
                    translated_words.append(reverse_common[word])
                else:
                    translated_words.append(word)
            
            translated = ' '.join(translated_words)
            cleaned = self._clean_translation(translated)
            
            logger.info(f"Translated: '{text}' -> '{cleaned}'")
            return cleaned
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return text
    
    async def get_translation_info(self, text: str, target_language: str) -> Dict[str, any]:
        """Get translation information and statistics"""
        original_words = len(text.split())
        
        if target_language.lower() == 'english':
            translated = await self.translate_indonesian_to_english(text)
        elif target_language.lower() == 'indonesian':
            translated = await self.translate_english_to_indonesian(text)
        else:
            translated = text
        
        translated_words = len(translated.split())
        
        return {
            "original_text": text,
            "translated_text": translated,
            "target_language": target_language,
            "original_word_count": original_words,
            "translated_word_count": translated_words,
            "translation_ratio": translated_words / original_words if original_words > 0 else 0
        }
    
    def get_supported_terms(self) -> Dict[str, List[str]]:
        """Get list of supported translation terms"""
        return {
            "mental_health_terms": list(self.mental_health_terms.keys()),
            "common_words": list(self.common_words.keys()),
            "total_terms": len(self.mental_health_terms) + len(self.common_words)
        }

# Global instance
translation_service = TranslationService()