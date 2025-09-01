from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime

from app.services.chat_service import ChatService
from app.services.conversation_flow_service import conversation_flow_service
from app.core.auth import get_current_user_optional

router = APIRouter()
chat_service = ChatService()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_data: Optional[Dict[str, Any]] = None
    semantic_context: Optional[List[Dict[str, Any]]] = None
    problem_category: Optional[str] = None
    assessment_progress: Optional[Dict[str, Any]] = None
    use_flow: Optional[bool] = True  # Enable conversation flow by default
    flow_mode: Optional[str] = "flow"  # "flow" or "legacy"

class ChatResponse(BaseModel):
    message: str
    sentiment: Dict[str, Any]
    is_crisis: bool
    timestamp: str
    conversation_id: str
    semantic_context: Optional[List[Dict[str, Any]]] = None
    relevant_resources: Optional[List[Dict[str, Any]]] = None
    assessment_recommendations: Optional[Dict[str, Any]] = None

class AssessmentRequest(BaseModel):
    problem_category: str
    session_data: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Send a chat message and get AI response
    Enhanced with conversation flow support
    """
    try:
        # Generate client ID (use user ID if authenticated, otherwise generate)
        client_id = current_user.get("id") if current_user else str(uuid.uuid4())

        # Process message with flow support
        if chat_message.use_flow and chat_message.flow_mode == "flow":
            # Use conversation flow service
            flow_status = conversation_flow_service.get_flow_status(client_id)
            
            if flow_status is None:
                # Start new conversation flow
                flow_response = await conversation_flow_service.start_conversation_flow(client_id, chat_message.message)
            else:
                # Continue existing flow
                flow_response = await conversation_flow_service.process_flow_message(client_id, chat_message.message)
            
            # Convert flow response to ChatResponse format
            response = {
                "message": flow_response.get("message", ""),
                "sentiment": {"score": 0.0, "label": "neutral"},  # Default sentiment
                "is_crisis": flow_response.get("type") == "crisis",
                "timestamp": datetime.now().isoformat(),
                "conversation_id": client_id,
                "semantic_context": flow_response.get("semantic_context", []),
                "relevant_resources": flow_response.get("relevant_resources", []),
                "assessment_recommendations": flow_response.get("assessment_recommendations", {})
            }
        else:
            # Use legacy chat service
            response = await chat_service.process_message(
                message=chat_message.message,
                client_id=client_id,
                session_data=chat_message.session_data,
                semantic_context=chat_message.semantic_context,
                problem_category=chat_message.problem_category,
                assessment_progress=chat_message.assessment_progress
            )

        return ChatResponse(**response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def send_message_stream(
    chat_message: ChatMessage,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Send a chat message and get streaming AI response
    """
    try:
        # Generate client ID
        client_id = current_user.get("id") if current_user else str(uuid.uuid4())

        async def generate_stream():
            async for chunk in chat_service.process_streaming_message(
                message=chat_message.message,
                client_id=client_id,
                session_data=chat_message.session_data,
                semantic_context=chat_message.semantic_context,
                problem_category=chat_message.problem_category,
                assessment_progress=chat_message.assessment_progress
            ):
                yield f"data: {chunk}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/recommendations")
