import httpx
import json
import asyncio
from typing import List, Dict, Optional, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.temperature = settings.OLLAMA_TEMPERATURE
        self.max_tokens = settings.OLLAMA_MAX_TOKENS

        # Mental health specific system prompt
        self.system_prompt = """Kamu adalah Ringan AI, asisten kesehatan mental yang ramah dan empatik. Kamu berperan sebagai psikolog yang melakukan konsultasi dengan pendekatan dialog interaktif.

PRINSIP UTAMA:
1. SELALU gunakan pendekatan dialog - ajukan SATU pertanyaan pada satu waktu
2. Jangan memberikan saran panjang atau daftar tips secara langsung
3. Fokus pada eksplorasi masalah melalui pertanyaan yang tepat
4. Bangun pemahaman bertahap tentang situasi pengguna
5. Gunakan bahasa yang hangat, empatik, dan mudah dipahami

FORMAT RESPONS:
- Berikan respons singkat dan fokus (maksimal 2-3 kalimat)
- Akhiri dengan SATU pertanyaan spesifik untuk menggali lebih dalam
- Gunakan emoji secukupnya untuk kehangatan
- Hindari memberikan daftar atau tips panjang

CONTOH DIALOG:
User: "Saya merasa stres dengan pekerjaan"
AI: "Saya memahami perasaan stres karena pekerjaan bisa sangat melelahkan 😔 Boleh ceritakan lebih spesifik apa yang membuat kamu merasa paling tertekan di tempat kerja?"

PENTING: Jika pengguna menunjukkan tanda-tanda krisis atau bahaya diri, segera berikan respons yang mendukung dan arahkan ke bantuan profesional."""

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """
        Generate response from Ollama model
        """
        try:
            # Use the messages as-is since they already contain the appropriate system prompt
            # from the dynamic_response_service based on user language and context
            conversation = messages

            payload = {
                "model": self.model,
                "messages": conversation,
                "stream": stream,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code != 200:
                    logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                    raise Exception(f"Ollama API error: {response.status_code}")

                data = response.json()
                return data.get("message", {}).get("content", "")

        except Exception as e:
            logger.error(f"Error generating Ollama response: {str(e)}")
            raise

    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]]
    ):
        """
        Generate streaming response from Ollama model
        """
        try:
            # Use the messages as-is since they already contain the appropriate system prompt
            # from the dynamic_response_service based on user language and context
            conversation = messages

            payload = {
                "model": self.model,
                "messages": conversation,
                "stream": True,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status_code != 200:
                        logger.error(f"Ollama streaming API error: {response.status_code}")
                        raise Exception(f"Ollama streaming API error: {response.status_code}")

                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    yield data["message"]["content"]
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Error generating streaming Ollama response: {str(e)}")
            raise

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment and emotion of user input
        """
        try:
            analysis_prompt = f"""
            Analisis perasaan dan emosi dari teks berikut. Berikan respons dalam format JSON:
            {{
                "sentiment": "positive/negative/neutral",
                "emotion": "sad/anxious/angry/happy/stressed/neutral",
                "confidence": 0.0-1.0,
                "crisis_risk": "low/medium/high"
            }}

            Teks: {text}
            """

            messages = [{"role": "user", "content": analysis_prompt}]
            response = await self.generate_response(messages)

            # Try to parse JSON response
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass

            # Fallback analysis
            return self._fallback_sentiment_analysis(text)

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return self._fallback_sentiment_analysis(text)

    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Simple fallback sentiment analysis using keyword matching
        """
        text_lower = text.lower()

        # Crisis detection
        crisis_keywords = settings.CRISIS_KEYWORDS
        crisis_risk = "low"
        for keyword in crisis_keywords:
            if keyword.lower() in text_lower:
                crisis_risk = "high"
                break

        # Emotion detection
        emotion = "neutral"
        if any(word in text_lower for word in ["sedih", "sad", "down", "murung"]):
            emotion = "sad"
        elif any(word in text_lower for word in ["cemas", "anxious", "worry", "khawatir"]):
            emotion = "anxious"
        elif any(word in text_lower for word in ["marah", "angry", "frustasi", "kesal"]):
            emotion = "angry"
        elif any(word in text_lower for word in ["bahagia", "happy", "senang", "gembira"]):
            emotion = "happy"
        elif any(word in text_lower for word in ["stress", "overwhelmed", "capek", "lelah"]):
            emotion = "stressed"

        # Sentiment
        sentiment = "neutral"
        if emotion in ["happy"]:
            sentiment = "positive"
        elif emotion in ["sad", "anxious", "angry", "stressed"]:
            sentiment = "negative"

        return {
            "sentiment": sentiment,
            "emotion": emotion,
            "confidence": 0.6,
            "crisis_risk": crisis_risk
        }

    async def check_model_availability(self) -> bool:
        """
        Check if Ollama model is available
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return any(model["name"] == self.model for model in models)
                return False
        except Exception as e:
            logger.error(f"Error checking model availability: {str(e)}")
            return False

    async def pull_model(self) -> bool:
        """
        Pull the specified model if not available
        """
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": self.model}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
            return False


