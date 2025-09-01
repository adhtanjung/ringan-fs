import json
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from app.services.semantic_search_service import semantic_search_service
from app.services.assessment_service import assessment_service
from app.services.ollama_service import OllamaService
from app.services.language_service import language_service, Language
from app.services.dynamic_response_service import DynamicResponseService
import logging

logger = logging.getLogger(__name__)

class ConversationStage(Enum):
    PROBLEM_IDENTIFICATION = "1.1 Problem Identification"
    SELF_ASSESSMENT = "1.2 Self-Assessment"
    SUGGESTIONS = "1.3 Suggestions"
    FEEDBACK = "1.4 Feedback"
    NEXT_ACTION = "1.5 Next Action After Feedback"

class ConversationFlowService:
    """
    Orchestrates the complete interactive conversation flow:
    1.1 Problem Identification -> 1.2 Self-Assessment -> 1.3 Suggestions -> 1.4 Feedback -> 1.5 Next Action
    """
    
    def __init__(self):
        self.ollama_service = OllamaService()
        self.dynamic_response_service = DynamicResponseService()
        self.active_flows: Dict[str, Dict] = {}  # Track conversation flows per client
    
    def _determine_user_language(self, session_data: Optional[Dict], detected_language: Language) -> Language:
        """
        Determine the correct user language by prioritizing session preferences over detection
        """
        if session_data and 'preferredLanguage' in session_data:
            preferred = session_data['preferredLanguage']
            if preferred == 'id' or preferred == 'indonesian':
                return Language.INDONESIAN
            elif preferred == 'en' or preferred == 'english':
                return Language.ENGLISH
        
        # Fallback to detected language
        return detected_language
        
    async def start_conversation_flow(self, client_id: str, initial_message: str, session_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Start a new conversation flow with problem identification
        """
        try:
            # Initialize conversation flow state
            flow_state = {
                "client_id": client_id,
                "current_stage": ConversationStage.PROBLEM_IDENTIFICATION,
                "started_at": datetime.now().isoformat(),
                "conversation_history": [],
                "identified_problems": [],
                "assessment_data": {},
                "suggestions_provided": [],
                "feedback_collected": [],
                "next_actions": [],
                "session_data": session_data or {},
                "stage_progress": {
                    ConversationStage.PROBLEM_IDENTIFICATION.value: {"status": "in_progress", "data": {}},
                    ConversationStage.SELF_ASSESSMENT.value: {"status": "pending", "data": {}},
                    ConversationStage.SUGGESTIONS.value: {"status": "pending", "data": {}},
                    ConversationStage.FEEDBACK.value: {"status": "pending", "data": {}},
                    ConversationStage.NEXT_ACTION.value: {"status": "pending", "data": {}}
                }
            }
            
            self.active_flows[client_id] = flow_state
            
            # Process initial message for problem identification
            return await self._process_problem_identification(client_id, initial_message)
            
        except Exception as e:
            logger.error(f"Error starting conversation flow: {str(e)}")
            
            # Determine user language for error message
            try:
                detected_language, _ = await language_service.detect_language(initial_message)
                user_language = self._determine_user_language(session_data, detected_language)
            except:
                user_language = Language.INDONESIAN  # Default fallback
            
            # Generate dynamic error message
            error_prompt = f"""
Generate a brief, empathetic error message for when the conversation system fails to start.
The message should:
- Apologize for the technical issue
- Encourage the user to try again
- Maintain a supportive tone
- Be concise and reassuring

Language: {'Indonesian' if user_language == Language.INDONESIAN else 'English'}
Tone: Apologetic, supportive, professional
"""
            
            try:
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=user_language,
                    context_type="general"
                )
            except:
                if user_language == Language.INDONESIAN:
                    error_message = "Maaf, terjadi kesalahan saat memulai percakapan. Silakan coba lagi."
                else:
                    error_message = "Sorry, there was an error starting the conversation. Please try again."
            
            return {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.PROBLEM_IDENTIFICATION.value
            }
    
    async def process_flow_message(self, client_id: str, message: str, session_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user message based on current conversation stage
        """
        try:
            if client_id not in self.active_flows:
                # Start new flow if none exists
                return await self.start_conversation_flow(client_id, message, session_data)
            
            flow_state = self.active_flows[client_id]
            # Update session data if provided
            if session_data:
                flow_state["session_data"].update(session_data)
            current_stage = flow_state["current_stage"]
            
            # Add message to conversation history
            flow_state["conversation_history"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "stage": current_stage.value
            })
            
            # Route to appropriate stage handler
            if current_stage == ConversationStage.PROBLEM_IDENTIFICATION:
                return await self._process_problem_identification(client_id, message)
            elif current_stage == ConversationStage.SELF_ASSESSMENT:
                return await self._process_self_assessment(client_id, message)
            elif current_stage == ConversationStage.SUGGESTIONS:
                return await self._process_suggestions(client_id, message)
            elif current_stage == ConversationStage.FEEDBACK:
                return await self._process_feedback(client_id, message)
            elif current_stage == ConversationStage.NEXT_ACTION:
                return await self._process_next_action(client_id, message)
            else:
                return {
                    "type": "error",
                    "message": "Stage percakapan tidak dikenali.",
                    "stage": current_stage.value
                }
                
        except Exception as e:
            logger.error(f"Error processing flow message: {str(e)}")
            return {
                "type": "error",
                "message": "Maaf, terjadi kesalahan saat memproses pesan Anda.",
                "stage": self.active_flows.get(client_id, {}).get("current_stage", {}).value if client_id in self.active_flows else "unknown"
            }
    
    async def start_conversation_flow_streaming(self, client_id: str, initial_message: str, session_data: Optional[Dict] = None):
        """
        Start a new conversation flow with streaming response
        """
        try:
            # Initialize conversation flow state
            flow_state = {
                "client_id": client_id,
                "current_stage": ConversationStage.PROBLEM_IDENTIFICATION,
                "started_at": datetime.now().isoformat(),
                "conversation_history": [],
                "identified_problems": [],
                "assessment_data": {},
                "suggestions_provided": [],
                "feedback_collected": [],
                "next_actions": [],
                "session_data": session_data or {},
                "stage_progress": {
                    ConversationStage.PROBLEM_IDENTIFICATION.value: {"status": "in_progress", "data": {}},
                    ConversationStage.SELF_ASSESSMENT.value: {"status": "pending", "data": {}},
                    ConversationStage.SUGGESTIONS.value: {"status": "pending", "data": {}},
                    ConversationStage.FEEDBACK.value: {"status": "pending", "data": {}},
                    ConversationStage.NEXT_ACTION.value: {"status": "pending", "data": {}}
                }
            }
            
            self.active_flows[client_id] = flow_state
            
            # Process initial message for problem identification with streaming
            async for chunk in self._process_problem_identification_streaming(client_id, initial_message):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error starting conversation flow: {str(e)}")
            error_response = {
                "type": "error",
                "message": "Sorry, an error occurred while starting the conversation. Please try again.",
                "stage": ConversationStage.PROBLEM_IDENTIFICATION.value
            }
            yield json.dumps(error_response)
    
    async def process_flow_message_streaming(self, client_id: str, message: str, session_data: Optional[Dict] = None):
        """
        Process user message based on current conversation stage with streaming
        """
        try:
            if client_id not in self.active_flows:
                # Start new flow if none exists
                async for chunk in self.start_conversation_flow_streaming(client_id, message, session_data):
                    yield chunk
                return
            
            flow_state = self.active_flows[client_id]
            # Update session data if provided
            if session_data:
                flow_state["session_data"].update(session_data)
            current_stage = flow_state["current_stage"]
            
            # Add message to conversation history
            flow_state["conversation_history"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "stage": current_stage.value
            })
            
            # Route to appropriate stage handler with streaming
            if current_stage == ConversationStage.PROBLEM_IDENTIFICATION:
                async for chunk in self._process_problem_identification_streaming(client_id, message):
                    yield chunk
            elif current_stage == ConversationStage.SELF_ASSESSMENT:
                async for chunk in self._process_self_assessment_streaming(client_id, message):
                    yield chunk
            elif current_stage == ConversationStage.SUGGESTIONS:
                async for chunk in self._process_suggestions_streaming(client_id, message):
                    yield chunk
            elif current_stage == ConversationStage.FEEDBACK:
                async for chunk in self._process_feedback_streaming(client_id, message):
                    yield chunk
            elif current_stage == ConversationStage.NEXT_ACTION:
                async for chunk in self._process_next_action_streaming(client_id, message):
                    yield chunk
            else:
                error_response = {
                    "type": "error",
                    "message": "Conversation stage not recognized.",
                    "stage": current_stage.value
                }
                yield json.dumps(error_response)
                
        except Exception as e:
            logger.error(f"Error processing flow message: {str(e)}")
            error_response = {
                "type": "error",
                "message": "Sorry, an error occurred while processing your message.",
                "stage": self.active_flows.get(client_id, {}).get("current_stage", {}).value if client_id in self.active_flows else "unknown"
            }
            yield json.dumps(error_response)

    async def process_flow_message(self, client_id: str, message: str, session_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user message based on current conversation stage
        """
        try:
            if client_id not in self.active_flows:
                # Start new flow if none exists
                return await self.start_conversation_flow(client_id, message, session_data)
            
            flow_state = self.active_flows[client_id]
            # Update session data if provided
            if session_data:
                flow_state["session_data"].update(session_data)
            current_stage = flow_state["current_stage"]
            
            # Add message to conversation history
            flow_state["conversation_history"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "stage": current_stage.value
            })
            
            # Route to appropriate stage handler
            if current_stage == ConversationStage.PROBLEM_IDENTIFICATION:
                return await self._process_problem_identification(client_id, message)
            elif current_stage == ConversationStage.SELF_ASSESSMENT:
                return await self._process_self_assessment(client_id, message)
            elif current_stage == ConversationStage.SUGGESTIONS:
                return await self._process_suggestions(client_id, message)
            elif current_stage == ConversationStage.FEEDBACK:
                return await self._process_feedback(client_id, message)
            elif current_stage == ConversationStage.NEXT_ACTION:
                return await self._process_next_action(client_id, message)
            else:
                return {
                    "type": "error",
                    "message": "Stage percakapan tidak dikenali.",
                    "stage": current_stage.value
                }
                
        except Exception as e:
            logger.error(f"Error processing flow message: {str(e)}")
            return {
                "type": "error",
                "message": "Maaf, terjadi kesalahan saat memproses pesan Anda.",
                "stage": self.active_flows.get(client_id, {}).get("current_stage", {}).value if client_id in self.active_flows else "unknown"
            }
    
    async def _process_problem_identification(self, client_id: str, message: str) -> Dict[str, Any]:
        """
        Stage 1.1: Identify user's problems using semantic search
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Detect user's language
            detected_language, confidence = await language_service.detect_language(message)
            logger.info(f"Detected language: {detected_language.value} (confidence: {confidence:.2f})")
            
            # Determine final user language (prioritize session preferences)
            session_data = flow_state.get("session_data")
            user_language = self._determine_user_language(session_data, detected_language)
            logger.info(f"Final user language: {user_language.value}")
            
            # Search for relevant problems in vector database
            problems_search = await semantic_search_service.search_problems(
                query=message,
                limit=3,
                score_threshold=0.15  # Adjusted threshold for better cross-language matching
            )
            
            logger.info(f"Semantic search results for '{message}': {problems_search}")
            
            identified_problems = []
            if problems_search.success and problems_search.results:
                for result in problems_search.results:
                    payload = result.payload
                    identified_problems.append({
                        "problem_id": payload.get("problem_id", ""),
                        "sub_category_id": payload.get("sub_category_id", ""),
                        "category": payload.get("category", ""),
                        "problem_text": payload.get("text", ""),
                        "domain": payload.get("domain", ""),
                        "score": result.score,
                        "suggestions_available": True
                    })
            
            logger.info(f"Identified problems: {identified_problems}")
            
            # Store identified problems
            flow_state["identified_problems"] = identified_problems
            flow_state["stage_progress"][ConversationStage.PROBLEM_IDENTIFICATION.value]["data"] = {
                "problems_found": len(identified_problems),
                "top_problem": identified_problems[0] if identified_problems else None
            }
            
            # Generate empathetic response with problem validation
            if identified_problems:
                top_problem = identified_problems[0]
                
                # Create context for AI response based on detected language
                # Generate dynamic transition prompt
                transition_prompt_generation = f"""
Generate a warm, inviting question asking if they would like to proceed with assessment questions.
The question should:
- Be supportive and non-pressuring
- Explain that assessment helps understand their situation better
- Use encouraging, professional tone
- Be concise and clear

Language: {'Indonesian' if user_language == Language.INDONESIAN else 'English'}
Tone: Warm, professional, encouraging
"""
                
                try:
                    transition_prompt = await self.dynamic_response_service.generate_simple_response(
                        transition_prompt_generation,
                        user_language=user_language,
                        context_type="assessment"
                    )
                except:
                    # Fallback to basic prompt
                    if user_language == Language.INDONESIAN:
                        transition_prompt = "Apakah Anda siap untuk melanjutkan dengan beberapa pertanyaan assessment?"
                    else:
                        transition_prompt = "Would you like to proceed with some assessment questions?"
                
                if user_language == Language.INDONESIAN:
                    context_prompt = f"""
User telah mengungkapkan masalah yang berkaitan dengan: {top_problem['category']} - {top_problem['problem_text']}

Berikan respons yang empati dan validasi masalah mereka, lalu tanyakan apakah mereka ingin melanjutkan dengan assessment untuk memahami situasi mereka lebih dalam.

Gunakan nada yang hangat, profesional, dan mendukung. Jangan langsung memberikan saran, fokus pada validasi dan transisi ke assessment.
"""
                else:
                    context_prompt = f"""
The user has expressed concerns related to: {top_problem['category']} - {top_problem['problem_text']}

Provide an empathetic response that validates their concerns, then ask if they would like to proceed with an assessment to better understand their situation.

Use a warm, professional, and supportive tone. Don't give immediate advice, focus on validation and transition to assessment.
"""
                
                ai_response = await self._generate_ai_response(
                    context_prompt, 
                    flow_state["conversation_history"], 
                    user_language, 
                    "general", 
                    flow_state.get("session_data")
                )
                
                # Check if user is ready to proceed to assessment
                response_data = {
                    "type": "problem_identified",
                    "message": ai_response,
                    "stage": ConversationStage.PROBLEM_IDENTIFICATION.value,
                    "identified_problems": identified_problems[:2],  # Show top 2 problems
                    "next_stage_available": True,
                    "transition_prompt": transition_prompt
                }
                
                # Auto-transition to assessment if user seems ready (more precise matching)
                # Include both Indonesian and English transition keywords
                basic_keywords = ['siap', 'lanjut', 'assessment', 'pertanyaan', 'okay', 'ok', 'ready', 'proceed', 'continue']
                found_keywords = [kw for kw in basic_keywords if kw in message.lower()]
                
                message_lower = message.lower()
                
                # For 'ya', ensure it's a standalone word, not part of another word like 'Saya'
                if (' ya ' in message_lower) or message_lower.strip() == 'ya' or message_lower.startswith('ya ') or message_lower.endswith(' ya'):
                    found_keywords.append('ya')
                
                # For 'yes', ensure it's a standalone word, not part of words like 'yesterday'
                if (' yes ' in message_lower) or message_lower.strip() == 'yes' or message_lower.startswith('yes ') or message_lower.endswith(' yes'):
                    found_keywords.append('yes')
                
                # For 'sure', ensure it's a standalone word and not in negative context
                # Check for word boundaries and exclude negative contexts like 'not sure', 'unsure'
                import re
                if re.search(r'\bsure\b', message_lower) and not re.search(r'\b(not|un)\s*sure\b', message_lower):
                    found_keywords.append('sure')
                
                logger.info(f"Checking transition keywords in '{message}': found {found_keywords}")
                
                if found_keywords:
                    logger.info(f"Auto-transitioning to assessment due to keywords: {found_keywords}")
                    return await self._transition_to_assessment(client_id)
                
                return response_data
            else:
                # No specific problems identified, ask for more details
                # Detect language for clarification prompt
                detected_language, _ = await language_service.detect_language(message)
                
                if detected_language == Language.INDONESIAN:
                    clarification_prompt = f"""
User: {message}

User belum memberikan informasi yang cukup spesifik tentang masalah mereka. Ajukan pertanyaan terbuka yang membantu mereka menjelaskan situasi atau perasaan mereka dengan lebih detail.

Gunakan nada yang hangat dan tidak menghakimi. Berikan contoh area yang bisa mereka ceritakan (seperti perasaan, situasi, atau tantangan yang dihadapi).
"""
                else:
                    clarification_prompt = f"""
User: {message}

The user hasn't provided enough specific information about their concerns. Ask open-ended questions that help them explain their situation or feelings in more detail.

Use a warm and non-judgmental tone. Provide examples of areas they could share about (such as feelings, situations, or challenges they're facing).
"""
                
                ai_response = await self._generate_ai_response(
                    clarification_prompt, 
                    flow_state["conversation_history"], 
                    detected_language, 
                    "general", 
                    flow_state.get("session_data")
                )
                
                return {
                    "type": "clarification_needed",
                    "message": ai_response,
                    "stage": ConversationStage.PROBLEM_IDENTIFICATION.value,
                    "next_stage_available": False
                }
                
        except Exception as e:
            logger.error(f"Error in problem identification: {str(e)}")
            # Generate dynamic error message
            error_prompt = """
Generate a brief, empathetic error message for when problem identification fails.
The message should:
- Apologize for the difficulty in understanding their concerns
- Encourage them to try rephrasing or continue
- Maintain a supportive, non-judgmental tone
- Be concise and reassuring

Language: Indonesian
Tone: Understanding, supportive, encouraging
"""
            
            try:
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=Language.INDONESIAN,
                    context_type="general"
                )
            except:
                error_message = "Maaf, terjadi kesalahan saat mengidentifikasi masalah Anda."
            
            return {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.PROBLEM_IDENTIFICATION.value
            }
    
    async def _transition_to_assessment(self, client_id: str) -> Dict[str, Any]:
        """
        Transition from problem identification to self-assessment
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Mark problem identification as complete
            flow_state["stage_progress"][ConversationStage.PROBLEM_IDENTIFICATION.value]["status"] = "completed"
            flow_state["current_stage"] = ConversationStage.SELF_ASSESSMENT
            flow_state["stage_progress"][ConversationStage.SELF_ASSESSMENT.value]["status"] = "in_progress"
            
            # Get the top identified problem for assessment
            if not flow_state["identified_problems"]:
                return {
                    "type": "error",
                    "message": "Tidak dapat memulai assessment tanpa identifikasi masalah terlebih dahulu.",
                    "stage": ConversationStage.SELF_ASSESSMENT.value
                }
            
            top_problem = flow_state["identified_problems"][0]
            
            # Determine user's preferred language
            user_language = self._determine_user_language(flow_state["session_data"], Language.ENGLISH)
            
            # Start assessment using assessment service
            logger.info(f"Starting assessment for problem: {top_problem}")
            assessment_result = await assessment_service.start_assessment(
                client_id=client_id,
                problem_category=top_problem["category"],
                sub_category_id=top_problem.get("sub_category_id"),  # Optional field
                user_language=user_language
            )
            logger.info(f"Assessment result: {assessment_result}")
            
            if assessment_result["type"] == "assessment_question":
                flow_state["assessment_data"] = assessment_result
                
                # Create language-appropriate introduction message
                if user_language == Language.INDONESIAN:
                    intro_message = "Baik, sekarang saya akan mengajukan beberapa pertanyaan untuk memahami situasi Anda lebih dalam."
                else:
                    intro_message = "Alright, now I will ask you some questions to better understand your situation."
                
                return {
                    "type": "assessment_started",
                    "message": f"{intro_message}\n\n{assessment_result['message']}",
                    "stage": ConversationStage.SELF_ASSESSMENT.value,
                    "assessment_data": assessment_result,
                    "progress": assessment_result.get("progress", {})
                }
            else:
                return assessment_result
                
        except Exception as e:
            logger.error(f"Error transitioning to assessment: {str(e)}")
            return {
                "type": "error",
                "message": "Maaf, terjadi kesalahan saat memulai assessment.",
                "stage": ConversationStage.SELF_ASSESSMENT.value
            }
    
    async def _process_self_assessment(self, client_id: str, message: str) -> Dict[str, Any]:
        """
        Stage 1.2: Process self-assessment responses
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Detect user's language
            detected_language, confidence = await language_service.detect_language(message)
            logger.info(f"Detected language: {detected_language.value} (confidence: {confidence:.2f})")
            
            # Get current assessment question ID
            current_assessment = flow_state.get("assessment_data", {})
            if not current_assessment or "question" not in current_assessment:
                error_message = "Session assessment tidak ditemukan. Memulai ulang..." if detected_language == Language.INDONESIAN else "Assessment session not found. Restarting..."
                return {
                    "type": "error",
                    "message": error_message,
                    "stage": ConversationStage.SELF_ASSESSMENT.value
                }
            
            question_id = current_assessment["question"]["question_id"]
            
            # Process assessment response
            assessment_result = await assessment_service.process_assessment_response(
                client_id=client_id,
                response=message,
                question_id=question_id
            )
            
            if assessment_result["type"] == "assessment_question":
                # Continue with next question
                flow_state["assessment_data"] = assessment_result
                
                return {
                    "type": "assessment_continue",
                    "message": assessment_result["message"],
                    "stage": ConversationStage.SELF_ASSESSMENT.value,
                    "assessment_data": assessment_result,
                    "progress": assessment_result.get("progress", {})
                }
            
            elif assessment_result["type"] == "assessment_complete":
                # Assessment completed, transition to suggestions
                flow_state["stage_progress"][ConversationStage.SELF_ASSESSMENT.value]["status"] = "completed"
                flow_state["stage_progress"][ConversationStage.SELF_ASSESSMENT.value]["data"] = assessment_result
                
                return await self._transition_to_suggestions(client_id, assessment_result)
            
            else:
                return assessment_result
                
        except Exception as e:
            logger.error(f"Error in self-assessment: {str(e)}")
            # Detect language for error message
            try:
                detected_language, _ = await language_service.detect_language(message)
                
                # Generate dynamic error message
                error_prompt = f"""
Generate a brief, empathetic error message for when assessment processing fails.
The message should:
- Apologize for the technical difficulty
- Reassure them their responses are valuable
- Encourage them to try again or continue
- Maintain a supportive tone

Language: {'Indonesian' if detected_language == Language.INDONESIAN else 'English'}
Tone: Apologetic, reassuring, supportive
"""
                
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=detected_language,
                    context_type="general"
                )
            except:
                error_message = "Maaf, terjadi kesalahan saat memproses jawaban assessment Anda."
            
            return {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.SELF_ASSESSMENT.value
            }
    
    async def _transition_to_suggestions(self, client_id: str, assessment_result: Dict) -> Dict[str, Any]:
        """
        Transition from self-assessment to suggestions
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Detect language from recent conversation
            recent_messages = [msg["content"] for msg in flow_state["conversation_history"][-3:] if msg["role"] == "user"]
            if recent_messages:
                detected_language, _ = await language_service.detect_language(" ".join(recent_messages))
            else:
                detected_language = Language.INDONESIAN
            
            # Update stage
            flow_state["current_stage"] = ConversationStage.SUGGESTIONS
            flow_state["stage_progress"][ConversationStage.SUGGESTIONS.value]["status"] = "in_progress"
            
            # Get suggestions based on assessment results
            suggestions = await self._get_therapeutic_suggestions(client_id, assessment_result)
            
            if suggestions:
                flow_state["suggestions_provided"] = suggestions
                flow_state["stage_progress"][ConversationStage.SUGGESTIONS.value]["data"] = {
                    "suggestions_count": len(suggestions),
                    "suggestions": suggestions
                }
                
                # Format suggestions message with language support
                suggestions_message = await self._format_suggestions_message(suggestions, assessment_result, detected_language)
                
                # Set next stage prompt based on language
                if detected_language == Language.INDONESIAN:
                    next_stage_prompt = "Bagaimana menurut Anda tentang saran-saran ini? Apakah ada yang terasa cocok atau relevan dengan situasi Anda?"
                else:
                    next_stage_prompt = "What do you think about these suggestions? Do any of them feel suitable or relevant to your situation?"
                
                return {
                    "type": "suggestions_provided",
                    "message": suggestions_message,
                    "stage": ConversationStage.SUGGESTIONS.value,
                    "suggestions": suggestions,
                    "assessment_summary": assessment_result.get("summary", {}),
                    "next_stage_prompt": next_stage_prompt
                }
            else:
                # Error message based on language
                if detected_language == Language.INDONESIAN:
                    error_message = "Maaf, tidak dapat menemukan saran yang sesuai saat ini."
                else:
                    error_message = "Sorry, I couldn't find suitable suggestions at this time."
                
                return {
                    "type": "error",
                    "message": error_message,
                    "stage": ConversationStage.SUGGESTIONS.value
                }
                
        except Exception as e:
            logger.error(f"Error transitioning to suggestions: {str(e)}")
            # Generate dynamic error message
            error_prompt = """
