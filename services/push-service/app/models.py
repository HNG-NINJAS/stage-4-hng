from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class PushNotificationRequest(BaseModel):
    """Push notification request from queue"""
    message_id: str
    correlation_id: str
    user_id: str
    template_id: str
    template_data: Dict[str, Any]
    device_token: str
    language_code: str = "en"
    priority: str = "normal"  # high, normal
    retry_count: int = 0


class PushNotificationResponse(BaseModel):
    """Response after sending notification"""
    success: bool
    message_id: str
    user_id: str
    sent_at: Optional[datetime] = None
    error: Optional[str] = None


class FCMNotification(BaseModel):
    """FCM notification payload"""
    title: str
    body: str
    image: Optional[str] = None
    click_action: Optional[str] = None
    data: Optional[Dict[str, str]] = None