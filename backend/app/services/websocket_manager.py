from typing import Dict, Set, Optional
from fastapi import WebSocket
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        # Store active connections: {session_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Store user connections: {telegram_id: Set[session_id]}
        self.user_connections: Dict[int, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, telegram_id: int):
        """Accept and register new connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        if telegram_id not in self.user_connections:
            self.user_connections[telegram_id] = set()
        self.user_connections[telegram_id].add(session_id)
        
        logger.info(f"WebSocket connected: session={session_id}, user={telegram_id}")
    
    def disconnect(self, session_id: str, telegram_id: int):
        """Remove connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if telegram_id in self.user_connections:
            self.user_connections[telegram_id].discard(session_id)
            if not self.user_connections[telegram_id]:
                del self.user_connections[telegram_id]
        
        logger.info(f"WebSocket disconnected: session={session_id}, user={telegram_id}")
    
    async def send_personal_message(self, message: dict, session_id: str):
        """Send message to specific session"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                # Remove dead connection
                self.active_connections.pop(session_id, None)
    
    async def send_to_user(self, message: dict, telegram_id: int):
        """Send message to all user's sessions"""
        if telegram_id in self.user_connections:
            session_ids = list(self.user_connections[telegram_id])
            for session_id in session_ids:
                await self.send_personal_message(message, session_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        dead_connections = []
        
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")
                dead_connections.append(session_id)
        
        # Clean up dead connections
        for session_id in dead_connections:
            self.active_connections.pop(session_id, None)
    
    def get_active_count(self) -> int:
        """Get count of active connections"""
        return len(self.active_connections)
    
    def get_user_sessions(self, telegram_id: int) -> list:
        """Get all active session IDs for user"""
        return list(self.user_connections.get(telegram_id, set()))
    
    def is_session_connected(self, session_id: str) -> bool:
        """Check if session is connected"""
        return session_id in self.active_connections


# Global connection manager instance
manager = ConnectionManager()


class WebSocketService:
    """WebSocket service for real-time updates"""
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.manager = manager
    
    async def handle_session_updates(
        self,
        websocket: WebSocket,
        session_id: str,
        telegram_id: int
    ):
        """Handle real-time session updates"""
        await self.manager.connect(websocket, session_id, telegram_id)
        
        try:
            while True:
                # Wait for messages from client (heartbeat or commands)
                try:
                    data = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=30.0
                    )
                    
                    # Handle client messages
                    await self._handle_client_message(data, session_id, telegram_id)
                    
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await self.send_ping(session_id)
                
        except Exception as e:
            logger.error(f"WebSocket error for session {session_id}: {e}")
        finally:
            self.manager.disconnect(session_id, telegram_id)
    
    async def _handle_client_message(
        self,
        data: dict,
        session_id: str,
        telegram_id: int
    ):
        """Handle messages from client"""
        message_type = data.get('type')
        
        if message_type == 'ping':
            await self.send_pong(session_id)
        
        elif message_type == 'traffic_update':
            # Client sends traffic update
            await self._handle_traffic_update(data, session_id)
        
        elif message_type == 'command':
            # Handle commands (pause, resume, etc.)
            await self._handle_command(data, session_id, telegram_id)
    
    async def _handle_traffic_update(self, data: dict, session_id: str):
        """Handle traffic update from client"""
        # This would typically update the database
        # For now, just acknowledge
        await self.send_session_update(
            session_id=session_id,
            update_type='traffic_acknowledged',
            data={'received': True}
        )
    
    async def _handle_command(self, data: dict, session_id: str, telegram_id: int):
        """Handle commands from client"""
        command = data.get('command')
        
        if command == 'pause':
            # Handle pause command
            await self.send_session_update(
                session_id=session_id,
                update_type='paused',
                data={'paused': True}
            )
        
        elif command == 'resume':
            # Handle resume command
            await self.send_session_update(
                session_id=session_id,
                update_type='resumed',
                data={'paused': False}
            )
    
    async def send_session_update(
        self,
        session_id: str,
        update_type: str,
        data: dict
    ):
        """Send session update to client"""
        message = {
            'type': 'session_update',
            'update_type': update_type,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        await self.manager.send_personal_message(message, session_id)
    
    async def send_traffic_stats(
        self,
        session_id: str,
        sent_mb: float,
        speed_mb_s: float,
        earned_usd: float
    ):
        """Send traffic statistics to client"""
        message = {
            'type': 'traffic_stats',
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'sent_mb': sent_mb,
                'speed_mb_s': speed_mb_s,
                'earned_usd': earned_usd,
            }
        }
        await self.manager.send_personal_message(message, session_id)
    
    async def send_balance_update(
        self,
        telegram_id: int,
        new_balance: float,
        delta: float
    ):
        """Send balance update to user"""
        message = {
            'type': 'balance_update',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'new_balance': new_balance,
                'delta': delta,
            }
        }
        await self.manager.send_to_user(message, telegram_id)
    
    async def send_session_completed(
        self,
        telegram_id: int,
        session_id: str,
        stats: dict
    ):
        """Send session completed notification"""
        message = {
            'type': 'session_completed',
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': stats
        }
        await self.manager.send_to_user(message, telegram_id)
    
    async def send_notification(
        self,
        telegram_id: int,
        title: str,
        body: str,
        notification_type: str
    ):
        """Send notification via WebSocket"""
        message = {
            'type': 'notification',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'title': title,
                'body': body,
                'notification_type': notification_type,
            }
        }
        await self.manager.send_to_user(message, telegram_id)
    
    async def send_system_message(
        self,
        telegram_id: int,
        message_text: str,
        severity: str = 'info'
    ):
        """Send system message to user"""
        message = {
            'type': 'system_message',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'message': message_text,
                'severity': severity,
            }
        }
        await self.manager.send_to_user(message, telegram_id)
    
    async def send_ping(self, session_id: str):
        """Send ping to keep connection alive"""
        message = {
            'type': 'ping',
            'timestamp': datetime.utcnow().isoformat(),
        }
        await self.manager.send_personal_message(message, session_id)
    
    async def send_pong(self, session_id: str):
        """Send pong response"""
        message = {
            'type': 'pong',
            'timestamp': datetime.utcnow().isoformat(),
        }
        await self.manager.send_personal_message(message, session_id)
    
    async def broadcast_price_update(self, price_per_gb: float, message: str):
        """Broadcast price update to all connected clients"""
        broadcast_message = {
            'type': 'price_update',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'price_per_gb': price_per_gb,
                'message': message,
            }
        }
        await self.manager.broadcast(broadcast_message)
    
    async def broadcast_maintenance_mode(self, enabled: bool, message: str):
        """Broadcast maintenance mode notification"""
        broadcast_message = {
            'type': 'maintenance',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'enabled': enabled,
                'message': message,
            }
        }
        await self.manager.broadcast(broadcast_message)
    
    def get_connection_stats(self) -> dict:
        """Get WebSocket connection statistics"""
        return {
            'total_connections': self.manager.get_active_count(),
            'unique_users': len(self.manager.user_connections),
            'timestamp': datetime.utcnow().isoformat(),
        }
