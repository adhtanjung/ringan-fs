import json
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.services.ollama_service import OllamaService
from app.services.semantic_search_service import semantic_search_service
from app.services.assessment_service import assessment_service
from app.services.conversation_flow_service import conversation_flow_service
from app.services.dynamic_response_service import dynamic_response_service
from app.services.language_service import language_service, Language
from app.services.translation_service import translation_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.ollama_service = OllamaService()
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.assessment_state: Dict[str, Dict] = {}  # Track assessment progress per client

    async def _generate_semantic_context(self, message: str, translated_message: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate semantic context from user message using vector search
        Uses translated message for better English vector database compatibility
        """
        try:
            # Semantic search service should already be initialized

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

    async def _get_next_assessment_question(self, client_id: str, user_message: str, detected_language: Language) -> Optional[Dict[str, Any]]:
        """
        Implement dialog-based assessment flow as per PRD requirements.
        Retrieves one question at a time from vector database based on user's response.
        """
        try:
            # Semantic search service should already be initialized

            # Get or initialize assessment state for this client
            if client_id not in self.assessment_state:
                self.assessment_state[client_id] = {
                    "current_problem_category": None,
                    "sub_category_id": None,
                    "questions_asked": [],
                    "assessment_complete": False,
                    "current_cluster": None
                }

            state = self.assessment_state[client_id]

            # If this is the first interaction, identify the problem category
            if not state["current_problem_category"]:
                # Search for relevant problems to identify category
                problems_search = await semantic_search_service.search_problems(
                    query=user_message,
                    limit=1,
                    score_threshold=0.5
                )

                if problems_search.success and problems_search.results:
                    problem_result = problems_search.results[0]
                    state["current_problem_category"] = problem_result.payload.get("problem_name")
                    state["sub_category_id"] = problem_result.payload.get("sub_category_id")
                    logger.info(f"Identified problem category: {state['current_problem_category']}")

            # Search for assessment questions based on the identified problem
            if state["sub_category_id"]:
                assessment_search = await semantic_search_service.search_assessment_questions(
                    problem_description=user_message,
                    sub_category_id=state["sub_category_id"],
                    limit=5,
                    score_threshold=0.4
                )

                if assessment_search.success and assessment_search.results:
                    # Filter out already asked questions
                    available_questions = [
                        result for result in assessment_search.results
                        if result.id not in state["questions_asked"]
                    ]

                    if available_questions:
                        # Select the most relevant question
                        next_question = available_questions[0]
                        state["questions_asked"].append(next_question.id)

                        question_text = next_question.payload.get("question_text", "")
                        response_type = next_question.payload.get("response_type", "text")

                        # Translate question if user is using Indonesian
                        if detected_language == Language.INDONESIAN:
                            question_text = await translation_service.translate_english_to_indonesian(question_text)

                        return {
                            "question_id": next_question.id,
                            "question_text": question_text,
                            "response_type": response_type,
                            "problem_category": state["current_problem_category"],
                            "is_assessment_question": True
                        }
                    else:
                        # No more questions available, assessment complete
                        state["assessment_complete"] = True
                        return None

            return None

        except Exception as e:
            logger.error(f"Error getting next assessment question: {str(e)}")
            return None

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
            print(f"🔍 Problem context analysis - context_text: '{context_text}'")

            # Try both original and English translation for better results
            problem_search = await semantic_search_service.search_problems(
                query=context_text,
                limit=5,
                score_threshold=0.3  # Lower threshold for better matching
            )

            # If no results found, try with English keywords
            if not problem_search.success or not problem_search.results:
                print(f"🔍 Problem context analysis - no results, trying English keywords")
                english_keywords = self._extract_english_keywords(context_text)
                if english_keywords:
                    problem_search = await semantic_search_service.search_problems(
                        query=english_keywords,
                        limit=5,
                        score_threshold=0.3
                    )
                    print(f"🔍 Problem context analysis - English search results: {len(problem_search.results) if problem_search.results else 0}")

            print(f"🔍 Problem context analysis - problem_search.success: {problem_search.success}")
            print(f"🔍 Problem context analysis - problem_search.results count: {len(problem_search.results) if problem_search.results else 0}")

            detected_problems = []
            confidence_scores = []

            if problem_search.success and problem_search.results:
                for result in problem_search.results:
                    payload = result.payload
                    # Use domain as fallback if category is empty
                    category = payload.get('category', '') or payload.get('domain', '')
                    print(f"🔍 Problem context analysis - found problem: {category} (score: {result.score})")
                    detected_problems.append({
                        "category": category,
                        "sub_category": payload.get('sub_category', ''),
                        "sub_category_id": payload.get('sub_category_id', ''),
                        "domain": payload.get('domain', ''),
                        "confidence": result.score,
                        "description": payload.get('text', '')
                    })
                    confidence_scores.append(result.score)

            # Determine if we have high confidence in problem identification
            max_confidence = max(confidence_scores) if confidence_scores else 0
            # Lower the threshold to 0.5 to be more inclusive for assessment suggestions
            should_suggest_assessment = max_confidence > 0.5 and len(detected_problems) > 0

            print(f"🔍 Problem context analysis - max_confidence: {max_confidence}")
            print(f"🔍 Problem context analysis - detected_problems count: {len(detected_problems)}")
            print(f"🔍 Problem context analysis - should_suggest_assessment: {should_suggest_assessment}")

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

    def _extract_english_keywords(self, text: str) -> str:
        """
        Extract English keywords from Indonesian text for better semantic search
        """
        # Simple Indonesian to English keyword mapping
        keyword_map = {
            'cemas': 'anxiety anxious',
            'stres': 'stress stressed',
            'depresi': 'depression depressed',
            'khawatir': 'worry worried anxious',
            'takut': 'fear afraid anxious',
            'panik': 'panic anxious',
            'gelisah': 'restless anxious',
            'tertekan': 'stressed depressed',
            'kesulitan': 'difficulty struggling',
            'masalah': 'problem issue',
            'bantuan': 'help support',
            'merasa': 'feeling',
            'saya': 'I',
            'aku': 'I',
            'sangat': 'very',
            'benar': 'really',
            'sekali': 'very',
            'sekali': 'very'
        }

        text_lower = text.lower()
        english_keywords = []

        for indo_word, english_words in keyword_map.items():
            if indo_word in text_lower:
                english_keywords.extend(english_words.split())

        return ' '.join(english_keywords) if english_keywords else ''

    async def _should_transition_to_assessment(self, context_analysis: Dict, conversation_history: List[Dict]) -> bool:
        """
        Determine if the conversation should transition to structured assessment
        """
        try:
            # Check confidence level
            max_confidence = context_analysis.get('max_confidence', 0)
            print(f"🔍 Assessment transition check - max_confidence: {max_confidence}")

            if max_confidence < 0.5:
                print(f"🔍 Assessment transition - confidence too low: {max_confidence}")
                return False

            # Check if user has been discussing problems for multiple messages
            history_length = len(conversation_history) if conversation_history else 0
            print(f"🔍 Assessment transition - conversation_history length: {history_length}")

            if history_length >= 6:  # At least 3 exchanges
                print(f"🔍 Assessment transition - enough conversation history: {history_length}")
                return True

            # Check for explicit distress indicators in recent messages
            recent_messages = conversation_history[-3:] if conversation_history else []
            distress_keywords = ['help', 'stressed', 'anxious', 'depressed', 'overwhelmed', 'struggling', 'difficult', 'feeling', 'trouble', 'problem', 'issue']

            print(f"🔍 Assessment transition - recent_messages: {recent_messages}")

            for msg in recent_messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '').lower()
                    print(f"🔍 Assessment transition - checking message: '{content}'")
                    if any(keyword in content for keyword in distress_keywords):
                        print(f"🔍 Assessment transition - distress keyword found in: '{content}'")
                        return True

            # If we have good confidence (>= 0.5) and detected problems, suggest assessment even for single messages
            if max_confidence >= 0.5 and context_analysis.get('detected_problems'):
                print(f"🔍 Assessment transition - good confidence single message: {max_confidence}")
                return True

            print(f"🔍 Assessment transition - no conditions met, returning False")
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

            # Step 5: Implement dialog-based assessment flow as per PRD
            if is_crisis:
                ai_response = await self._generate_crisis_response(message)
                next_question = None
            else:
                # Get next assessment question from vector database
                next_question = await self._get_next_assessment_question(client_id, message, detected_language)

                if next_question:
                    # Use the question from vector database as the AI response
                    ai_response = next_question["question_text"]
                    logger.info(f"Using assessment question: {next_question['question_id']}")
                else:
                    # Fallback to AI-generated response if no questions available
                    ai_response = await self.ollama_service.generate_response(conversation_messages)

            # Get current conversation history
            current_history = self.conversation_history.get(client_id, [])

            # Analyze problem context using AI-powered analysis
            context_analysis = await self._analyze_problem_context(message, current_history)

            # Assessment state info
            assessment_state = self.assessment_state.get(client_id, {})
            should_transition = not assessment_state.get("assessment_complete", False)

            # Use detected problem category if not explicitly provided
            if not problem_category and context_analysis.get('primary_category'):
                problem_category = context_analysis.get('primary_category')

            # Add context analysis to conversation for AI awareness (only if not using assessment questions)
            if not next_question and context_analysis.get('detected_problems'):
                context_info = f"Detected potential concerns: {', '.join([p.get('category', '') for p in context_analysis['detected_problems'][:2]])}"
                conversation_messages.insert(-1, {"role": "system", "content": context_info})

            # Step 6: Handle response language based on user preference
            # Check user's preferred language from session data
            preferred_language = session_data.get('preferredLanguage', 'en') if session_data else 'en'
            logger.info(f"User's preferred language: {preferred_language}")

            # Only translate to Indonesian if user's preferred language is Indonesian
            if preferred_language == 'id' and detected_language == Language.INDONESIAN and confidence > 0.7:
                # Check if the user's message contains any English words that suggest they prefer English
                english_indicators = ['english', 'in english', 'speak english', 'respond in english']
                message_lower = message.lower()
                wants_english = any(indicator in message_lower for indicator in english_indicators)

                if not wants_english:
                    # If the AI response is in English, translate it to Indonesian
                    response_language, response_confidence = await language_service.detect_language(ai_response)
                    if response_language == Language.ENGLISH and response_confidence > 0.3:
                        ai_response = await translation_service.translate_english_to_indonesian(ai_response)
                        logger.info(f"Translated response back to Indonesian (confidence: {confidence:.2f})")
                else:
                    logger.info(f"User prefers English response despite Indonesian input")
            else:
                logger.info(f"Keeping response in English based on user preference: {preferred_language}")

            # Store conversation
            self._store_conversation(client_id, message, ai_response, sentiment_analysis)

            # Prepare response with enhanced context and assessment information
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
                "detected_problem_category": problem_category,
                "assessment_question": next_question,
                "assessment_state": assessment_state,
                "is_dialog_based_assessment": next_question is not None
            }

            return response_data

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")

            # Generate dynamic error message
            try:
                # Try to detect language for error message
                detected_language, _ = await language_service.detect_language(message)

                error_prompt = f"""
Generate a brief, empathetic error message for a technical failure.
The message should:
- Apologize for the technical difficulty
- Suggest they try again
- Include emergency contact information (112)
- Maintain a supportive, caring tone

Language: {'English' if detected_language == Language.ENGLISH else 'Indonesian'}
Tone: Apologetic, supportive, helpful
"""

                from app.services.dynamic_response_service import DynamicResponseService
                dynamic_service = DynamicResponseService()
                error_message = await dynamic_service.generate_simple_response(
                    error_prompt,
                    user_language=detected_language,
                    context_type="general"
                )
            except:
                # Fallback to basic message
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
                print(f"🔍 Assessment suggestion check - should_transition: {should_transition}")
                print(f"🔍 Assessment suggestion check - context_analysis.get('should_suggest_assessment'): {context_analysis.get('should_suggest_assessment')}")
                print(f"🔍 Assessment suggestion check - context_analysis: {context_analysis}")

                if should_transition and context_analysis.get('should_suggest_assessment'):
                    print(f"🔍 Assessment suggestion - conditions met, generating suggestion")
                    primary_problem = context_analysis.get('detected_problems', [{}])[0]

                    # Generate dynamic assessment suggestion
                    assessment_prompt = f"Generate a natural, empathetic suggestion for a structured assessment based on the detected problem category: {primary_problem.get('category', 'general concerns')}. Keep it conversational and supportive."

                    assessment_response_data = await dynamic_response_service.generate_therapeutic_response(
                        user_message=assessment_prompt,
                        conversation_history=current_history[-3:],
                        context_type="assessment",
                        user_language=detected_language,
                        session_data=session_data
                    )

                    assessment_suggestion = f"\n\n{assessment_response_data.get('response', '')}"
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

                # Handle response language based on user preference
                # Check user's preferred language from session data
                preferred_language = session_data.get('preferredLanguage', 'en') if session_data else 'en'
                logger.info(f"User's preferred language in streaming: {preferred_language}")

                # Only translate to Indonesian if user's preferred language is Indonesian
                if preferred_language == 'id' and detected_language == Language.INDONESIAN and confidence > 0.7:
                    # Check if the user's message contains any English words that suggest they prefer English
                    english_indicators = ['english', 'in english', 'speak english', 'respond in english']
                    message_lower = message.lower()
                    wants_english = any(indicator in message_lower for indicator in english_indicators)

                    if not wants_english:
                        # Check if response needs translation (simple heuristic)
                        response_language, response_confidence = await language_service.detect_language(full_response)
                        if response_language == Language.ENGLISH and response_confidence > 0.3:
                            translated_response = await translation_service.translate_english_to_indonesian(full_response)
                            logger.info(f"Translated streaming response back to Indonesian (confidence: {confidence:.2f})")
                            # Send translated response as final chunk
                            yield json.dumps({
                                "type": "translation",
                                "content": translated_response,
                                "original_content": full_response,
                                "timestamp": datetime.now().isoformat()
                            })
                            full_response = translated_response
                    else:
                        logger.info(f"User prefers English response despite Indonesian input in streaming")
                else:
                    logger.info(f"Keeping streaming response in English based on user preference: {preferred_language}")

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

            # Generate dynamic error message
            try:
                # Try to detect language for error message
                detected_language, _ = await language_service.detect_language(message)

                error_prompt = f"""
Generate a brief, empathetic error message for a streaming message processing failure.
The message should:
- Apologize for the technical difficulty
- Suggest they try again
- Maintain a supportive, understanding tone
- Be concise for streaming context

Language: {'English' if detected_language == Language.ENGLISH else 'Indonesian'}
Tone: Apologetic, supportive, brief
"""

                from app.services.dynamic_response_service import DynamicResponseService
                dynamic_service = DynamicResponseService()
                error_message = await dynamic_service.generate_simple_response(
                    error_prompt,
                    user_language=detected_language,
                    context_type="general"
                )
            except:
                # Fallback to basic message
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
            # Also reset conversation flow if exists
            conversation_flow_service.reset_flow(client_id)

    def get_flow_status(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation flow status for a client
        """
        return conversation_flow_service.get_flow_status(client_id)

    def reset_flow(self, client_id: str) -> bool:
        """
        Reset conversation flow for a client
        """
        return conversation_flow_service.reset_flow(client_id)

    def get_all_active_flows(self) -> List[str]:
        """
        Get all active conversation flows
        """
        return conversation_flow_service.get_all_active_flows()

    async def process_message_with_flow(self, message: str, client_id: str,
                                      session_data: Optional[Dict] = None,
                                      use_flow: bool = True) -> Dict[str, Any]:
        """
        Process message with conversation flow integration
        """
        try:
            if use_flow:
                # Check if this is a new conversation or continuing flow
                flow_status = conversation_flow_service.get_flow_status(client_id)

                if flow_status is None:
                    # Start new conversation flow
                    flow_response = await conversation_flow_service.start_conversation_flow(client_id, message)
                else:
                    # Continue existing flow
                    flow_response = await conversation_flow_service.process_flow_message(client_id, message)

                # Store conversation in history
                self._store_conversation(client_id, message, flow_response.get("message", ""), {})

                return flow_response
            else:
                # Use original process_message method
                return await self.process_message(message, client_id, session_data)

        except Exception as e:
            logger.error(f"Error processing message with flow: {str(e)}")
            return await self.process_message(message, client_id, session_data)

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


