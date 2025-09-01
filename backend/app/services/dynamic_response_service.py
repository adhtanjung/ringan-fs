import json
import logging
from typing import Dict, List, Optional, Any
from app.services.ollama_service import OllamaService
from app.services.semantic_search_service import semantic_search_service
from app.services.language_service import language_service, Language

logger = logging.getLogger(__name__)

class DynamicResponseService:
    """
    Service for generating dynamic, context-aware responses using LLM with RAG integration
    and intelligent fallback mechanisms for mental health conversations.
    """

    def __init__(self):
        self.ollama_service = OllamaService()

    async def generate_therapeutic_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        context_type: str = "general",
        user_language: Language = Language.INDONESIAN,
        session_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a dynamic therapeutic response using RAG and LLM

        Args:
            user_message: The user's current message
            conversation_history: Previous conversation messages
            context_type: Type of therapeutic context (general, assessment, crisis, etc.)
            user_language: User's preferred language
            session_data: Additional session context

        Returns:
            Dict containing the response and metadata
        """
        try:
            # Step 1: Search for relevant therapeutic content
            search_results = await self._search_therapeutic_content(
                user_message, context_type, user_language
            )

            # Step 2: Generate context-aware system prompt
            system_prompt = await self._generate_system_prompt(
                context_type, user_language, search_results
            )

            # Step 3: Prepare conversation context
            messages = await self._prepare_conversation_context(
                system_prompt, user_message, conversation_history, search_results
            )

            # Step 4: Generate response using LLM
            response = await self._generate_llm_response(messages, user_language)

            # Step 5: Apply therapeutic enhancements
            enhanced_response = await self._enhance_therapeutic_response(
                response, context_type, user_language, search_results
            )

            return {
                "response": enhanced_response,
                "context_type": context_type,
                "language": user_language.value,
                "has_rag_context": len(search_results) > 0,
                "search_results_count": len(search_results),
                "metadata": {
                    "generated_at": "dynamic",
                    "fallback_used": False
                }
            }

        except Exception as e:
            logger.error(f"Error generating therapeutic response: {str(e)}")
            return await self._generate_fallback_response(
                user_message, context_type, user_language
            )

    async def _search_therapeutic_content(
        self,
        user_message: str,
        context_type: str,
        user_language: Language
    ) -> List[Dict]:
        """
        Search for relevant therapeutic content using semantic search
        """
        try:
            # Enhance search query based on context type
            enhanced_query = await self._enhance_search_query(
                user_message, context_type, user_language
            )

            # Perform semantic search
            search_results = await semantic_search_service.search(
                query=enhanced_query,
                top_k=5,
                threshold=0.7
            )

            return search_results if search_results else []

        except Exception as e:
            logger.error(f"Error searching therapeutic content: {str(e)}")
            return []

    async def _enhance_search_query(
        self,
        user_message: str,
        context_type: str,
        user_language: Language
    ) -> str:
        """
        Enhance the search query based on context and therapeutic needs
        """
        context_keywords = {
            "general": "mental health support counseling",
            "assessment": "psychological assessment evaluation",
            "crisis": "crisis intervention emergency support",
            "anxiety": "anxiety management coping strategies",
            "depression": "depression support therapeutic interventions",
            "stress": "stress management relaxation techniques"
        }

        base_keyword = context_keywords.get(context_type, "mental health support")

        if user_language == Language.INDONESIAN:
            base_keyword += " kesehatan mental konseling"

        return f"{user_message} {base_keyword}"

    async def _generate_system_prompt(
        self,
        context_type: str,
        user_language: Language,
        search_results: List[Dict]
    ) -> str:
        """
        Generate a dynamic system prompt based on context and available knowledge
        Enhanced with therapeutic conversation patterns and context-aware responses
        """
        # Enhanced therapeutic conversation guidelines
        therapeutic_guidelines = {
            Language.INDONESIAN: {
                "core_principles": """Prinsip Terapi:
- Gunakan pendekatan empati dan validasi emosi
- Ajukan pertanyaan terbuka untuk eksplorasi diri
- Berikan refleksi yang mendalam tentang perasaan pengguna
- Tawarkan strategi coping yang praktis dan dapat diterapkan
- Jaga batasan profesional dan arahkan ke bantuan ahli jika diperlukan
- Gunakan teknik active listening dalam respons tertulis
- Hindari memberikan diagnosis atau saran medis langsung""",
                "conversation_flow": """Pola Percakapan:
