from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.services.websocket_manager import ws_manager
from app.core.security import decode_jwt

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    REAL WebSocket endpoint for live updates
    """
    # Verify token
    try:
        payload = decode_jwt(token)
        telegram_id = payload.get("telegram_id")
        
        if not telegram_id:
            await websocket.close(code=1008)
            return
    
    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        await websocket.close(code=1008)
        return
    
    # Connect
    await ws_manager.connect(websocket, telegram_id)
    
    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            
            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, telegram_id)
        logger.info(f"WebSocket disconnected: user {telegram_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket, telegram_id)
