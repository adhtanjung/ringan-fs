import json
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from app.services.semantic_search_service import semantic_search_service
from app.services.vector_service import vector_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AssessmentService:
    def __init__(self):
        # Store active assessment sessions
        self.active_sessions: Dict[str, Dict] = {}
        
    async def start_assessment(self, client_id: str, problem_category: str, sub_category_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a structured assessment flow based on problem category
        """
        try:
            # Search for assessment questions related to the problem
            search_response = await semantic_search_service.search_assessment_questions(
                problem_description=problem_category,
                sub_category_id=sub_category_id,
                limit=50,  # Get more questions to build proper flow
                score_threshold=0.3
            )
            
            if not search_response.success or not search_response.results:
                return {
                    "type": "error",
                    "message": "Tidak dapat menemukan pertanyaan assessment untuk kategori ini."
                }
            
            # Extract questions and build assessment flow
            questions = []
            for result in search_response.results:
                payload = result.payload
                questions.append({
                    "question_id": payload.get("question_id", ""),
                    "sub_category_id": payload.get("sub_category_id", ""),
                    "batch_id": payload.get("batch_id", ""),
                    "question_text": payload.get("text", ""),  # 'text' field from vector storage
                    "response_type": payload.get("response_type", "text"),
                    "next_step": payload.get("next_step"),
                    "clusters": payload.get("clusters", []),
                    "domain": payload.get("domain", ""),
                    "score": result.score
                })
            
            # Find the first question (usually has no previous reference or highest score)
            first_question = self._find_first_question(questions)
            
            if not first_question:
                # Fallback to highest scoring question
                first_question = questions[0] if questions else None
            
            if not first_question:
                return {
                    "type": "error",
                    "message": "Tidak dapat memulai assessment."
                }
            
            # Initialize assessment session
            session_data = {
                "client_id": client_id,
                "problem_category": problem_category,
                "sub_category_id": sub_category_id,
                "all_questions": questions,
                "current_question": first_question,
                "answered_questions": [],
                "responses": {},
                "started_at": datetime.now().isoformat(),
                "progress": {
                    "current_step": 1,
                    "total_estimated": min(len(questions), 10),  # Limit to reasonable number
                    "completed_questions": 0
                }
            }
            
            self.active_sessions[client_id] = session_data
            
            return {
                "type": "assessment_question",
                "session_id": client_id,
                "question": first_question,
                "progress": session_data["progress"],
                "message": self._format_question_message(first_question)
            }
            
        except Exception as e:
            logger.error(f"Error starting assessment: {str(e)}")
            return {
                "type": "error",
                "message": "Maaf, terjadi kesalahan saat memulai assessment."
            }
    
    async def process_assessment_response(self, client_id: str, response: str, question_id: str) -> Dict[str, Any]:
        """
        Process user response to assessment question and determine next step
        """
        try:
            if client_id not in self.active_sessions:
                return {
                    "type": "error",
                    "message": "Session assessment tidak ditemukan. Silakan mulai assessment baru."
                }
            
            session = self.active_sessions[client_id]
            current_question = session["current_question"]
            
            # Validate question ID
            if current_question["question_id"] != question_id:
                return {
                    "type": "error",
                    "message": "Pertanyaan tidak sesuai dengan session saat ini."
                }
            
            # Store the response
            session["responses"][question_id] = {
                "response": response,
                "question_text": current_question["question_text"],
                "response_type": current_question["response_type"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to answered questions
            session["answered_questions"].append(current_question)
            session["progress"]["completed_questions"] += 1
            
            # Find next question
            next_question = await self._find_next_question(session, current_question, response)
            
            if next_question:
                # Continue assessment
                session["current_question"] = next_question
                session["progress"]["current_step"] += 1
                
                return {
                    "type": "assessment_question",
                    "session_id": client_id,
                    "question": next_question,
                    "progress": session["progress"],
                    "message": self._format_question_message(next_question)
                }
            else:
                # Assessment complete
                return await self._complete_assessment(client_id)
                
        except Exception as e:
            logger.error(f"Error processing assessment response: {str(e)}")
            return {
                "type": "error",
                "message": "Terjadi kesalahan saat memproses jawaban Anda."
            }
    
    async def _find_next_question(self, session: Dict, current_question: Dict, response: str) -> Optional[Dict]:
        """
        Find the next question based on current question's next_step logic
        """
        try:
            next_step = current_question.get("next_step")
            all_questions = session["all_questions"]
            answered_ids = [q["question_id"] for q in session["answered_questions"]]
            
            # If there's a specific next_step, try to find that question
            if next_step and next_step.strip():
                for question in all_questions:
                    if (question["question_id"] == next_step and 
                        question["question_id"] not in answered_ids):
                        return question
            
            # Fallback: find next question in same batch or sub_category
            current_batch = current_question.get("batch_id")
            current_sub_category = current_question.get("sub_category_id")
            
            # Try to find next question in same batch
            if current_batch:
                for question in all_questions:
                    if (question["batch_id"] == current_batch and 
                        question["question_id"] not in answered_ids and
                        question["question_id"] != current_question["question_id"]):
                        return question
            
            # Try to find next question in same sub_category
            if current_sub_category:
                for question in all_questions:
                    if (question["sub_category_id"] == current_sub_category and 
                        question["question_id"] not in answered_ids and
                        question["question_id"] != current_question["question_id"]):
                        return question
            
            # Final fallback: any unanswered question
            for question in all_questions:
                if question["question_id"] not in answered_ids:
                    return question
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding next question: {str(e)}")
            return None
    
    def _find_first_question(self, questions: List[Dict]) -> Optional[Dict]:
        """
        Find the first question in the assessment flow
        """
        if not questions:
            return None
        
        # Look for questions that are not referenced as next_step by others
        all_next_steps = set()
        for q in questions:
            if q.get("next_step"):
                all_next_steps.add(q["next_step"])
        
        # Find questions not referenced as next steps (potential starting points)
        starting_questions = []
        for q in questions:
            if q["question_id"] not in all_next_steps:
                starting_questions.append(q)
        
        if starting_questions:
            # Return the one with highest score
            return max(starting_questions, key=lambda x: x.get("score", 0))
        
        # Fallback to highest scoring question
        return max(questions, key=lambda x: x.get("score", 0))
    
    def _format_question_message(self, question: Dict) -> str:
        """
        Format question for display to user
        """
        question_text = question["question_text"]
        response_type = question.get("response_type", "text")
        
        if response_type == "scale":
            return f"{question_text}\n\nSilakan berikan jawaban dalam skala 1-10 (1 = sangat rendah, 10 = sangat tinggi)"
        elif response_type == "yes_no":
            return f"{question_text}\n\nSilakan jawab dengan 'ya' atau 'tidak'"
        else:
            return f"{question_text}\n\nSilakan berikan jawaban Anda dengan bebas."
    
    async def _complete_assessment(self, client_id: str) -> Dict[str, Any]:
        """
        Complete the assessment and generate results
        """
        try:
            session = self.active_sessions[client_id]
            responses = session["responses"]
            
            # Generate assessment summary
            total_questions = len(session["answered_questions"])
            problem_category = session["problem_category"]
            
            # Calculate basic metrics
            scale_responses = []
            text_responses = []
            
            for response_data in responses.values():
                if response_data["response_type"] == "scale":
                    try:
                        scale_value = float(response_data["response"])
                        if 1 <= scale_value <= 10:
                            scale_responses.append(scale_value)
                    except ValueError:
                        continue
                else:
                    text_responses.append(response_data["response"])
            
            average_score = sum(scale_responses) / len(scale_responses) if scale_responses else 5.0
            
            # Generate detailed analysis
            analysis = self._generate_analysis(scale_responses, text_responses, problem_category)
            insights = self._generate_insights(session, average_score)
            
            # Generate recommendations based on responses
            recommendations = await self._generate_recommendations(session)
            
            # Clean up session
            completed_session = self.active_sessions.pop(client_id)
            
            return {
                "type": "assessment_complete",
                "session_id": client_id,
                "summary": f"Assessment untuk {problem_category} telah selesai dengan {total_questions} pertanyaan dijawab dalam {self._calculate_duration(completed_session)} menit.",
                "score": f"{round(average_score, 1)}/10",
                "analysis": analysis,
                "insights": insights,
                "recommendations": [rec["text"] for rec in recommendations],
                "detailed_results": {
                    "total_questions": total_questions,
                    "problem_category": problem_category,
                    "average_score": round(average_score, 1),
                    "completed_at": datetime.now().isoformat(),
                    "duration_minutes": self._calculate_duration(completed_session),
                    "scale_responses_count": len(scale_responses),
                    "text_responses_count": len(text_responses)
                },
                "message": self._format_completion_message(average_score, problem_category)
            }
            
        except Exception as e:
            logger.error(f"Error completing assessment: {str(e)}")
            return {
                "type": "error",
                "message": "Terjadi kesalahan saat menyelesaikan assessment."
            }
    
    async def _generate_recommendations(self, session: Dict) -> List[Dict]:
        """
        Generate therapeutic recommendations based on assessment responses
        """
        try:
            problem_category = session["problem_category"]
            sub_category_id = session.get("sub_category_id")
            
            # Search for relevant therapeutic suggestions
            search_response = await semantic_search_service.search_therapeutic_suggestions(
                problem_description=problem_category,
                sub_category_id=sub_category_id,
                limit=5,
                score_threshold=0.4
            )
            
            recommendations = []
            if search_response.success:
                for result in search_response.results:
                    payload = result.payload
                    recommendations.append({
                        "suggestion_id": payload.get("suggestion_id", ""),
                        "text": payload.get("text", ""),
                        "cluster": payload.get("cluster", ""),
                        "resource_link": payload.get("resource_link"),
                        "score": result.score
                    })
            
            return recommendations[:3]  # Return top 3 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def _generate_analysis(self, scale_responses: List[float], text_responses: List[str], problem_category: str) -> str:
        """
        Generate detailed analysis based on responses
        """
        if not scale_responses:
            return f"Berdasarkan jawaban Anda untuk {problem_category}, kami mengidentifikasi beberapa area yang memerlukan perhatian khusus."
        
        avg_score = sum(scale_responses) / len(scale_responses)
        
        if avg_score <= 3:
            return f"Analisis menunjukkan Anda mengalami tingkat kesulitan yang signifikan terkait {problem_category}. Skor rata-rata {avg_score:.1f} mengindikasikan perlunya dukungan profesional dan strategi coping yang lebih intensif."
        elif avg_score <= 6:
            return f"Hasil analisis menunjukkan Anda menghadapi beberapa tantangan terkait {problem_category}. Dengan skor rata-rata {avg_score:.1f}, ada ruang untuk perbaikan melalui strategi self-care dan dukungan yang tepat."
        else:
            return f"Analisis menunjukkan kondisi Anda terkait {problem_category} relatif stabil dengan skor rata-rata {avg_score:.1f}. Fokus pada pemeliharaan kesehatan mental dan pencegahan akan sangat bermanfaat."
    
    def _generate_insights(self, session: Dict, average_score: float) -> List[str]:
        """
        Generate insights based on assessment patterns
        """
        insights = []
        responses = session["responses"]
        
        # Analyze response patterns
        high_scores = sum(1 for r in responses.values() 
                         if r.get("response_type") == "scale" and 
                         float(r.get("response", 0)) >= 7)
        
        low_scores = sum(1 for r in responses.values() 
                        if r.get("response_type") == "scale" and 
                        float(r.get("response", 0)) <= 3)
        
        total_scale_responses = sum(1 for r in responses.values() 
                                   if r.get("response_type") == "scale")
        
        if total_scale_responses > 0:
            if high_scores / total_scale_responses > 0.6:
                insights.append("Sebagian besar respons Anda menunjukkan tingkat kesulitan yang tinggi, menandakan perlunya perhatian segera.")
            elif low_scores / total_scale_responses > 0.6:
                insights.append("Mayoritas respons Anda menunjukkan kondisi yang relatif baik, yang merupakan indikator positif.")
            else:
                insights.append("Respons Anda menunjukkan variasi yang menandakan beberapa area memerlukan perhatian lebih.")
        
        # Duration-based insights
        duration = self._calculate_duration(session)
        if duration < 3:
            insights.append("Assessment diselesaikan dengan cepat, menunjukkan kemungkinan sudah memiliki pemahaman yang baik tentang kondisi diri.")
        elif duration > 10:
            insights.append("Waktu yang dihabiskan untuk assessment menunjukkan pertimbangan yang matang dalam menjawab setiap pertanyaan.")
        
        return insights[:3]  # Return max 3 insights
    
    def _calculate_duration(self, session: Dict) -> int:
        """
        Calculate assessment duration in minutes
        """
        try:
            start_time = datetime.fromisoformat(session["start_time"])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() / 60
            return max(1, round(duration))
        except Exception:
            return 1
    
    def _format_completion_message(self, average_score: float, problem_category: str) -> str:
        """
        Format completion message based on assessment results
        """
        if average_score <= 3:
            level = "rendah"
            message = "Hasil assessment menunjukkan Anda mungkin mengalami tingkat kesulitan yang cukup signifikan."
        elif average_score <= 6:
            level = "sedang"
            message = "Hasil assessment menunjukkan Anda mengalami beberapa tantangan yang perlu perhatian."
        else:
            level = "baik"
            message = "Hasil assessment menunjukkan kondisi Anda relatif stabil dengan beberapa area yang bisa ditingkatkan."
        
        return f"""🎯 **Assessment Selesai**

{message}

**Kategori**: {problem_category}
**Skor Rata-rata**: {average_score}/10 ({level})

Berikut adalah beberapa rekomendasi yang dapat membantu Anda:"""
    
    def get_session_status(self, client_id: str) -> Optional[Dict]:
        """
        Get current assessment session status
        """
        return self.active_sessions.get(client_id)
    
    def cancel_assessment(self, client_id: str) -> bool:
        """
        Cancel active assessment session
        """
        if client_id in self.active_sessions:
            del self.active_sessions[client_id]
            return True
        return False

# Global instance
assessment_service = AssessmentService()