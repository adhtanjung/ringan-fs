"""
Simple FastAPI WebSocket Server for Testing
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Simple WebSocket Test Server",
    description="Simple WebSocket server for testing chat functionality",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")

# Create connection manager
manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "message": "Simple WebSocket Test Server",
        "version": "1.0.0",
        "status": "running",
        "websocket_endpoint": "/api/v1/chat/ws/{client_id}"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "clients": list(manager.active_connections.keys())
    }

# WebSocket endpoint for real-time chat
@app.websocket("/api/v1/chat/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received from {client_id}: {data}")

            # Simple echo response for testing
            response = {
                "type": "message",
                "content": f"Echo: {data}",
                "client_id": client_id,
                "timestamp": "2024-01-01T00:00:00Z"
            }

            await manager.send_personal_message(json.dumps(response), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}")
        manager.disconnect(websocket, client_id)

if __name__ == "__main__":
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )









