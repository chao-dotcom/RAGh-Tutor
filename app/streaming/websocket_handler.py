"""WebSocket handler for streaming"""
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        """Remove connection"""
        self.active_connections.pop(client_id, None)
    
    async def send_message(self, client_id: str, message: Dict):
        """Send message to specific client"""
        websocket = self.active_connections.get(client_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: Dict):
        """Broadcast to all connected clients"""
        for client_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                self.disconnect(client_id)


class WebSocketHandler:
    """Handle WebSocket connections (backward compatibility)"""
    
    def __init__(self):
        self.connections: set = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.connections.add(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.connections.discard(websocket)
    
    async def send_message(self, websocket: WebSocket, message: dict):
        """Send message through WebSocket"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast to all connections"""
        for connection in list(self.connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                self.connections.discard(connection)