- Mulai dengan validasi dan pengakuan perasaan
- Eksplorasi lebih dalam dengan pertanyaan reflektif
- Berikan insight atau perspektif baru yang membantu
- Tawarkan langkah konkret atau teknik yang bisa dicoba
- Tutup dengan dukungan dan harapan positif"""
            },
            Language.ENGLISH: {
                "core_principles": """Therapeutic Principles:
- Use empathetic approach and emotional validation
- Ask open-ended questions for self-exploration
- Provide deep reflection on user's feelings
- Offer practical and applicable coping strategies
- Maintain professional boundaries and refer to experts when needed
- Use active listening techniques in written responses
- Avoid giving direct diagnosis or medical advice""",
                "conversation_flow": """Conversation Flow:
- Start with validation and acknowledgment of feelings
- Explore deeper with reflective questions
- Provide helpful insights or new perspectives
- Offer concrete steps or techniques to try
- Close with support and positive hope"""
            }
        }

        base_prompts = {
            Language.INDONESIAN: {
                "general": """Anda adalah Ringan AI, asisten kesehatan mental yang empati, profesional, dan mendukung.

Peran Anda:
- Memberikan dukungan emosional yang hangat dan memahami
- Membantu pengguna mengeksplorasi perasaan dan pikiran mereka
- Menawarkan strategi coping yang praktis dan evidence-based
- Memfasilitasi self-reflection dan pertumbuhan personal
- Mengenali kapan harus merujuk ke bantuan profesional

Gaya Komunikasi:
- Gunakan bahasa yang hangat, tidak menghakimi, dan mendukung
- Tunjukkan empati genuine dalam setiap respons
- Berikan validasi terhadap pengalaman dan perasaan pengguna
- Ajukan pertanyaan yang membantu pengguna memahami diri mereka
- Berikan respons yang personal dan relevan dengan situasi mereka""",

                "assessment": """Anda adalah Ringan AI yang membantu proses assessment kesehatan mental dengan pendekatan yang sensitif dan mendukung.

Tujuan Assessment:
- Membantu pengguna memahami kondisi mental mereka saat ini
- Mengidentifikasi area yang membutuhkan perhatian
- Memberikan insight tentang pola pikir dan perilaku
- Mengarahkan ke langkah-langkah yang tepat untuk perbaikan

Pendekatan:
- Gunakan pertanyaan yang tidak invasif namun mendalam
- Berikan ruang aman untuk eksplorasi diri
- Validasi pengalaman tanpa memberikan label atau diagnosis
- Fokus pada kekuatan dan resiliensi pengguna""",

                "crisis": """Anda adalah Ringan AI yang menangani situasi krisis kesehatan mental dengan prioritas keselamatan dan dukungan segera.

Protokol Krisis:
- Prioritaskan keselamatan pengguna di atas segalanya
- Berikan dukungan emosional segera dan menenangkan
- Arahkan ke layanan darurat (112) jika ada risiko immediate harm
- Tawarkan strategi grounding dan stabilisasi emosi
- Berikan informasi kontak bantuan profesional yang relevan

Pendekatan:
- Tetap tenang dan memberikan rasa aman
- Validasi perasaan tanpa meminimalkan krisis
- Berikan harapan dan perspektif bahwa bantuan tersedia
- Gunakan teknik de-escalation yang gentle namun efektif"""
            },
            Language.ENGLISH: {
                "general": """You are Ringan AI, an empathetic, professional, and supportive mental health assistant.

Your Role:
- Provide warm and understanding emotional support
- Help users explore their feelings and thoughts
- Offer practical and evidence-based coping strategies
- Facilitate self-reflection and personal growth
- Recognize when to refer to professional help

Communication Style:
- Use warm, non-judgmental, and supportive language
- Show genuine empathy in every response
- Validate user experiences and feelings
- Ask questions that help users understand themselves
- Provide personalized and relevant responses to their situation""",

                "assessment": """You are Ringan AI assisting with mental health assessment using a sensitive and supportive approach.

