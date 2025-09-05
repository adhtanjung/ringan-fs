"""
Main FastAPI Application Entry Point
Mental Health Chat Backend with Vector Database Integration
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.core.websocket import ConnectionManager
from app.core.auth import verify_token
from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service
from app.services.semantic_search_service import semantic_search_service
from app.services.dataset_management_service import dataset_management_service

# Load environment variables
load_dotenv()

# WebSocket connection manager
manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Mental Health Chat Backend...")

    # Initialize databases
    await init_db()
    print("✅ Database initialized")

    # Initialize vector database
    try:
        await vector_service.connect()
        await vector_service.create_collections()
        print("✅ Vector database initialized")
    except Exception as e:
        print(f"⚠️  Vector database initialization failed: {e}")

    # Initialize embedding service
    try:
        await embedding_service.initialize()
        print("✅ Embedding service initialized")
    except Exception as e:
        print(f"⚠️  Embedding service initialization failed: {e}")

    # Initialize semantic search service
    try:
        await semantic_search_service.initialize()
        print("✅ Semantic search service initialized")
    except Exception as e:
        print(f"⚠️  Semantic search service initialization failed: {e}")

    # Initialize dataset management service
    try:
        await dataset_management_service.initialize()
        print("✅ Dataset management service initialized")
    except Exception as e:
        print(f"⚠️  Dataset management service initialization failed: {e}")

    print("✅ Backend ready!")

    yield

    # Shutdown
    print("🛑 Shutting down backend...")
    await vector_service.close()
    await embedding_service.close()

# Create FastAPI app
app = FastAPI(
    title="Mental Health Chat API",
    description="AI-powered mental health chat application backend with vector database integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Mental Health Chat API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Vector Database Integration (Qdrant)",
            "Semantic Search",
            "Ollama AI Integration",
            "Excel Data Import",
            "Mental Health Assessment",
            "Therapeutic Suggestions"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check for all services"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {}
        }

        # Check vector database
        try:
            vector_health = await vector_service.health_check()
            health_status["services"]["vector_database"] = vector_health
        except Exception as e:
            health_status["services"]["vector_database"] = {"status": "unhealthy", "error": str(e)}

        # Check embedding service
        try:
            embedding_info = embedding_service.get_model_info()
            health_status["services"]["embedding_service"] = embedding_info
        except Exception as e:
            health_status["services"]["embedding_service"] = {"status": "unhealthy", "error": str(e)}

        # Check semantic search service
        try:
            search_stats = await semantic_search_service.get_collection_stats()
            health_status["services"]["semantic_search"] = {"status": "healthy", "collections": search_stats}
        except Exception as e:
            health_status["services"]["semantic_search"] = {"status": "unhealthy", "error": str(e)}

        return health_status

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# WebSocket endpoint for real-time chat
@app.websocket("/api/v1/chat/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Process message and send response
            response = await process_chat_message(data, client_id)
            await manager.send_personal_message(response, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)

async def process_chat_message(message: str, client_id: str):
    """Process chat message and return response"""
    try:
        # This will be implemented in the chat service
        from app.services.chat_service import ChatService
        chat_service = ChatService()
        return await chat_service.process_message(message, client_id)
    except Exception as e:
        return {
            "error": str(e),
            "message": "Maaf, terjadi kesalahan teknis. Silakan coba lagi."
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
