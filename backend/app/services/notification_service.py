import requests
import json
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.config import settings


def send_fcm_notification(device_token: str, title: str, body: str, data: Dict = None):
    """Send FCM notification to a device"""
    if not settings.FCM_SERVER_KEY:
        return False
    
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": f"key={settings.FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "to": device_token,
        "notification": {
            "title": title,
            "body": body
        }
    }
    
    if data:
        payload["data"] = data
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"FCM notification error: {e}")
        return False


def send_notification_to_user(db: Session, telegram_id: int, title: str, body: str, data: Dict = None):
    """Send notification to a specific user"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user or not user.device_token or not user.notifications_enabled:
        return False
    
    return send_fcm_notification(user.device_token, title, body, data)


def send_notification_to_all(db: Session, title: str, body: str, data: Dict = None):
    """Send notification to all enabled users"""
    users = db.query(User).filter(
        User.notifications_enabled == True,
        User.device_token.isnot(None)
    ).all()
    
    results = []
    for user in users:
        success = send_fcm_notification(user.device_token, title, body, data)
        results.append({"telegram_id": user.telegram_id, "success": success})
    
    return results
