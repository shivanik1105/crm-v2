"""
WebSocket manager for real-time updates
"""
from fastapi import WebSocket
from typing import List, Dict
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_data: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.client_data[client_id] = {"websocket": websocket, "subscribed_to": []}
        print(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, client_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if client_id in self.client_data:
            del self.client_data[client_id]
        print(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for conn in dead_connections:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def notify_new_email(self, email_data: dict):
        """Notify all clients about new email"""
        await self.broadcast({
            "type": "new_email",
            "data": email_data
        })

    async def notify_email_classified(self, email_id: str, classification: dict):
        """Notify about email classification"""
        await self.broadcast({
            "type": "email_classified",
            "email_id": email_id,
            "data": classification
        })

    async def notify_stats_update(self, stats: dict):
        """Notify about updated dashboard stats"""
        await self.broadcast({
            "type": "stats_update",
            "data": stats
        })

    async def notify_churn_risk(self, contact_email: str, risk_data: dict):
        """Notify about churn risk detection"""
        await self.broadcast({
            "type": "churn_risk_alert",
            "contact": contact_email,
            "data": risk_data
        })

manager = ConnectionManager()