async def get_assessment_recommendations(
    request: Dict[str, Any],
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Get assessment recommendations based on user message
    """
    try:
        # Generate client ID
        client_id = current_user.get("id") if current_user else str(uuid.uuid4())

        # Get assessment recommendations
        message = request.get("message", "")
        recommendations = await chat_service._get_assessment_recommendations(message)

        return {
            "success": True,
            "recommendations": recommendations,
            "client_id": client_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/start")
async def start_assessment(
    assessment_request: AssessmentRequest,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Start structured assessment
    """
    try:
        client_id = current_user.get("id") if current_user else str(uuid.uuid4())

        response = await chat_service.start_assessment(
            client_id=client_id,
            problem_category=assessment_request.problem_category,
            sub_category_id=getattr(assessment_request, 'sub_category_id', None)
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/respond")
async def respond_assessment(
    request: dict,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Process user response to assessment question
    """
    try:
        client_id = current_user.get("id") if current_user else str(uuid.uuid4())
        response = request.get("response", "")
        question_id = request.get("question_id", "")
        
        if not response or not question_id:
            raise HTTPException(status_code=400, detail="Response and question_id are required")
        
        result = await chat_service.process_assessment_response(
            client_id=client_id,
            response=response,
            question_id=question_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assessment/status")
async def get_assessment_status(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Get current assessment session status
    """
    try:
        client_id = current_user.get("id") if current_user else str(uuid.uuid4())
        status = chat_service.get_assessment_status(client_id)
        
        if status:
            return {
                "active": True,
                "progress": status.get("progress", {}),
                "current_question": status.get("current_question", {}),
                "problem_category": status.get("problem_category", "")
            }
        else:
            return {"active": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/cancel")
async def cancel_assessment(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Cancel active assessment session
    """
    try:
        client_id = current_user.get("id") if current_user else str(uuid.uuid4())
        success = chat_service.cancel_assessment(client_id)
        
        return {
            "success": success,
            "message": "Assessment dibatalkan" if success else "Tidak ada assessment aktif"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/history")
async def get_conversation_history(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Get conversation history for current user
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        client_id = current_user.get("id")
        history = chat_service.get_conversation_history(client_id)

        return {
            "conversation_history": history,
            "total_messages": len(history)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/clear")
async def clear_conversation_history(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Clear conversation history for current user
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        client_id = current_user.get("id")
        chat_service.clear_conversation_history(client_id)

        return {"message": "Conversation history cleared successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/status")
async def get_model_status():
    """
    Get Ollama model status
    """
    try:
        status = await chat_service.check_model_status()
        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/model/pull")
async def pull_model():
    """
    Pull Ollama model
    """
    try:
        success = await chat_service.ollama_service.pull_model()

        if success:
            return {"message": "Model pulled successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to pull model")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time chat with streaming support
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Check if this is an assessment response
            if message_data.get("type") == "assessment_response":
                # Handle assessment response directly
                response = message_data.get("response", "")
                question_id = message_data.get("question_id", "")
                
                if response and question_id:
                    # Process assessment response and stream the result
                    async for chunk in conversation_flow_service.process_flow_message_streaming(
                        client_id=client_id,
                        message=response,
                        session_data=message_data.get("session_data", {})
                    ):
                        await websocket.send_text(chunk)
                else:
                    error_response = {
                        "type": "error",
                        "message": "Response and question_id are required for assessment"
                    }
                    await websocket.send_text(json.dumps(error_response))
                continue

            # Process message with flow support
            use_flow = message_data.get("use_flow", True)
            
            if use_flow:
                # Use conversation flow service with streaming
                flow_status = conversation_flow_service.get_flow_status(client_id)
                
                if flow_status is None:
                    # Start new conversation flow with streaming
                    async for chunk in conversation_flow_service.start_conversation_flow_streaming(
                        client_id=client_id,
                        initial_message=message_data.get("message", ""),
                        session_data=message_data.get("session_data")
                    ):
                        await websocket.send_text(chunk)
                else:
                    # Continue existing flow with streaming
                    async for chunk in conversation_flow_service.process_flow_message_streaming(
                        client_id=client_id,
                        message=message_data.get("message", ""),
                        session_data=message_data.get("session_data")
                    ):
                        await websocket.send_text(chunk)
            else:
                # Use streaming chat service for better user experience
                async for chunk_json in chat_service.process_streaming_message(
                    message=message_data.get("message", ""),
                    client_id=client_id,
                    session_data=message_data.get("session_data"),
                    semantic_context=message_data.get("semantic_context"),
                    problem_category=message_data.get("problem_category"),
                    assessment_progress=message_data.get("assessment_progress")
                ):
                    # Forward the streaming chunk to the client
                    await websocket.send_text(chunk_json)

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
    except Exception as e:
        error_response = {
            "error": str(e),
            "message": "An error occurred while processing your message"
        }
        await websocket.send_text(json.dumps(error_response))

# Streaming WebSocket endpoint for real-time chat with streaming responses
@router.websocket("/ws/chat/stream")
async def streaming_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid.uuid4())  # Generate unique client ID

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Process message with streaming
            complete_data = None
            async for chunk_json in chat_service.process_streaming_message(
                message=message_data.get("message", ""),
                client_id=client_id,
                session_data=message_data.get("session_data"),
                semantic_context=message_data.get("semantic_context"),
                problem_category=message_data.get("problem_category"),
                assessment_progress=message_data.get("assessment_progress")
            ):
                # Parse the JSON chunk from the service
                try:
                    chunk_data = json.loads(chunk_json)
                    
                    # Forward the chunk as-is to maintain all metadata
                    await websocket.send_text(chunk_json)
                    
                    # Store complete data for final response
                    if chunk_data.get("type") == "complete":
                        complete_data = chunk_data
                        
                except json.JSONDecodeError:
                    # Handle plain text chunks (fallback)
                    await websocket.send_text(json.dumps({
                        "type": "chunk",
                        "content": chunk_json
                    }))

            # Send final completion signal with all metadata if available
            if complete_data:
                await websocket.send_text(json.dumps(complete_data))
            else:
                await websocket.send_text(json.dumps({
                    "type": "complete",
                    "message": "Stream completed"
                }))

    except WebSocketDisconnect:
        print(f"Streaming client {client_id} disconnected")
    except Exception as e:
        error_response = {
            "type": "error",
            "error": str(e),
            "message": "An error occurred while processing your message"
        }
        await websocket.send_text(json.dumps(error_response))

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "chat"}

@router.get("/flow/status/{client_id}")
async def get_flow_status(
    client_id: str,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Get conversation flow status for a client
    """
    try:
        flow_status = conversation_flow_service.get_flow_status(client_id)
        return {
            "client_id": client_id,
            "flow_status": flow_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/flow/reset/{client_id}")
async def reset_flow(
    client_id: str,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Reset conversation flow for a client
    """
    try:
        conversation_flow_service.reset_flow(client_id)
        return {
            "client_id": client_id,
            "message": "Conversation flow reset successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flow/all")
async def get_all_active_flows(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Get all active conversation flows (admin endpoint)
    """
    try:
        active_flows = conversation_flow_service.get_all_active_flows()
        return {
            "active_flows": active_flows,
            "total_count": len(active_flows)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