Assessment Goals:
- Help users understand their current mental state
- Identify areas that need attention
- Provide insights about thought and behavior patterns
- Guide toward appropriate next steps for improvement

Approach:
- Use non-invasive yet deep questions
- Provide safe space for self-exploration
- Validate experiences without labeling or diagnosing
- Focus on user strengths and resilience""",

                "crisis": """You are Ringan AI handling mental health crisis situations with safety and immediate support as priorities.

Crisis Protocol:
- Prioritize user safety above all else
- Provide immediate emotional support and calming presence
- Direct to emergency services (112) if there's risk of immediate harm
- Offer grounding strategies and emotional stabilization
- Provide relevant professional help contact information

Approach:
- Stay calm and provide sense of safety
- Validate feelings without minimizing the crisis
- Offer hope and perspective that help is available
- Use gentle yet effective de-escalation techniques"""
            }
        }

        # Get base prompt and therapeutic guidelines
        base_prompt = base_prompts[user_language].get(context_type, base_prompts[user_language]["general"])
        guidelines = therapeutic_guidelines[user_language]

        # Combine base prompt with therapeutic guidelines
        enhanced_prompt = f"{base_prompt}\n\n{guidelines['core_principles']}\n\n{guidelines['conversation_flow']}"

        # Add knowledge context if available
        if search_results:
            knowledge_context = "\n\nRelevant therapeutic knowledge available:\n"
            for i, result in enumerate(search_results[:3], 1):
                content = result.get('content', '')[:300]  # Increased context length
                source = result.get('source', 'Unknown')
                knowledge_context += f"{i}. [{source}] {content}...\n"

            if user_language == Language.INDONESIAN:
                knowledge_context += "\nGunakan informasi ini untuk memberikan respons yang lebih informatif, akurat, dan membantu. Integrasikan pengetahuan ini secara natural dalam percakapan."
            else:
                knowledge_context += "\nUse this information to provide more informative, accurate, and helpful responses. Integrate this knowledge naturally into the conversation."

            enhanced_prompt += knowledge_context

        return enhanced_prompt

    async def _prepare_conversation_context(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: List[Dict],
        search_results: List[Dict]
    ) -> List[Dict]:
        """
        Prepare the conversation context for LLM generation
        """
        messages = [{"role": "system", "content": system_prompt}]

        # Add relevant conversation history (last 4 messages for context)
        for msg in conversation_history[-4:]:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                messages.append(msg)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    async def _generate_llm_response(
        self,
        messages: List[Dict],
        user_language: Language
    ) -> str:
        """
        Generate response using the LLM service with strict language enforcement
        """
        try:
            # Add strict language instruction to the system message
            if messages and messages[0].get('role') == 'system':
                language_instruction = {
                    Language.INDONESIAN: "\n\nIMPORTANT: Respond ONLY in Indonesian (Bahasa Indonesia). Do not mix languages. Use Indonesian throughout your entire response.",
                    Language.ENGLISH: "\n\nIMPORTANT: Respond ONLY in English. Do not mix languages. Use English throughout your entire response."
                }
                
                messages[0]['content'] += language_instruction.get(user_language, language_instruction[Language.INDONESIAN])
            
            response = await self.ollama_service.generate_response(messages=messages)
            return response if isinstance(response, str) else ""
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise

    async def _enhance_therapeutic_response(
        self,
        response: str,
        context_type: str,
        user_language: Language,
        search_results: List[Dict]
    ) -> str:
        """
        Enhance the response with therapeutic patterns and safety checks
        """
        if not response:
            return response

        # Add empathetic acknowledgment if missing
        enhanced_response = await self._add_empathetic_elements(response, user_language)

        # Add safety reminders for crisis situations
        if context_type == "crisis":
            enhanced_response = await self._add_crisis_safety_elements(
                enhanced_response, user_language
            )

        return enhanced_response

    async def _add_empathetic_elements(
        self,
        response: str,
        user_language: Language
    ) -> str:
        """
        Validate empathetic elements in the response (no hardcoded additions)
        The LLM should generate empathetic responses naturally
        """
        # Simply return the response as-is, letting the LLM handle empathy naturally
        # The system prompts should guide the LLM to be empathetic without hardcoded prefixes
        return response

    async def _add_crisis_safety_elements(
        self,
        response: str,
        user_language: Language
    ) -> str:
        """
        Add safety elements for crisis situations
        """
        safety_reminders = {
            Language.INDONESIAN: "\n\nJika Anda merasa dalam bahaya segera, silakan hubungi layanan darurat 112 atau konselor profesional terdekat.",
            Language.ENGLISH: "\n\nIf you're in immediate danger, please contact emergency services 112 or a nearby professional counselor."
        }

        if "112" not in response and "emergency" not in response.lower():
            response += safety_reminders[user_language]

        return response

    async def _generate_fallback_response(
        self,
        user_message: str,
        context_type: str,
        user_language: Language
    ) -> Dict[str, Any]:
        """
        Generate an intelligent fallback response when LLM generation fails
        Uses contextual analysis to provide more helpful and creative responses
        """
        # Analyze user message for emotional context and keywords
        message_lower = user_message.lower()

        # Detect emotional indicators
        emotional_keywords = {
            'stress': ['stress', 'tertekan', 'overwhelmed', 'kewalahan'],
            'anxiety': ['anxious', 'cemas', 'worry', 'khawatir', 'nervous', 'gugup'],
            'depression': ['sad', 'sedih', 'depressed', 'depresi', 'hopeless', 'putus asa'],
            'anger': ['angry', 'marah', 'frustrated', 'frustrasi', 'annoyed', 'kesal'],
            'fear': ['afraid', 'takut', 'scared', 'ketakutan', 'phobia', 'fobia']
        }

        detected_emotion = None
        for emotion, keywords in emotional_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_emotion = emotion
                break

        # Generate contextual responses based on detected emotion and context
        if user_language == Language.INDONESIAN:
            if detected_emotion == 'stress':
                response = "Saya memahami bahwa Anda sedang merasa tertekan. Stres adalah respons alami tubuh terhadap tantangan. Mari kita coba teknik pernapasan sederhana: tarik napas dalam-dalam selama 4 detik, tahan 4 detik, lalu hembuskan perlahan selama 6 detik. Apa yang paling membuat Anda merasa tertekan saat ini?"
            elif detected_emotion == 'anxiety':
                response = "Kecemasan yang Anda rasakan sangat dapat dipahami. Ketika pikiran terasa berputar-putar, cobalah untuk fokus pada hal-hal yang dapat Anda kontrol saat ini. Bisakah Anda menyebutkan 3 hal di sekitar Anda yang dapat Anda lihat, 2 hal yang dapat Anda dengar, dan 1 hal yang dapat Anda sentuh?"
            elif detected_emotion == 'depression':
                response = "Terima kasih telah berani berbagi perasaan Anda. Kesedihan yang mendalam memang berat untuk dihadapi sendirian. Ingatlah bahwa perasaan ini tidak akan berlangsung selamanya. Apakah ada aktivitas kecil yang biasanya membuat Anda merasa sedikit lebih baik, meskipun hanya sebentar?"
            elif detected_emotion == 'anger':
                response = "Kemarahan adalah emosi yang valid dan wajar dirasakan. Penting untuk mengakui perasaan ini tanpa menghakimi diri sendiri. Ketika emosi terasa intens, kadang membantu untuk mengambil jeda sejenak. Apa yang menurut Anda memicu perasaan ini?"
            elif detected_emotion == 'fear':
                response = "Ketakutan adalah sinyal perlindungan alami dari tubuh kita. Meskipun tidak nyaman, perasaan ini menunjukkan bahwa Anda peduli dengan keselamatan diri. Mari kita coba memahami lebih dalam - apakah ketakutan ini terkait dengan situasi spesifik atau lebih umum?"
            else:
                # General contextual response based on context_type
                if context_type == "assessment":
                    response = "Saya menghargai kepercayaan Anda untuk berbagi. Meskipun saya tidak memiliki akses ke informasi spesifik saat ini, saya tetap ingin membantu Anda memahami kondisi yang Anda alami. Bisakah Anda menjelaskan gejala atau perasaan yang paling mengganggu Anda belakangan ini?"
                elif context_type == "crisis":
                    response = "Saya mendengar bahwa Anda mungkin sedang dalam situasi yang menantang. Keselamatan dan kesejahteraan Anda adalah yang terpenting. Jika ini adalah keadaan darurat, jangan ragu untuk menghubungi 112. Saya di sini untuk mendengarkan dan mendukung Anda sebisa mungkin."
                else:
                    response = "Terima kasih telah mempercayai saya dengan perasaan Anda. Setiap orang memiliki pengalaman yang unik, dan saya ingin memahami perspektif Anda dengan lebih baik. Apa yang paling Anda butuhkan dari percakapan kita hari ini?"
        else:  # English
            if detected_emotion == 'stress':
                response = "I understand you're feeling overwhelmed. Stress is a natural response to challenges. Let's try a simple breathing technique: breathe in deeply for 4 seconds, hold for 4 seconds, then exhale slowly for 6 seconds. What's contributing most to your stress right now?"
            elif detected_emotion == 'anxiety':
                response = "The anxiety you're experiencing is completely understandable. When thoughts feel overwhelming, try focusing on what you can control right now. Can you name 3 things you can see around you, 2 things you can hear, and 1 thing you can touch?"
            elif detected_emotion == 'depression':
                response = "Thank you for having the courage to share your feelings. Deep sadness can feel overwhelming to face alone. Remember that these feelings won't last forever. Is there a small activity that usually helps you feel even slightly better, even if just for a moment?"
            elif detected_emotion == 'anger':
                response = "Anger is a valid and natural emotion to experience. It's important to acknowledge these feelings without judging yourself. When emotions feel intense, sometimes taking a brief pause can help. What do you think might be triggering these feelings?"
            elif detected_emotion == 'fear':
                response = "Fear is our body's natural protection signal. While uncomfortable, this feeling shows that you care about your safety. Let's try to understand this better - is this fear related to a specific situation or more general?"
            else:
                # General contextual response based on context_type
                if context_type == "assessment":
                    response = "I appreciate your trust in sharing with me. While I don't have access to specific information right now, I still want to help you understand what you're experiencing. Could you describe the symptoms or feelings that have been most troubling for you lately?"
                elif context_type == "crisis":
                    response = "I hear that you might be going through a challenging situation. Your safety and wellbeing are most important. If this is an emergency, please don't hesitate to contact 112. I'm here to listen and support you as best I can."
                else:
                    response = "Thank you for trusting me with your feelings. Everyone has unique experiences, and I want to better understand your perspective. What do you need most from our conversation today?"

        return {
            "response": response,
            "context_type": context_type,
            "language": user_language.value,
            "has_rag_context": False,
            "search_results_count": 0,
            "detected_emotion": detected_emotion,
            "metadata": {
                "generated_at": "intelligent_fallback",
                "fallback_used": True,
                "emotion_detected": detected_emotion is not None
            }
        }

    async def generate_simple_response(
        self,
        prompt: str,
        user_language: Language = Language.INDONESIAN,
        context_type: str = "general"
    ) -> str:
        """
        Generate a simple therapeutic response from a prompt
        """
        try:
            # Generate system prompt for simple response
            system_prompt = await self._generate_system_prompt(
                context_type, user_language, []
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            response = await self._generate_llm_response(messages, user_language)

            # Apply basic therapeutic enhancements
            enhanced_response = await self._enhance_therapeutic_response(
                response, context_type, user_language, []
            )

            return enhanced_response

        except Exception as e:
            logger.error(f"Error generating simple response: {str(e)}")
            # Return a basic fallback
            if user_language == Language.INDONESIAN:
                return "Saya memahami situasi Anda dan ingin membantu. Bisakah Anda menceritakan lebih detail?"
            else:
                return "I understand your situation and want to help. Could you tell me more details?"

    async def generate_error_response(
        self,
        user_language: Language = Language.INDONESIAN
    ) -> str:
        """
        Generate a user-friendly error response
        """
        error_responses = {
            Language.INDONESIAN: "Maaf, saya mengalami kendala teknis saat ini. Silakan coba lagi dalam beberapa saat. Jika ini adalah situasi darurat, segera hubungi 112.",
            Language.ENGLISH: "Sorry, I'm experiencing technical difficulties right now. Please try again in a moment. If this is an emergency, please contact 112 immediately."
        }

        return error_responses[user_language]

# Create global instance
dynamic_response_service = DynamicResponseService()