Generate a brief, empathetic error message for when suggestion preparation fails.
The message should:
- Apologize for the delay in providing suggestions
- Reassure them that help is still available
- Encourage them to continue or try again
- Maintain a hopeful, supportive tone

Language: Indonesian
Tone: Apologetic, hopeful, encouraging
"""
            
            try:
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=Language.INDONESIAN,
                    context_type="general"
                )
            except:
                error_message = "Maaf, terjadi kesalahan saat menyiapkan saran."
            
            return {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.SUGGESTIONS.value
            }
    
    async def _process_suggestions(self, client_id: str, message: str) -> Dict[str, Any]:
        """
        Stage 1.3: Process user response to suggestions
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Detect user's language
            detected_language, confidence = await language_service.detect_language(message)
            logger.info(f"Detected language: {detected_language.value} (confidence: {confidence:.2f})")
            
            # Analyze user's response to suggestions
            suggestions_feedback = await self._analyze_suggestions_feedback(message, flow_state["suggestions_provided"])
            
            # Mark suggestions stage as complete
            flow_state["stage_progress"][ConversationStage.SUGGESTIONS.value]["status"] = "completed"
            flow_state["stage_progress"][ConversationStage.SUGGESTIONS.value]["data"]["user_feedback"] = suggestions_feedback
            
            # Transition to feedback collection
            return await self._transition_to_feedback(client_id, suggestions_feedback)
            
        except Exception as e:
            logger.error(f"Error processing suggestions: {str(e)}")
            # Detect language for error message
            try:
                detected_language, _ = await language_service.detect_language(message)
                
                # Generate dynamic error message
                error_prompt = f"""
Generate a brief, empathetic error message for when processing user's response to suggestions fails.
The message should:
- Apologize for the technical difficulty
- Acknowledge their input is valuable
- Encourage them to try again or continue
- Maintain a supportive tone

Language: {'Indonesian' if detected_language == Language.INDONESIAN else 'English'}
Tone: Apologetic, understanding, supportive
"""
                
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=detected_language,
                    context_type="general"
                )
            except:
                error_message = "Maaf, terjadi kesalahan saat memproses respons Anda terhadap saran."
            
            return {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.SUGGESTIONS.value
            }
    
    async def _transition_to_feedback(self, client_id: str, suggestions_feedback: Dict) -> Dict[str, Any]:
        """
        Transition to feedback collection stage
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Detect language from recent conversation
            recent_messages = [msg["content"] for msg in flow_state["conversation_history"][-3:] if msg["role"] == "user"]
            if recent_messages:
                detected_language, _ = await language_service.detect_language(" ".join(recent_messages))
            else:
                detected_language = Language.INDONESIAN
            
            # Update stage
            flow_state["current_stage"] = ConversationStage.FEEDBACK
            flow_state["stage_progress"][ConversationStage.FEEDBACK.value]["status"] = "in_progress"
            
            # Get feedback prompts from vector database
            feedback_prompts = await self._get_feedback_prompts(client_id, suggestions_feedback)
            
            if feedback_prompts:
                feedback_message = await self._format_feedback_message(feedback_prompts, suggestions_feedback, detected_language)
                
                flow_state["stage_progress"][ConversationStage.FEEDBACK.value]["data"] = {
                    "feedback_prompts": feedback_prompts,
                    "suggestions_feedback": suggestions_feedback
                }
                
                return {
                    "type": "feedback_collection",
                    "message": feedback_message,
                    "stage": ConversationStage.FEEDBACK.value,
                    "feedback_prompts": feedback_prompts
                }
            else:
                # Generate dynamic feedback question
                feedback_prompt = f"""
