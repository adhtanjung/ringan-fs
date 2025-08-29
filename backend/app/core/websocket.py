from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_groups: Dict[str, List[str]] = {}

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
            logger.error(f"Error sending personal message: {str(e)}")

    async def send_to_client(self, client_id: str, message: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {str(e)}")
                # Remove disconnected client
                del self.active_connections[client_id]

    async def broadcast(self, message: str):
        disconnected_clients = []

        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            del self.active_connections[client_id]

    async def send_to_group(self, group_id: str, message: str):
        if group_id in self.connection_groups:
            for client_id in self.connection_groups[group_id]:
                await self.send_to_client(client_id, message)

    def add_to_group(self, client_id: str, group_id: str):
        if group_id not in self.connection_groups:
            self.connection_groups[group_id] = []

        if client_id not in self.connection_groups[group_id]:
            self.connection_groups[group_id].append(client_id)

    def remove_from_group(self, client_id: str, group_id: str):
        if group_id in self.connection_groups:
            if client_id in self.connection_groups[group_id]:
                self.connection_groups[group_id].remove(client_id)

    def get_active_connections_count(self) -> int:
        return len(self.active_connections)

    def get_connection_info(self) -> Dict:
        return {
            "active_connections": len(self.active_connections),
            "connection_groups": len(self.connection_groups),
            "clients": list(self.active_connections.keys())
        }


