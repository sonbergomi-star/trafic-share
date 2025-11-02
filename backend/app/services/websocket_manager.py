from typing import Dict, Set, Any
from fastapi import WebSocket
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    REAL WebSocket manager for live updates
    Handles real-time session data streaming
    """
    
    def __init__(self):
        # telegram_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # session_id -> telegram_id mapping
        self.session_users: Dict[str, int] = {}
    
    async def connect(self, websocket: WebSocket, telegram_id: int):
        """
        REAL connect websocket for user
        """
        await websocket.accept()
        
        if telegram_id not in self.active_connections:
            self.active_connections[telegram_id] = set()
        
        self.active_connections[telegram_id].add(websocket)
        
        logger.info(f"WebSocket connected: user {telegram_id}")
        
        # Send welcome message
        await self.send_to_user(telegram_id, {
            "type": "connected",
            "message": "WebSocket connection established",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket, telegram_id: int):
        """
        REAL disconnect websocket
        """
        if telegram_id in self.active_connections:
            self.active_connections[telegram_id].discard(websocket)
            
            if not self.active_connections[telegram_id]:
                del self.active_connections[telegram_id]
        
        logger.info(f"WebSocket disconnected: user {telegram_id}")
    
    async def send_to_user(self, telegram_id: int, data: Dict[str, Any]):
        """
        REAL send message to specific user's all connections
        """
        if telegram_id not in self.active_connections:
            return
        
        message = json.dumps(data)
        
        # Send to all user's connections
        disconnected = set()
        
        for connection in self.active_connections[telegram_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"WebSocket send error: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected
        for connection in disconnected:
            self.disconnect(connection, telegram_id)
    
    async def broadcast_to_admins(self, data: Dict[str, Any]):
        """
        REAL broadcast to all admin connections
        """
        from app.core.config import settings
        
        for admin_id in settings.admin_ids_list:
            await self.send_to_user(admin_id, data)
    
    async def send_session_update(
        self,
        telegram_id: int,
        session_id: str,
        mb_sent: float,
        speed_mbps: float,
        duration_sec: int,
        estimated_earnings: float
    ):
        """
        REAL send session live update
        """
        data = {
            "type": "session_update",
            "session_id": session_id,
            "mb_sent": round(mb_sent, 2),
            "gb_sent": round(mb_sent / 1024, 3),
            "speed_mbps": round(speed_mbps, 2),
            "duration_sec": duration_sec,
            "estimated_earnings": round(estimated_earnings, 6),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_to_user(telegram_id, data)
    
    async def send_balance_update(
        self,
        telegram_id: int,
        new_balance: float,
        delta: float
    ):
        """
        REAL send balance update notification
        """
        data = {
            "type": "balance_update",
            "new_balance": round(new_balance, 2),
            "delta": round(delta, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_to_user(telegram_id, data)
    
    async def send_price_update(self, price_per_gb: float, message: str):
        """
        REAL broadcast price update to all connected users
        """
        data = {
            "type": "price_update",
            "price_per_gb": price_per_gb,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all connected users
        for telegram_id in list(self.active_connections.keys()):
            await self.send_to_user(telegram_id, data)
    
    def get_active_users_count(self) -> int:
        """Get count of users with active WebSocket connections"""
        return len(self.active_connections)
    
    def is_user_connected(self, telegram_id: int) -> bool:
        """Check if user has active connection"""
        return telegram_id in self.active_connections and len(self.active_connections[telegram_id]) > 0


# Global WebSocket manager instance
ws_manager = WebSocketManager()