User has completed the conversation flow and we need to collect feedback about their experience.

Generate a warm, empathetic message asking for feedback about:
- How they feel after the conversation
- What was helpful or not helpful
- Any additional support they might need

Language: {'Indonesian' if detected_language == Language.INDONESIAN else 'English'}
Tone: Supportive, caring, professional
"""
                
                fallback_message = await self.dynamic_response_service.generate_simple_response(
                    feedback_prompt,
                    user_language=detected_language,
                    context_type="general"
                )
                
                return {
                    "type": "feedback_collection",
                    "message": fallback_message,
                    "stage": ConversationStage.FEEDBACK.value,
                    "feedback_prompts": []
                }
                
        except Exception as e:
            logger.error(f"Error transitioning to feedback: {str(e)}")
            # Generate dynamic error message
            error_prompt = """
Generate a brief, empathetic error message for when feedback preparation fails.
The message should:
- Apologize for the technical difficulty
- Reassure them their input is valuable
- Encourage them to continue sharing their thoughts
- Maintain a supportive tone

Language: Indonesian
Tone: Apologetic, encouraging, supportive
"""
            
            try:
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=Language.INDONESIAN,
                    context_type="general"
                )
            except:
                error_message = "Maaf, terjadi kesalahan saat mempersiapkan tahap feedback."
            
            return {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.FEEDBACK.value
            }
    
    async def _process_feedback(self, client_id: str, message: str) -> Dict[str, Any]:
        """
        Stage 1.4: Process user feedback
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Store feedback
            feedback_data = {
                "feedback_text": message,
                "timestamp": datetime.now().isoformat(),
                "sentiment": await self._analyze_feedback_sentiment(message)
            }
            
            flow_state["feedback_collected"].append(feedback_data)
            flow_state["stage_progress"][ConversationStage.FEEDBACK.value]["status"] = "completed"
            flow_state["stage_progress"][ConversationStage.FEEDBACK.value]["data"]["collected_feedback"] = feedback_data
            
            # Transition to next action
            return await self._transition_to_next_action(client_id, feedback_data)
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            return {
                "type": "error",
                "message": "Maaf, terjadi kesalahan saat memproses feedback Anda.",
                "stage": ConversationStage.FEEDBACK.value
            }
    
    async def _transition_to_next_action(self, client_id: str, feedback_data: Dict) -> Dict[str, Any]:
        """
        Transition to next action determination
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Detect language from recent conversation
            recent_messages = [msg["content"] for msg in flow_state["conversation_history"][-3:] if msg["role"] == "user"]
            if recent_messages:
                detected_language, _ = await language_service.detect_language(" ".join(recent_messages))
            else:
                detected_language = Language.INDONESIAN
            
            # Update stage
            flow_state["current_stage"] = ConversationStage.NEXT_ACTION
            flow_state["stage_progress"][ConversationStage.NEXT_ACTION.value]["status"] = "in_progress"
            
            # Determine next actions based on feedback and conversation history
            next_actions = await self._determine_next_actions(client_id, feedback_data)
            
            flow_state["next_actions"] = next_actions
            flow_state["stage_progress"][ConversationStage.NEXT_ACTION.value]["data"] = {
                "recommended_actions": next_actions
            }
            
            # Format next action message with language support
            next_action_message = self._format_next_action_message(next_actions, flow_state, detected_language)
            
            return {
                "type": "next_actions_provided",
                "message": next_action_message,
                "stage": ConversationStage.NEXT_ACTION.value,
                "next_actions": next_actions,
                "conversation_complete": True,
                "flow_summary": self._generate_flow_summary(flow_state)
            }
            
        except Exception as e:
            logger.error(f"Error transitioning to next action: {str(e)}")
            # Generate dynamic error message
            error_prompt = """
