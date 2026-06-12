import json
import asyncio
from typing import Dict, List, Set, Any
from datetime import datetime
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.global_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, channel: str = "global"):
        await websocket.accept()
        if channel == "global":
            self.global_connections.add(websocket)
        else:
            if channel not in self.active_connections:
                self.active_connections[channel] = set()
            self.active_connections[channel].add(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str = "global"):
        if channel == "global":
            self.global_connections.discard(websocket)
        elif channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
    
    async def broadcast(self, message: Dict[str, Any], channel: str = None):
        payload = json.dumps(message, default=str)
        dead_connections = []
        
        targets = self.global_connections.copy()
        if channel and channel in self.active_connections:
            targets.update(self.active_connections[channel])
        
        for connection in targets:
            try:
                await connection.send_text(payload)
            except Exception:
                dead_connections.append(connection)
        
        for conn in dead_connections:
            self.global_connections.discard(conn)
            for ch in self.active_connections.values():
                ch.discard(conn)
    
    async def send_email_event(self, email_data: Dict[str, Any]):
        await self.broadcast({
            "type": "email_ingested",
            "data": email_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_classification_event(self, email_id: str, classification: Dict[str, Any]):
        await self.broadcast({
            "type": "email_classified",
            "data": {
                "email_id": email_id,
                "classification": classification
            },
            "timestamp": datetime.utcnow().isoformat()
        }, channel=f"email:{email_id}")
    
    async def send_agent_event(self, email_id: str, trace: Dict[str, Any]):
        await self.broadcast({
            "type": "agent_decision",
            "data": {
                "email_id": email_id,
                "trace": trace
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_action_event(self, action_type: str, email_id: str, details: Dict[str, Any]):
        await self.broadcast({
            "type": "action_taken",
            "data": {
                "action_type": action_type,
                "email_id": email_id,
                "details": details
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_stats_update(self, stats: Dict[str, Any]):
        await self.broadcast({
            "type": "stats_update",
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        })

ws_manager = WebSocketManager()
