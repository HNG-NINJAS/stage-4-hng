"""Pydantic models"""
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional


class EmailNotificationMessage(BaseModel):
    """Email notification message from queue"""
    message_id: str
    correlation_id: str
    user_id: str
    template_id: str
    template_data: Dict[str, Any]
    recipient_email: EmailStr
    language_code: str = "en"
    priority: str = "normal"
    retry_count: int = 0


class TemplateRenderRequest(BaseModel):
    """Request to render template"""
    data: Dict[str, Any]
    language_code: str = "en"


class TemplateRenderResponse(BaseModel):
    """Response from template service"""
    subject: str
    body: str
    template_id: str
    language_code: str
