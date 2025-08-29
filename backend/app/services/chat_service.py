import json
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.services.ollama_service import OllamaService
from app.services.semantic_search_service import semantic_search_service
from app.services.assessment_service import assessment_service
from app.services.language_service import language_service, Language
from app.services.translation_service import translation_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.ollama_service = OllamaService()
        self.conversation_history: Dict[str, List[Dict]] = {}

    async def _generate_semantic_context(self, message: str, translated_message: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate semantic context from user message using vector search
        Uses translated message for better English vector database compatibility
        """
        try:
            # Initialize semantic search service if needed
            await semantic_search_service.initialize()

            context_results = []
            
            # Use translated message for vector search if available, otherwise use original
            search_query = translated_message if translated_message else message
            logger.info(f"Searching with query: '{search_query}'")

            # Search for relevant problems
            problems_search = await semantic_search_service.search_problems(
                query=search_query,
                limit=2,
                score_threshold=0.4
            )

            if problems_search.success and problems_search.results:
                context_results.extend(problems_search.results)

            # Search for relevant suggestions
            suggestions_search = await semantic_search_service.search_therapeutic_suggestions(
                problem_description=search_query,
                limit=2,
                score_threshold=0.4
            )

            if suggestions_search.success and suggestions_search.results:
                context_results.extend(suggestions_search.results)

            # Search for relevant assessment questions
            assessments_search = await semantic_search_service.search_assessment_questions(
                problem_description=search_query,
                limit=2,
                score_threshold=0.4
            )

            if assessments_search.success and assessments_search.results:
                context_results.extend(assessments_search.results)

            logger.info(f"Generated semantic context with {len(context_results)} results")
            return context_results

        except Exception as e:
            logger.error(f"Failed to generate semantic context: {str(e)}")
            return []

    async def _get_relevant_resources(self, message: str, problem_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get relevant resources and suggestions based on user message
        """
        try:
            await semantic_search_service.initialize()

            resources = []

            # Search for therapeutic suggestions
            suggestions_search = await semantic_search_service.search_therapeutic_suggestions(
                problem_description=message,
                limit=3,
                score_threshold=0.4
            )

            if suggestions_search.success and suggestions_search.results:
                for result in suggestions_search.results:
                    resources.append({
                        "type": "suggestion",
                        "content": result.payload.get("suggestion_text", ""),
                        "evidence_based": result.payload.get("evidence_based", True),
                        "resource_link": result.payload.get("resource_link"),
                        "score": result.score
                    })

            return resources

        except Exception as e:
            logger.error(f"Failed to get relevant resources: {str(e)}")
            return []

    async def _get_assessment_recommendations(self, message: str) -> Dict[str, Any]:
        """
        Get assessment recommendations based on user message
        """
        try:
            await semantic_search_service.initialize()

            # Search for relevant assessment questions
            assessments_search = await semantic_search_service.search_assessment_questions(
                problem_description=message,
                limit=5,
                score_threshold=0.4
            )

            if assessments_search.success and assessments_search.results:
                questions = []
                for result in assessments_search.results:
                    questions.append({
                        "question_id": result.payload.get("question_id", ""),
                        "question_text": result.payload.get("text", ""),  # Use 'text' field from payload
                        "response_type": result.payload.get("response_type", "text"),
                        "score": result.score
                    })

                return {
                    "recommended_questions": questions,
                    "total_questions": len(questions),
                    "assessment_ready": len(questions) > 0
                }

            return {"recommended_questions": [], "total_questions": 0, "assessment_ready": False}

        except Exception as e:
            logger.error(f"Failed to get assessment recommendations: {str(e)}")
            return {"recommended_questions": [], "total_questions": 0, "assessment_ready": False}

    async def _analyze_problem_context(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Analyze conversation context to identify potential mental health problem categories
        """
        try:
            # Combine current message with recent conversation history for context
            context_text = message
            if conversation_history:
                recent_messages = conversation_history[-5:]  # Last 5 messages for context
                context_parts = [msg.get('content', '') for msg in recent_messages if msg.get('role') == 'user']
                context_text = ' '.join(context_parts + [message])

            # Search for matching problem categories
            problem_search = await semantic_search_service.search_problems(
                query=context_text,
                limit=5,
                score_threshold=0.4
            )

            detected_problems = []
            confidence_scores = []
            
            if problem_search.success and problem_search.results:
                for result in problem_search.results:
                    payload = result.payload
                    detected_problems.append({
                        "category": payload.get('category', ''),
                        "sub_category": payload.get('sub_category', ''),
                        "sub_category_id": payload.get('sub_category_id', ''),
                        "domain": payload.get('domain', ''),
                        "confidence": result.score,
                        "description": payload.get('text', '')
                    })
                    confidence_scores.append(result.score)

            # Determine if we have high confidence in problem identification
            max_confidence = max(confidence_scores) if confidence_scores else 0
            should_suggest_assessment = max_confidence > 0.6 and len(detected_problems) > 0

            return {
                "detected_problems": detected_problems,
                "max_confidence": max_confidence,
                "should_suggest_assessment": should_suggest_assessment,
                "primary_category": detected_problems[0].get('category', '') if detected_problems else None,
                "primary_sub_category_id": detected_problems[0].get('sub_category_id', '') if detected_problems else None
            }

        except Exception as e:
            logger.error(f"Error analyzing problem context: {str(e)}")
            return {
                "detected_problems": [],
                "max_confidence": 0,
                "should_suggest_assessment": False,
                "primary_category": None,
                "primary_sub_category_id": None
            }

    async def _should_transition_to_assessment(self, context_analysis: Dict, conversation_history: List[Dict]) -> bool:
        """
        Determine if the conversation should transition to structured assessment
        """
        try:
            # Check confidence level
            if context_analysis.get('max_confidence', 0) < 0.6:
                return False

            # Check if user has been discussing problems for multiple messages
            if len(conversation_history) >= 6:  # At least 3 exchanges
                return True

            # Check for explicit distress indicators
            recent_messages = conversation_history[-3:] if conversation_history else []
            distress_keywords = ['help', 'stressed', 'anxious', 'depressed', 'overwhelmed', 'struggling', 'difficult']
            
            for msg in recent_messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '').lower()
                    if any(keyword in content for keyword in distress_keywords):
                        return True

            return False

        except Exception as e:
            logger.error(f"Error determining assessment transition: {str(e)}")
            return False

    async def process_message(
        self,
        message: str,
        client_id: str,
        session_data: Optional[Dict] = None,
        semantic_context: Optional[List[Dict]] = None,
        problem_category: Optional[str] = None,
        assessment_progress: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process incoming chat message and generate response with semantic search integration
        Now supports multilingual interactions with language detection and translation
        """
        try:
            # Initialize conversation history for client if not exists
            if client_id not in self.conversation_history:
                self.conversation_history[client_id] = []

            # Step 1: Detect language of user input
            detected_language, confidence = await language_service.detect_language(message)
            logger.info(f"Detected language: {detected_language.value} (confidence: {confidence:.2f})")
            
            # Step 2: Translate to English if needed for vector search
            translated_message = None
            if detected_language == Language.INDONESIAN:
                translated_message = await translation_service.translate_indonesian_to_english(message)
                logger.info(f"Translated for search: '{message}' -> '{translated_message}'")
            
            # Step 3: Analyze sentiment (use original message for better accuracy)
            sentiment_analysis = await self.ollama_service.analyze_sentiment(message)

            # Check for crisis keywords
            is_crisis = sentiment_analysis.get("crisis_risk") == "high"

            # Step 4: Generate semantic context using translated message if available
            if semantic_context is None:
                search_results = await self._generate_semantic_context(message, translated_message)
                # Convert SearchResult objects to dictionaries
                semantic_context = []
                for result in search_results:
                    semantic_context.append({
                        "id": result.id,
                        "score": result.score,
                        "payload": result.payload
                    })

            # Get relevant resources and assessment recommendations
            relevant_resources = await self._get_relevant_resources(message, problem_category)
            assessment_recommendations = await self._get_assessment_recommendations(message)

            # Prepare conversation context
            conversation_messages = self._prepare_conversation_context(
                client_id,
                message,
                session_data,
                semantic_context,
                problem_category,
                assessment_progress
            )

            # Step 5: Generate AI response
            if is_crisis:
                ai_response = await self._generate_crisis_response(message)
            else:
                ai_response = await self.ollama_service.generate_response(conversation_messages)

            # Get current conversation history
            current_history = self.conversation_history.get(client_id, [])

            # Analyze problem context using AI-powered analysis
            context_analysis = await self._analyze_problem_context(message, current_history)
            
            # Determine if we should suggest transitioning to structured assessment
            should_transition = await self._should_transition_to_assessment(context_analysis, current_history)

            # Use detected problem category if not explicitly provided
            if not problem_category and context_analysis.get('primary_category'):
                problem_category = context_analysis.get('primary_category')

            # Add context analysis to conversation for AI awareness
            if context_analysis.get('detected_problems'):
                context_info = f"Detected potential concerns: {', '.join([p.get('category', '') for p in context_analysis['detected_problems'][:2]])}"
                conversation_messages.insert(-1, {"role": "system", "content": context_info})

            # Enhance AI response with assessment suggestion if appropriate
            if should_transition and context_analysis.get('should_suggest_assessment'):
                primary_problem = context_analysis.get('detected_problems', [{}])[0]
                if detected_language == Language.INDONESIAN:
                    assessment_suggestion = f"\n\nBerdasarkan percakapan kita, saya melihat Anda mungkin mengalami {primary_problem.get('category', 'masalah')}. Apakah Anda ingin melakukan assessment terstruktur untuk membantu memahami situasi Anda lebih baik?"
                else:
                    assessment_suggestion = f"\n\nBased on our conversation, I see you might be experiencing {primary_problem.get('category', 'issues')}. Would you like to take a structured assessment to help understand your situation better?"
                ai_response += assessment_suggestion
            
            # Step 6: Translate response back to user's language if needed
            if detected_language == Language.INDONESIAN and confidence > 0.3:
                # If the AI response is in English, translate it to Indonesian
                # Check if response needs translation (simple heuristic)
                response_language, response_confidence = await language_service.detect_language(ai_response)
                if response_language == Language.ENGLISH and response_confidence > 0.3:
                    ai_response = await translation_service.translate_english_to_indonesian(ai_response)
                    logger.info(f"Translated response back to Indonesian")

            # Store conversation
            self._store_conversation(client_id, message, ai_response, sentiment_analysis)

            # Prepare response with enhanced context
            response_data = {
                "message": ai_response,
                "sentiment": sentiment_analysis,
                "is_crisis": is_crisis,
                "timestamp": datetime.now().isoformat(),
                "conversation_id": client_id,
                "semantic_context": semantic_context,
                "relevant_resources": relevant_resources,
                "assessment_recommendations": assessment_recommendations,
                "context_analysis": context_analysis,
                "should_suggest_assessment": should_transition,
                "detected_problem_category": problem_category
            }

            return response_data

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Provide error message in appropriate language
            try:
                # Try to detect language for error message
                detected_language, _ = await language_service.detect_language(message)
                if detected_language == Language.ENGLISH:
                    error_message = "Sorry, a technical error occurred. Please try again. If this is an emergency, please contact 112 immediately."
                else:
                    error_message = "Maaf, terjadi kesalahan teknis. Silakan coba lagi. Jika ini adalah situasi darurat, segera hubungi 112."
            except:
                # Fallback to Indonesian if language detection fails
                error_message = "Maaf, terjadi kesalahan teknis. Silakan coba lagi. Jika ini adalah situasi darurat, segera hubungi 112."
            
            return {
                "message": error_message,
                "sentiment": {
                    "overall": "neutral",
                    "crisis_risk": "low",
                    "confidence": 0.0
                },
                "is_crisis": False,
                "timestamp": datetime.now().isoformat(),
                "conversation_id": client_id,
                "semantic_context": None,
                "relevant_resources": None,
                "assessment_recommendations": None,
                "context_analysis": {"detected_problems": [], "should_suggest_assessment": False},
                "should_suggest_assessment": False,
                "detected_problem_category": None
            }

    async def process_streaming_message(
        self,
        message: str,
        client_id: str,
        session_data: Optional[Dict] = None,
        semantic_context: Optional[List[Dict]] = None,
        problem_category: Optional[str] = None,
        assessment_progress: Optional[Dict] = None
    ):
        """
        Process message with streaming response and semantic search integration
        """
        try:
            # Initialize conversation history for client if not exists
            if client_id not in self.conversation_history:
                self.conversation_history[client_id] = []

            # Step 1: Detect language
            detected_language, confidence = await language_service.detect_language(message)
            logger.info(f"Detected language: {detected_language.value} (confidence: {confidence})")

            # Step 2: Translate message if needed for vector search
            translated_message = None
            if detected_language == Language.INDONESIAN and confidence > 0.3:
                translated_message = await translation_service.translate_indonesian_to_english(message)
                logger.info(f"Translated message for search: {translated_message[:100]}...")

            # Get current conversation history
            current_history = self.conversation_history.get(client_id, [])

            # Analyze sentiment
            sentiment_analysis = await self.ollama_service.analyze_sentiment(message)

            # Check for crisis keywords
            is_crisis = sentiment_analysis.get("crisis_risk") == "high"

            # Analyze problem context using AI-powered analysis
            context_analysis = await self._analyze_problem_context(message, current_history)
            
            # Determine if we should suggest transitioning to structured assessment
            should_transition = await self._should_transition_to_assessment(context_analysis, current_history)

            # Generate semantic context if not provided
            if semantic_context is None:
                search_results = await self._generate_semantic_context(message, translated_message)
                # Convert SearchResult objects to dictionaries
                semantic_context = []
                for result in search_results:
                    semantic_context.append({
                        "id": result.id,
                        "score": result.score,
                        "payload": result.payload
                    })

            # Use detected problem category if not explicitly provided
            if not problem_category and context_analysis.get('primary_category'):
                problem_category = context_analysis.get('primary_category')

            # Get relevant resources and assessment recommendations
            relevant_resources = await self._get_relevant_resources(message, problem_category)
            assessment_recommendations = await self._get_assessment_recommendations(message)

            # Check for crisis
            is_crisis = sentiment_analysis.get("crisis_risk") == "high"

            # Prepare conversation context
            conversation_messages = self._prepare_conversation_context(
                client_id,
                message,
                session_data,
                semantic_context,
                problem_category,
                assessment_progress
            )

            # Add context analysis to conversation for AI awareness
            if context_analysis.get('detected_problems'):
                context_info = f"Detected potential concerns: {', '.join([p.get('category', '') for p in context_analysis['detected_problems'][:2]])}"
                conversation_messages.insert(-1, {"role": "system", "content": context_info})

            # Generate streaming response
            if is_crisis:
                ai_response = await self._generate_crisis_response(message)
                yield json.dumps({
                    "type": "message",
                    "content": ai_response,
                    "sentiment": sentiment_analysis,
                    "is_crisis": True,
                    "timestamp": datetime.now().isoformat(),
                    "context_analysis": context_analysis,
                    "detected_language": detected_language.value if 'detected_language' in locals() else "indonesian"
                })
            else:
                full_response = ""
                async for chunk in self.ollama_service.generate_streaming_response(conversation_messages):
                    full_response += chunk
                    yield json.dumps({
                        "type": "chunk",
                        "content": chunk,
                        "timestamp": datetime.now().isoformat(),
                        "semantic_context": semantic_context,
                        "relevant_resources": relevant_resources,
                        "assessment_recommendations": assessment_recommendations,
                        "context_analysis": context_analysis,
                        "should_suggest_assessment": should_transition
                    })

                # Add assessment suggestion if appropriate
                if should_transition and context_analysis.get('should_suggest_assessment'):
                    primary_problem = context_analysis.get('detected_problems', [{}])[0]
                    if detected_language == Language.INDONESIAN:
                        assessment_suggestion = f"\n\nBerdasarkan percakapan kita, saya melihat Anda mungkin mengalami {primary_problem.get('category', 'masalah')}. Apakah Anda ingin melakukan assessment terstruktur untuk membantu memahami situasi Anda lebih baik?"
                    else:
                        assessment_suggestion = f"\n\nBased on our conversation, I see you might be experiencing {primary_problem.get('category', 'issues')}. Would you like to take a structured assessment to help understand your situation better?"
                    
                    full_response += assessment_suggestion
                    
                    # Send the assessment suggestion as a separate chunk
                    yield json.dumps({
                        "type": "chunk",
                        "content": assessment_suggestion,
                        "is_assessment_suggestion": True,
                        "suggested_category": primary_problem.get('category', ''),
                        "sub_category_id": primary_problem.get('sub_category_id', ''),
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Translate response back to user's language if needed
                if detected_language == Language.INDONESIAN and confidence > 0.3:
                    # Check if response needs translation (simple heuristic)
                    response_language, response_confidence = await language_service.detect_language(full_response)
                    if response_language == Language.ENGLISH and response_confidence > 0.3:
                        translated_response = await translation_service.translate_english_to_indonesian(full_response)
                        logger.info(f"Translated streaming response back to Indonesian")
                        # Send translated response as final chunk
                        yield json.dumps({
                            "type": "translation",
                            "content": translated_response,
                            "original_content": full_response,
                            "timestamp": datetime.now().isoformat()
                        })
                        full_response = translated_response

                # Store conversation after completion
                self._store_conversation(client_id, message, full_response, sentiment_analysis)

                # Send completion signal
                yield json.dumps({
                    "type": "complete",
                    "sentiment": sentiment_analysis,
                    "is_crisis": False,
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            logger.error(f"Error processing streaming message: {str(e)}")
            
            # Provide error message in appropriate language
            try:
                # Try to detect language for error message
                detected_language, _ = await language_service.detect_language(message)
                if detected_language == Language.ENGLISH:
                    error_message = "Sorry, a technical error occurred. Please try again."
                else:
                    error_message = "Maaf, terjadi kesalahan teknis. Silakan coba lagi."
            except:
                # Fallback to Indonesian if language detection fails
                error_message = "Maaf, terjadi kesalahan teknis. Silakan coba lagi."
            
            yield json.dumps({
                "type": "error",
                "content": error_message,
                "timestamp": datetime.now().isoformat()
            })

    def _prepare_conversation_context(
        self,
        client_id: str,
        current_message: str,
        session_data: Optional[Dict] = None,
        semantic_context: Optional[List[Dict]] = None,
        problem_category: Optional[str] = None,
        assessment_progress: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Prepare conversation context for AI
        """
        messages = []

        # Add session context if available
        if session_data:
            context = f"User context: {session_data.get('user_context', '')}"
            if session_data.get('selected_problem'):
                context += f" Selected problem: {session_data['selected_problem']}"
            messages.append({"role": "system", "content": context})

        # Add semantic context if available
        if semantic_context:
            context_parts = []
            for item in semantic_context:
                if isinstance(item, dict) and 'payload' in item:
                    context_parts.append(str(item['payload']))
            if context_parts:
                semantic_context_str = "Semantic context: " + " | ".join(context_parts)
                messages.append({"role": "system", "content": semantic_context_str})

        # Add problem category if available
        if problem_category:
            messages.append({"role": "system", "content": f"Problem category: {problem_category}"})

        # Add assessment progress if available
        if assessment_progress:
            progress_info = f"Assessment progress: {assessment_progress}"
            messages.append({"role": "system", "content": progress_info})

        # Add conversation history (last 10 messages to avoid context overflow)
        history = self.conversation_history.get(client_id, [])[-10:]
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": current_message
        })

        return messages

    def _store_conversation(
        self,
        client_id: str,
        user_message: str,
        ai_response: str,
        sentiment_analysis: Dict
    ):
        """
        Store conversation in memory
        """
        conversation = self.conversation_history.get(client_id, [])

        # Add user message
        conversation.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat(),
            "sentiment": sentiment_analysis
        })

        # Add AI response
        conversation.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last 50 messages to prevent memory overflow
        if len(conversation) > 50:
            conversation = conversation[-50:]

        self.conversation_history[client_id] = conversation

    async def _generate_crisis_response(self, message: str) -> str:
        """
        Generate crisis response with emergency information in appropriate language
        """
        # Detect language of the crisis message
        try:
            detected_language, confidence = await language_service.detect_language(message)
        except:
            # Fallback to Indonesian if detection fails
            detected_language = Language.INDONESIAN
            confidence = 1.0
        
        if detected_language == Language.ENGLISH and confidence > 0.3:
            crisis_response = f"""I care deeply about your safety. The feelings you're experiencing right now are very heavy, but you are not alone. It was right for you to share this with me.

**If you feel in immediate danger, please contact:**
• Emergency: {settings.EMERGENCY_NUMBER}
• Crisis Hotline: {settings.CRISIS_HOTLINE}

**Meanwhile, try to focus on your breathing:**
1. Breathe in slowly for 4 seconds
2. Hold for 4 seconds
3. Breathe out for 4 seconds
4. Repeat until you feel a little calmer

Would you like to tell me more about what's making you feel this way? I'm here to listen."""
        else:
            crisis_response = f"""Saya sangat peduli dengan keselamatan Anda. Perasaan yang Anda alami sekarang sangat berat, tapi Anda tidak sendirian. Sudah tepat Anda berbagi dengan saya.

**Jika Anda merasa dalam bahaya segera, tolong hubungi:**
• Emergency: {settings.EMERGENCY_NUMBER}
• Crisis Hotline: {settings.CRISIS_HOTLINE}

**Sementara itu, coba fokus pada pernapasan Anda:**
1. Tarik napas perlahan selama 4 detik
2. Tahan 4 detik
3. Hembuskan 4 detik
4. Ulangi sampai Anda merasa sedikit lebih tenang

Apakah Anda mau cerita lebih lanjut tentang apa yang membuat Anda merasa seperti ini? Saya di sini untuk mendengarkan."""

        return crisis_response

    def get_conversation_history(self, client_id: str) -> List[Dict]:
        """
        Get conversation history for a client
        """
        return self.conversation_history.get(client_id, [])

    def clear_conversation_history(self, client_id: str):
        """
        Clear conversation history for a client
        """
        if client_id in self.conversation_history:
            del self.conversation_history[client_id]

    async def start_assessment(self, client_id: str, problem_category: str, sub_category_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a structured assessment flow based on problem category
        """
        return await assessment_service.start_assessment(client_id, problem_category, sub_category_id)
    
    async def process_assessment_response(self, client_id: str, response: str, question_id: str) -> Dict[str, Any]:
        """
        Process user response to assessment question
        """
        return await assessment_service.process_assessment_response(client_id, response, question_id)
    
    def get_assessment_status(self, client_id: str) -> Optional[Dict]:
        """
        Get current assessment session status
        """
        return assessment_service.get_session_status(client_id)
    
    def cancel_assessment(self, client_id: str) -> bool:
        """
        Cancel active assessment session
        """
        return assessment_service.cancel_assessment(client_id)

    async def check_model_status(self) -> Dict[str, Any]:
        """
        Check Ollama model status
        """
        try:
            is_available = await self.ollama_service.check_model_availability()

            return {
                "model": settings.OLLAMA_MODEL,
                "available": is_available,
                "base_url": settings.OLLAMA_BASE_URL,
                "temperature": settings.OLLAMA_TEMPERATURE,
                "max_tokens": settings.OLLAMA_MAX_TOKENS
            }

        except Exception as e:
            logger.error(f"Error checking model status: {str(e)}")
            return {
                "model": settings.OLLAMA_MODEL,
                "available": False,
                "error": str(e)
            }