Generate a brief, empathetic error message for when next action determination fails.
The message should:
- Apologize for the technical difficulty
- Reassure them the conversation was valuable
- Encourage them to continue their mental health journey
- Maintain a hopeful, supportive tone

Language: Indonesian
Tone: Apologetic, hopeful, encouraging
"""
            
            try:
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=Language.INDONESIAN,
                    context_type="general"
                )
            except:
                error_message = "Maaf, terjadi kesalahan saat menentukan langkah selanjutnya."
            
            return {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.NEXT_ACTION.value
            }
    
    async def _process_next_action(self, client_id: str, message: str) -> Dict[str, Any]:
        """
        Stage 1.5: Process user response to next actions
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Analyze user's choice or response
            action_choice = await self._analyze_action_choice(message, flow_state["next_actions"])
            
            # Mark flow as complete
            flow_state["stage_progress"][ConversationStage.NEXT_ACTION.value]["status"] = "completed"
            flow_state["completed_at"] = datetime.now().isoformat()
            
            # Generate final response
            final_message = await self._generate_final_response(action_choice, flow_state)
            
            return {
                "type": "conversation_complete",
                "message": final_message,
                "stage": ConversationStage.NEXT_ACTION.value,
                "action_choice": action_choice,
                "flow_complete": True,
                "flow_summary": self._generate_flow_summary(flow_state)
            }
            
        except Exception as e:
            logger.error(f"Error processing next action: {str(e)}")
            return {
                "type": "error",
                "message": "Maaf, terjadi kesalahan saat memproses pilihan Anda.",
                "stage": ConversationStage.NEXT_ACTION.value
            }
    
    # Helper methods
    async def _generate_ai_response(self, prompt: str, conversation_history: List[Dict], user_language: Language = Language.ENGLISH, context_type: str = "general", session_data: Optional[Dict] = None) -> str:
        """
        Generate AI response using dynamic response service with RAG integration
        """
        try:
            response_data = await dynamic_response_service.generate_therapeutic_response(
                user_message=prompt,
                conversation_history=conversation_history,
                context_type=context_type,
                user_language=user_language,
                session_data=session_data
            )
            
            return response_data.get("response", "")
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return await dynamic_response_service.generate_error_response(user_language)
    
    async def _get_therapeutic_suggestions(self, client_id: str, assessment_result: Dict) -> List[Dict]:
        """
        Get therapeutic suggestions based on assessment results
        """
        try:
            flow_state = self.active_flows[client_id]
            top_problem = flow_state["identified_problems"][0] if flow_state["identified_problems"] else None
            
            if not top_problem:
                return []
            
            # Search for suggestions
            suggestions_search = await semantic_search_service.search_therapeutic_suggestions(
                problem_description=top_problem["problem_text"],
                sub_category_id=top_problem["sub_category_id"],
                limit=3,
                score_threshold=0.3
            )
            
            suggestions = []
            if suggestions_search.success and suggestions_search.results:
                for result in suggestions_search.results:
                    payload = result.payload
                    suggestions.append({
                        "suggestion_id": payload.get("suggestion_id", ""),
                        "suggestion_text": payload.get("text", ""),
                        "category": payload.get("category", ""),
                        "sub_category_id": payload.get("sub_category_id", ""),
                        "cluster": payload.get("cluster", ""),
                        "resource_link": payload.get("resource_link", ""),
                        "domain": payload.get("domain", ""),
                        "score": result.score
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting therapeutic suggestions: {str(e)}")
            return []

    async def _generate_personalized_suggestions(self, identified_problems: List[Dict], assessment_result: Dict, user_language: Language) -> List[Dict]:
        """
        Generate personalized therapeutic suggestions based on identified problems and assessment results
        """
        try:
            if not identified_problems:
                return []
            
            top_problem = identified_problems[0]
            
            # Search for suggestions using semantic search
            suggestions_search = await semantic_search_service.search_therapeutic_suggestions(
                problem_description=top_problem["problem_text"],
                sub_category_id=top_problem.get("sub_category_id"),
                limit=3,
                score_threshold=0.3
            )
            
            suggestions = []
            if suggestions_search.success and suggestions_search.results:
                for result in suggestions_search.results:
                    payload = result.payload
                    suggestion_text = payload.get("text", "")
                    
                    # Format suggestion with title and description for streaming
                    if user_language == Language.INDONESIAN:
                        title = f"Saran {len(suggestions) + 1}"
                    else:
                        title = f"Suggestion {len(suggestions) + 1}"
                    
                    suggestions.append({
                        "suggestion_id": payload.get("suggestion_id", ""),
                        "title": title,
                        "description": suggestion_text,
                        "suggestion_text": suggestion_text,  # Keep for compatibility
                        "category": payload.get("category", ""),
                        "sub_category_id": payload.get("sub_category_id", ""),
                        "cluster": payload.get("cluster", ""),
                        "resource_link": payload.get("resource_link", ""),
                        "domain": payload.get("domain", ""),
                        "score": result.score
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating personalized suggestions: {str(e)}")
            return []

    async def _get_feedback_prompts(self, client_id: str, suggestions_feedback: Dict) -> List[Dict]:
        """
        Get feedback prompts from vector database
        """
        try:
            # Search for feedback prompts
            feedback_search = await semantic_search_service.search_feedback_prompts(
                context="post_suggestion",
                limit=2,
                score_threshold=0.3
            )
            
            prompts = []
            if feedback_search.success and feedback_search.results:
                for result in feedback_search.results:
                    payload = result.payload
                    prompts.append({
                        "prompt_id": payload.get("prompt_id", ""),
                        "prompt_text": payload.get("text", ""),
                        "context": payload.get("context", ""),
                        "domain": payload.get("domain", ""),
                        "score": result.score
                    })
            
            return prompts
            
        except Exception as e:
            logger.error(f"Error getting feedback prompts: {str(e)}")
            return []
    
    async def _determine_next_actions(self, client_id: str, feedback_data: Dict) -> List[Dict]:
        """
        Determine next actions based on conversation flow and feedback
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Search for next actions in vector database
            next_action_search = await semantic_search_service.search_next_actions(
                feedback_context=feedback_data["feedback_text"],
                limit=3,
                score_threshold=0.3
            )
            
            actions = []
            if next_action_search.success and next_action_search.results:
                for result in next_action_search.results:
                    payload = result.payload
                    actions.append({
                        "action_id": payload.get("action_id", ""),
                        "action_text": payload.get("text", ""),
                        "action_type": payload.get("action_type", ""),
                        "priority": payload.get("priority", "medium"),
                        "domain": payload.get("domain", ""),
                        "score": result.score
                    })
            
            # Add default actions if none found
            if not actions:
                actions = [
                    {
                        "action_id": "default_1",
                        "action_text": "Lanjutkan praktik self-care yang telah dibahas",
                        "action_type": "self_care",
                        "priority": "high"
                    },
                    {
                        "action_id": "default_2",
                        "action_text": "Pertimbangkan untuk berbicara dengan profesional jika diperlukan",
                        "action_type": "professional_help",
                        "priority": "medium"
                    }
                ]
            
            return actions
            
        except Exception as e:
            logger.error(f"Error determining next actions: {str(e)}")
            return []
    
    # Formatting and analysis helper methods
    async def _format_suggestions_message(self, suggestions: List[Dict], assessment_result: Dict, user_language: Language = Language.INDONESIAN) -> str:
        """
        Format suggestions into a readable message with language support
        """
        # Generate dynamic intro message for suggestions
        intro_prompt = f"""
Generate a warm, encouraging introduction for presenting therapeutic suggestions.
The message should:
- Reference that it's based on their completed assessment
- Express that these suggestions might be helpful
- Use a supportive, hopeful tone
- Be brief and lead into a numbered list

Language: {'Indonesian' if user_language == Language.INDONESIAN else 'English'}
Tone: Encouraging, supportive, professional
"""
        
        try:
            message = await self.dynamic_response_service.generate_simple_response(
                intro_prompt,
                user_language=user_language,
                context_type="general"
            )
            message += "\n\n"  # Add spacing for the list
        except:
            # Fallback to basic message
            if user_language == Language.INDONESIAN:
                message = "Berdasarkan assessment yang telah Anda lakukan, berikut adalah beberapa saran yang mungkin membantu:\n\n"
            else:
                message = "Based on the assessment you've completed, here are some suggestions that might help:\n\n"
        
        for i, suggestion in enumerate(suggestions[:3], 1):
            message += f"{i}. {suggestion['suggestion_text']}\n"
            if suggestion.get('resource_link'):
                resource_label = "📖 Resource:" if user_language == Language.INDONESIAN else "📖 Resource:"
                message += f"   {resource_label} {suggestion['resource_link']}\n"
            message += "\n"
        
        return message
    
    async def _format_feedback_message(self, feedback_prompts: List[Dict], suggestions_feedback: Dict, user_language: Language = Language.INDONESIAN) -> str:
        """
        Format feedback collection message with language support
        """
        if feedback_prompts:
            return feedback_prompts[0]["prompt_text"]
        else:
            # Generate dynamic feedback message
            feedback_prompt = f"""
User has received suggestions and we need to collect their feedback.

Generate a caring message asking:
- How they feel about the suggestions provided
- Which suggestions feel relevant or helpful
- Any concerns or questions they might have

Language: {'Indonesian' if user_language == Language.INDONESIAN else 'English'}
Tone: Warm, supportive, encouraging
"""
            
            return await self.dynamic_response_service.generate_simple_response(
                feedback_prompt,
                user_language=user_language,
                context_type="general"
            )
    
    def _format_next_action_message(self, next_actions: List[Dict], flow_state: Dict, user_language: Language = Language.INDONESIAN) -> str:
        """
        Format next action recommendations with language support
        """
        if user_language == Language.INDONESIAN:
            message = "Terima kasih telah berbagi. Berdasarkan percakapan kita, berikut adalah beberapa langkah yang bisa Anda pertimbangkan:\n\n"
            
            for i, action in enumerate(next_actions[:3], 1):
                message += f"{i}. {action['action_text']}\n"
            
            message += "\nApakah ada dari langkah-langkah ini yang ingin Anda coba atau diskusikan lebih lanjut?"
        else:
            message = "Thank you for sharing. Based on our conversation, here are some steps you might consider:\n\n"
            
            for i, action in enumerate(next_actions[:3], 1):
                message += f"{i}. {action['action_text']}\n"
            
            message += "\nIs there any of these steps you'd like to try or discuss further?"
        
        return message
    
    async def _analyze_suggestions_feedback(self, message: str, suggestions: List[Dict]) -> Dict:
        """
        Analyze user's feedback on suggestions
        """
        # Simple sentiment and relevance analysis
        positive_keywords = ['baik', 'membantu', 'cocok', 'relevan', 'setuju', 'ya', 'iya']
        negative_keywords = ['tidak', 'kurang', 'bukan', 'salah', 'tidak cocok']
        
        message_lower = message.lower()
        
        sentiment = "neutral"
        if any(keyword in message_lower for keyword in positive_keywords):
            sentiment = "positive"
        elif any(keyword in message_lower for keyword in negative_keywords):
            sentiment = "negative"
        
        return {
            "sentiment": sentiment,
            "feedback_text": message,
            "suggestions_count": len(suggestions)
        }
    
    async def _analyze_feedback_sentiment(self, message: str) -> str:
        """
        Analyze sentiment of feedback message
        """
        positive_keywords = ['baik', 'membantu', 'senang', 'terima kasih', 'lega', 'positif']
        negative_keywords = ['buruk', 'tidak membantu', 'sedih', 'kecewa', 'sulit', 'negatif']
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in positive_keywords):
            return "positive"
        elif any(keyword in message_lower for keyword in negative_keywords):
            return "negative"
        else:
            return "neutral"
    
    async def _analyze_action_choice(self, message: str, next_actions: List[Dict]) -> Dict:
        """
        Analyze user's choice of next actions
        """
        # Simple analysis of which action they're interested in
        message_lower = message.lower()
        
        chosen_actions = []
        for action in next_actions:
            action_keywords = action['action_text'].lower().split()[:3]  # First 3 words
            if any(keyword in message_lower for keyword in action_keywords):
                chosen_actions.append(action)
        
        return {
            "chosen_actions": chosen_actions,
            "user_response": message,
            "engagement_level": "high" if len(chosen_actions) > 0 else "medium"
        }
    
    async def _generate_final_response(self, action_choice: Dict, flow_state: Dict) -> str:
        """
        Generate final response for conversation completion with language support
        """
        # Detect language from recent conversation
        recent_messages = [msg["content"] for msg in flow_state["conversation_history"][-3:] if msg["role"] == "user"]
        if recent_messages:
            try:
                detected_language, _ = await language_service.detect_language(" ".join(recent_messages))
            except:
                detected_language = Language.INDONESIAN
        else:
            detected_language = Language.INDONESIAN
        
        # Generate dynamic final response
        final_prompt = f"""
User has completed the conversation flow and chosen their next actions.

Generate a warm, encouraging closing message that:
- Thanks them for their time and openness
- Acknowledges their chosen actions: {action_choice.get('chosen_actions', [])}
- Encourages them about their mental health journey
- Offers continued support
- Ends on a positive, hopeful note

Language: {'Indonesian' if detected_language == Language.INDONESIAN else 'English'}
Tone: Warm, supportive, encouraging, professional
"""
        
        base_message = await self.dynamic_response_service.generate_simple_response(
            final_prompt,
            user_language=detected_language,
            context_type="general"
        )
        
        return base_message
    
    def _generate_flow_summary(self, flow_state: Dict) -> Dict:
        """
        Generate summary of the conversation flow
        """
        return {
            "client_id": flow_state["client_id"],
            "duration": self._calculate_flow_duration(flow_state),
            "stages_completed": [stage for stage, data in flow_state["stage_progress"].items() if data["status"] == "completed"],
            "problems_identified": len(flow_state["identified_problems"]),
            "suggestions_provided": len(flow_state["suggestions_provided"]),
            "feedback_collected": len(flow_state["feedback_collected"]),
            "next_actions_count": len(flow_state["next_actions"]),
            "conversation_length": len(flow_state["conversation_history"])
        }
    
    def _calculate_flow_duration(self, flow_state: Dict) -> int:
        """
        Calculate conversation flow duration in minutes
        """
        try:
            start_time = datetime.fromisoformat(flow_state["started_at"])
            end_time = datetime.fromisoformat(flow_state.get("completed_at", datetime.now().isoformat()))
            duration = (end_time - start_time).total_seconds() / 60
            return round(duration, 2)
        except:
            return 0
    
    # Public utility methods
    def get_flow_status(self, client_id: str) -> Optional[Dict]:
        """
        Get current flow status for a client
        """
        if client_id not in self.active_flows:
            return None
        
        flow_state = self.active_flows[client_id]
        return {
            "client_id": client_id,
            "current_stage": flow_state["current_stage"].value,
            "stage_progress": flow_state["stage_progress"],
            "started_at": flow_state["started_at"],
            "conversation_length": len(flow_state["conversation_history"])
        }
    
    def reset_flow(self, client_id: str) -> bool:
        """
        Reset conversation flow for a client
        """
        if client_id in self.active_flows:
            del self.active_flows[client_id]
            return True
        return False
    
    def get_all_active_flows(self) -> List[str]:
        """
        Get list of all active flow client IDs
        """
        return list(self.active_flows.keys())
    
    async def _process_problem_identification_streaming(self, client_id: str, message: str):
        """
        Stage 1.1: Process problem identification with streaming response
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Detect language and determine user's preferred language
            detected_language, _ = await language_service.detect_language(message)
            user_language = self._determine_user_language(flow_state["session_data"], detected_language)
            
            # Add message to conversation history
            flow_state["conversation_history"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "stage": ConversationStage.PROBLEM_IDENTIFICATION.value
            })
            
            # Use semantic search to identify problems
            problems_search = await semantic_search_service.search_problems(
                query=message,
                limit=5,
                score_threshold=0.3
            )
            
            if problems_search.success and problems_search.results:
                # Process and store identified problems
                identified_problems = []
                for result in problems_search.results:
                    payload = result.payload
                    problem_data = {
                        "problem_id": payload.get("problem_id", ""),
                        "sub_category_id": payload.get("sub_category_id"),
                        "category": payload.get("category", "general"),
                        "problem_text": payload.get("text", ""),
                        "domain": payload.get("domain", ""),
                        "score": result.score,
                        "suggestions_available": True
                    }
                    identified_problems.append(problem_data)
                
                flow_state["identified_problems"] = identified_problems
                
                # Generate streaming response
                if user_language == Language.INDONESIAN:
                    intro_text = "Saya memahami situasi yang Anda alami. Berdasarkan apa yang Anda ceritakan, saya dapat mengidentifikasi beberapa area yang mungkin perlu perhatian."
                else:
                    intro_text = "I understand the situation you're experiencing. Based on what you've shared, I can identify several areas that may need attention."
                
                # Stream the introduction
                yield json.dumps({
                    "type": "chunk",
                    "content": intro_text,
                    "stage": ConversationStage.PROBLEM_IDENTIFICATION.value
                })
                
                # Transition to assessment
                async for chunk in self._transition_to_assessment_streaming(client_id):
                    yield chunk
            else:
                # No problems identified, generate dynamic response asking for more information
                flow_state = self.active_flows[client_id]
                conversation_history = flow_state.get("conversation_history", [])
                
                # Generate dynamic response for requesting more information
                response_data = await self.dynamic_response_service.generate_therapeutic_response(
                    user_message=message,
                    conversation_history=conversation_history,
                    context_type="problem_identification_clarification",
                    user_language=user_language,
                    session_data=flow_state.get("session_data", {})
                )
                
                response_text = response_data.get("response", "Could you tell me more about what you're experiencing?")
                
                yield json.dumps({
                    "type": "complete",
                    "content": response_text,
                    "stage": ConversationStage.PROBLEM_IDENTIFICATION.value,
                    "needs_more_info": True
                })
                
        except Exception as e:
            logger.error(f"Error in problem identification streaming: {str(e)}")
            error_response = {
                "type": "error",
                "message": "Sorry, an error occurred while identifying your concerns.",
                "stage": ConversationStage.PROBLEM_IDENTIFICATION.value
            }
            yield json.dumps(error_response)
    
    async def _transition_to_assessment_streaming(self, client_id: str):
        """
        Transition from problem identification to self-assessment with streaming
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Mark problem identification as complete
            flow_state["stage_progress"][ConversationStage.PROBLEM_IDENTIFICATION.value]["status"] = "completed"
            flow_state["current_stage"] = ConversationStage.SELF_ASSESSMENT
            flow_state["stage_progress"][ConversationStage.SELF_ASSESSMENT.value]["status"] = "in_progress"
            
            # Get the top identified problem for assessment
            if not flow_state["identified_problems"]:
                error_response = {
                    "type": "error",
                    "message": "Cannot start assessment without problem identification first.",
                    "stage": ConversationStage.SELF_ASSESSMENT.value
                }
                yield json.dumps(error_response)
                return
            
            top_problem = flow_state["identified_problems"][0]
            
            # Determine user's preferred language
            user_language = self._determine_user_language(flow_state["session_data"], Language.ENGLISH)
            
            # Start assessment using assessment service
            assessment_result = await assessment_service.start_assessment(
                client_id=client_id,
                problem_category=top_problem["category"],
                sub_category_id=top_problem.get("sub_category_id"),
                user_language=user_language
            )
            
            if assessment_result["type"] == "assessment_question":
                flow_state["assessment_data"] = assessment_result
                
                # Create language-appropriate introduction message
                if user_language == Language.INDONESIAN:
                    intro_message = "Baik, sekarang saya akan mengajukan beberapa pertanyaan untuk memahami situasi Anda lebih dalam."
                else:
                    intro_message = "Alright, now I will ask you some questions to better understand your situation."
                
                # Stream the introduction
                yield json.dumps({
                    "type": "chunk",
                    "content": intro_message + "\n\n",
                    "stage": ConversationStage.SELF_ASSESSMENT.value
                })
                
                # Stream the assessment question
                yield json.dumps({
                    "type": "complete",
                    "content": assessment_result["message"],
                    "stage": ConversationStage.SELF_ASSESSMENT.value,
                    "assessment_data": assessment_result,
                    "progress": assessment_result.get("progress", {})
                })
            else:
                yield json.dumps(assessment_result)
                
        except Exception as e:
            logger.error(f"Error transitioning to assessment: {str(e)}")
            error_response = {
                "type": "error",
                "message": "Sorry, an error occurred while starting the assessment.",
                "stage": ConversationStage.SELF_ASSESSMENT.value
            }
            yield json.dumps(error_response)
    
    async def _process_self_assessment_streaming(self, client_id: str, message: str):
        """
        Stage 1.2: Process self-assessment responses with streaming
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Determine user's preferred language
            user_language = self._determine_user_language(flow_state["session_data"], Language.ENGLISH)
            
            # Get current assessment question ID
            current_assessment = flow_state.get("assessment_data", {})
            if not current_assessment or "question" not in current_assessment:
                error_message = "Session assessment tidak ditemukan. Memulai ulang..." if user_language == Language.INDONESIAN else "Assessment session not found. Restarting..."
                yield json.dumps({
                    "type": "error",
                    "message": error_message,
                    "stage": ConversationStage.SELF_ASSESSMENT.value
                })
                return
            
            question_id = current_assessment["question"]["question_id"]
            
            # Process assessment response
            assessment_result = await assessment_service.process_assessment_response(
                client_id=client_id,
                response=message,
                question_id=question_id
            )
            
            if assessment_result["type"] == "assessment_question":
                # More questions available
                flow_state["assessment_data"] = assessment_result
                yield json.dumps({
                    "type": "complete",
                    "content": assessment_result["message"],
                    "stage": ConversationStage.SELF_ASSESSMENT.value,
                    "assessment_data": assessment_result,
                    "progress": assessment_result.get("progress", {})
                })
            elif assessment_result["type"] == "assessment_complete":
                # Assessment completed, transition to suggestions
                flow_state["stage_progress"][ConversationStage.SELF_ASSESSMENT.value]["status"] = "completed"
                flow_state["assessment_data"] = assessment_result
                
                async for chunk in self._transition_to_suggestions_streaming(client_id, assessment_result):
                    yield chunk
            else:
                yield json.dumps(assessment_result)
                
        except Exception as e:
            logger.error(f"Error processing self-assessment: {str(e)}")
            error_response = {
                "type": "error",
                "message": "Sorry, an error occurred during the assessment.",
                "stage": ConversationStage.SELF_ASSESSMENT.value
            }
            yield json.dumps(error_response)
    
    async def _transition_to_suggestions_streaming(self, client_id: str, assessment_result: Dict):
        """
        Transition to suggestions stage with streaming
        """
        try:
            flow_state = self.active_flows[client_id]
            flow_state["current_stage"] = ConversationStage.SUGGESTIONS
            flow_state["stage_progress"][ConversationStage.SUGGESTIONS.value]["status"] = "in_progress"
            
            # Determine user's preferred language
            user_language = self._determine_user_language(flow_state["session_data"], Language.ENGLISH)
            
            # Generate suggestions based on assessment
            suggestions = await self._generate_personalized_suggestions(
                flow_state["identified_problems"],
                assessment_result,
                user_language
            )
            
            flow_state["suggestions_provided"] = suggestions
            
            # Generate dynamic intro text for streaming suggestions
            intro_prompt = f"""
Generate a warm, encouraging introduction for presenting therapeutic suggestions in streaming format.
The message should:
- Reference that it's based on their assessment results
- Express that these suggestions can help them
- Use a supportive, hopeful tone
- Be brief and lead into suggestions

Language: {'Indonesian' if user_language == Language.INDONESIAN else 'English'}
Tone: Encouraging, supportive, professional
"""
            
            try:
                intro_text = await self.dynamic_response_service.generate_simple_response(
                    intro_prompt,
                    user_language=user_language,
                    context_type="general"
                )
                intro_text += "\n\n"  # Add spacing for the suggestions
            except:
                # Fallback to basic message
                if user_language == Language.INDONESIAN:
                    intro_text = "Berdasarkan hasil assessment, berikut adalah beberapa saran yang dapat membantu Anda:\n\n"
                else:
                    intro_text = "Based on the assessment results, here are some suggestions that can help you:\n\n"
            
            yield json.dumps({
                "type": "chunk",
                "content": intro_text,
                "stage": ConversationStage.SUGGESTIONS.value
            })
            
            # Stream each suggestion
            for i, suggestion in enumerate(suggestions, 1):
                suggestion_text = f"{i}. {suggestion['title']}\n{suggestion['description']}\n\n"
                yield json.dumps({
                    "type": "chunk",
                    "content": suggestion_text,
                    "stage": ConversationStage.SUGGESTIONS.value
                })
            
            # Final message
            if user_language == Language.INDONESIAN:
                final_text = "Apakah ada saran tertentu yang menarik bagi Anda? Atau apakah Anda memiliki pertanyaan tentang saran-saran ini?"
            else:
                final_text = "Are there any particular suggestions that interest you? Or do you have questions about these suggestions?"
            
            yield json.dumps({
                "type": "complete",
                "content": final_text,
                "stage": ConversationStage.SUGGESTIONS.value,
                "suggestions": suggestions
            })
            
        except Exception as e:
            logger.error(f"Error transitioning to suggestions: {str(e)}")
            error_response = {
                "type": "error",
                "message": "Sorry, an error occurred while generating suggestions.",
                "stage": ConversationStage.SUGGESTIONS.value
            }
            yield json.dumps(error_response)
    
    async def _process_suggestions_streaming(self, client_id: str, message: str):
        """
        Stage 1.3: Process user response to suggestions with streaming
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Determine user's preferred language
            user_language = self._determine_user_language(flow_state["session_data"], Language.ENGLISH)
            
            # Analyze user's response to suggestions
            suggestions_feedback = await self._analyze_suggestions_feedback(message, flow_state["suggestions_provided"])
            
            # Mark suggestions stage as complete
            flow_state["stage_progress"][ConversationStage.SUGGESTIONS.value]["status"] = "completed"
            flow_state["stage_progress"][ConversationStage.SUGGESTIONS.value]["data"]["user_feedback"] = suggestions_feedback
            
            # Transition to feedback collection
            async for chunk in self._transition_to_feedback_streaming(client_id, suggestions_feedback):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error processing suggestions: {str(e)}")
            # Generate dynamic error message
            error_prompt = """
Generate a brief, empathetic error message for when suggestion processing fails.
The message should:
- Apologize for the technical difficulty
- Acknowledge their input is valuable
- Encourage them to continue
- Maintain a supportive tone

Language: Indonesian
Tone: Apologetic, understanding, supportive
"""
            
            try:
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=Language.INDONESIAN,
                    context_type="general"
                )
            except:
                error_message = "Maaf, terjadi kesalahan saat memproses respons Anda."
            
            error_response = {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.SUGGESTIONS.value
            }
            yield json.dumps(error_response)
    
    async def _transition_to_feedback_streaming(self, client_id: str, suggestions_feedback: Dict):
        """
        Transition to feedback collection with streaming
        """
        try:
            flow_state = self.active_flows[client_id]
            flow_state["current_stage"] = ConversationStage.FEEDBACK
            flow_state["stage_progress"][ConversationStage.FEEDBACK.value]["status"] = "in_progress"
            
            # Determine user's preferred language
            user_language = self._determine_user_language(flow_state["session_data"], Language.ENGLISH)
            
            # Generate dynamic feedback request
            feedback_prompt = f"""
Generate a warm, empathetic message asking for feedback about the conversation.
The message should:
- Thank them for their engagement
- Ask how they feel after the conversation
- Inquire about what was helpful or not helpful
- Encourage honest feedback
- Maintain a caring, supportive tone

Language: {'Indonesian' if user_language == Language.INDONESIAN else 'English'}
Tone: Grateful, caring, encouraging
"""
            
            try:
                feedback_text = await self.dynamic_response_service.generate_simple_response(
                    feedback_prompt,
                    user_language=user_language,
                    context_type="general"
                )
            except:
                # Fallback to basic message
                if user_language == Language.INDONESIAN:
                    feedback_text = "Terima kasih atas tanggapan Anda. Bagaimana perasaan Anda setelah percakapan ini?"
                else:
                    feedback_text = "Thank you for your responses. How do you feel after our conversation?"
            
            yield json.dumps({
                "type": "complete",
                "content": feedback_text,
                "stage": ConversationStage.FEEDBACK.value,
                "suggestions_feedback": suggestions_feedback
            })
            
        except Exception as e:
            logger.error(f"Error transitioning to feedback: {str(e)}")
            # Generate dynamic error message
            error_prompt = """
Generate a brief, empathetic error message for when feedback request fails.
The message should:
- Apologize for the technical difficulty
- Reassure them their input is valuable
- Encourage them to continue sharing
- Maintain a supportive tone

Language: Indonesian
Tone: Apologetic, encouraging, supportive
"""
            
            try:
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=Language.INDONESIAN,
                    context_type="general"
                )
            except:
                error_message = "Maaf, terjadi kesalahan saat meminta feedback."
            
            error_response = {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.FEEDBACK.value
            }
            yield json.dumps(error_response)
    
    async def _process_feedback_streaming(self, client_id: str, message: str):
        """
        Stage 1.4: Process user feedback with streaming
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Store feedback
            feedback_data = {
                "feedback_text": message,
                "timestamp": datetime.now().isoformat(),
                "sentiment": await self._analyze_feedback_sentiment(message)
            }
            
            flow_state["feedback_collected"].append(feedback_data)
            flow_state["stage_progress"][ConversationStage.FEEDBACK.value]["status"] = "completed"
            flow_state["stage_progress"][ConversationStage.FEEDBACK.value]["data"]["collected_feedback"] = feedback_data
            
            # Transition to next action
            async for chunk in self._transition_to_next_action_streaming(client_id, feedback_data):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            # Generate dynamic error message
            error_prompt = """
Generate a brief, empathetic error message for when feedback processing fails.
The message should:
- Apologize for the technical difficulty
- Thank them for their feedback
- Reassure them their input is valuable
- Maintain a supportive tone

Language: Indonesian
Tone: Apologetic, grateful, supportive
"""
            
            try:
                error_message = await self.dynamic_response_service.generate_simple_response(
                    error_prompt,
                    user_language=Language.INDONESIAN,
                    context_type="general"
                )
            except:
                error_message = "Maaf, terjadi kesalahan saat memproses feedback Anda."
            
            error_response = {
                "type": "error",
                "message": error_message,
                "stage": ConversationStage.FEEDBACK.value
            }
            yield json.dumps(error_response)
    
    async def _transition_to_next_action_streaming(self, client_id: str, feedback_data: Dict):
        """
        Transition to next action with streaming
        """
        try:
            flow_state = self.active_flows[client_id]
            flow_state["current_stage"] = ConversationStage.NEXT_ACTION
            flow_state["stage_progress"][ConversationStage.NEXT_ACTION.value]["status"] = "in_progress"
            
            # Determine user's preferred language
            user_language = self._determine_user_language(flow_state["session_data"], Language.ENGLISH)
            
            # Generate next actions
            next_actions = await self._generate_next_actions(
                flow_state["identified_problems"],
                flow_state["assessment_data"],
                flow_state["suggestions_provided"],
                feedback_data,
                user_language
            )
            
            flow_state["next_actions"] = next_actions
            
            # Stream next actions
            if user_language == Language.INDONESIAN:
                intro_text = "Berdasarkan percakapan kita, berikut adalah beberapa langkah yang dapat Anda ambil selanjutnya:\n\n"
            else:
                intro_text = "Based on our conversation, here are some next steps you can take:\n\n"
            
            yield json.dumps({
                "type": "chunk",
                "content": intro_text,
                "stage": ConversationStage.NEXT_ACTION.value
            })
            
            # Stream each action
            for i, action in enumerate(next_actions, 1):
                action_text = f"{i}. {action['title']}\n{action['description']}\n\n"
                yield json.dumps({
                    "type": "chunk",
                    "content": action_text,
                    "stage": ConversationStage.NEXT_ACTION.value
                })
            
            # Final message
            if user_language == Language.INDONESIAN:
                final_text = "Apakah ada langkah tertentu yang ingin Anda coba? Saya di sini untuk mendukung Anda dalam perjalanan ini."
            else:
                final_text = "Is there a particular step you'd like to try? I'm here to support you on this journey."
            
            yield json.dumps({
                "type": "complete",
                "content": final_text,
                "stage": ConversationStage.NEXT_ACTION.value,
                "next_actions": next_actions,
                "conversation_complete": True,
                "flow_summary": self._generate_flow_summary(flow_state)
            })
            
        except Exception as e:
            logger.error(f"Error transitioning to next action: {str(e)}")
            error_response = {
                "type": "error",
                "message": "Sorry, an error occurred while generating next steps.",
                "stage": ConversationStage.NEXT_ACTION.value
            }
            yield json.dumps(error_response)
    
    async def _process_next_action_streaming(self, client_id: str, message: str):
        """
        Stage 1.5: Process user response to next actions with streaming
        """
        try:
            flow_state = self.active_flows[client_id]
            
            # Determine user's preferred language
            user_language = self._determine_user_language(flow_state["session_data"], Language.ENGLISH)
            
            # Analyze user's choice or response
            action_choice = await self._analyze_action_choice(message, flow_state["next_actions"])
            
            # Mark flow as complete
            flow_state["stage_progress"][ConversationStage.NEXT_ACTION.value]["status"] = "completed"
            flow_state["completed_at"] = datetime.now().isoformat()
            
            # Generate final response
            final_message = await self._generate_final_response(action_choice, flow_state)
            
            yield json.dumps({
                "type": "complete",
                "content": final_message,
                "stage": ConversationStage.NEXT_ACTION.value,
                "action_choice": action_choice,
                "flow_complete": True,
                "flow_summary": self._generate_flow_summary(flow_state)
            })
            
        except Exception as e:
            logger.error(f"Error processing next action: {str(e)}")
            error_response = {
                "type": "error",
                "message": "Sorry, an error occurred while processing your choice.",
                "stage": ConversationStage.NEXT_ACTION.value
            }
            yield json.dumps(error_response)

    async def _generate_next_actions(
        self, 
        identified_problems: List[Dict], 
        assessment_data: Dict, 
        suggestions_provided: List[str], 
        feedback_data: Dict, 
        user_language: Language
    ) -> List[Dict]:
        """Generate personalized next action recommendations"""
        try:
            # Prepare context for next actions generation
            context_prompt = f"""
            Based on the user's identified problems: {identified_problems}
            Assessment results: {assessment_data}
            Previous suggestions: {suggestions_provided}
            User feedback: {feedback_data}
            
            Generate 3-5 specific, actionable next steps that the user can take to address their mental health concerns.
            Each action should be practical, achievable, and tailored to their specific situation.
            """
            
            # Use dynamic response service to generate next actions
            response_data = await dynamic_response_service.generate_therapeutic_response(
                user_message=context_prompt,
                conversation_history=[],
                context_type="next_actions",
                user_language=user_language,
                session_data={
                    "problems": identified_problems,
                    "assessment": assessment_data,
                    "feedback": feedback_data
                }
            )
            
            # Parse the response into structured actions
            actions_text = response_data.get('response', '')
            
            # Create structured action items
            actions = []
            if actions_text:
                # Split by common action indicators
                action_lines = [line.strip() for line in actions_text.split('\n') if line.strip()]
                
                for i, line in enumerate(action_lines[:5], 1):  # Limit to 5 actions
                    if line and (line.startswith(str(i)) or line.startswith('-') or line.startswith('•')):
                        action_text = line.lstrip('0123456789.-• ').strip()
                        if action_text:
                            actions.append({
                                "id": f"action_{i}",
                                "title": action_text[:50] + "..." if len(action_text) > 50 else action_text,
                                "description": action_text,
                                "priority": "high" if i <= 2 else "medium",
                                "category": self._categorize_action(action_text)
                            })
            
            # Generate dynamic fallback actions if no actions were parsed
            if not actions:
                fallback_prompt = f"""
Generate 2-3 personalized next action recommendations based on the user's conversation context:

Problems identified: {identified_problems}
Assessment data: {assessment_data}
Suggestions provided: {suggestions}
User feedback: {feedback}

Create actionable, specific recommendations that include:
- Professional support options
- Self-care activities
- Practical steps they can take

Format as a numbered list with brief, clear action items.
Language: {'Indonesian' if user_language == Language.INDONESIAN else 'English'}
"""
                
                try:
                    response_data = await self.dynamic_response_service.generate_simple_response(
                        fallback_prompt,
                        user_language=user_language,
                        context_type="general"
                    )
                    
                    # Parse the response into structured actions
                    actions_text = response_data
                    action_lines = [line.strip() for line in actions_text.split('\n') if line.strip()]
                    
                    for i, line in enumerate(action_lines[:3], 1):
                        if line and (line.startswith(str(i)) or line.startswith('-') or line.startswith('•')):
                            action_text = line.lstrip('0123456789.-• ').strip()
                            if action_text:
                                actions.append({
                                    "id": f"action_fallback_{i}",
                                    "title": action_text[:50] + "..." if len(action_text) > 50 else action_text,
                                    "description": action_text,
                                    "priority": "high" if i <= 2 else "medium",
                                    "category": self._categorize_action(action_text)
                                })
                except Exception as e:
                    logger.error(f"Error generating dynamic fallback actions: {str(e)}")
                    # Basic fallback if dynamic generation fails
                    actions = [{
                        "id": "action_basic_fallback",
                        "title": "Continue self-care" if user_language == Language.ENGLISH else "Lanjutkan perawatan diri",
                        "description": "Keep taking care of your mental health" if user_language == Language.ENGLISH else "Terus jaga kesehatan mental Anda",
                        "priority": "medium",
                        "category": "self_care"
                    }]
            
            return actions
            
        except Exception as e:
            logger.error(f"Error generating next actions: {str(e)}")
            # Return basic fallback action
            return [{
                "id": "action_emergency_fallback",
                "title": "Continue self-care" if user_language == Language.ENGLISH else "Lanjutkan perawatan diri",
                "description": "Keep taking care of your mental health with positive activities" if user_language == Language.ENGLISH else "Terus jaga kesehatan mental Anda dengan aktivitas positif",
                "priority": "medium",
                "category": "self_care"
            }]
    
    def _categorize_action(self, action_text: str) -> str:
        """Categorize an action based on its content"""
        action_lower = action_text.lower()
        
        if any(word in action_lower for word in ['professional', 'therapist', 'counselor', 'psikolog', 'konselor']):
            return "professional_help"
        elif any(word in action_lower for word in ['exercise', 'workout', 'olahraga', 'aktivitas fisik']):
            return "physical_activity"
        elif any(word in action_lower for word in ['meditation', 'mindfulness', 'meditasi', 'relaksasi']):
            return "mindfulness"
        elif any(word in action_lower for word in ['social', 'friend', 'family', 'sosial', 'teman', 'keluarga']):
            return "social_support"
        elif any(word in action_lower for word in ['sleep', 'rest', 'tidur', 'istirahat']):
            return "sleep_hygiene"
        else:
            return "self_care"

# Create service instance
conversation_flow_service = ConversationFlowService()