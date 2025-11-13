import logging
from typing import Optional
from app.models import PushNotificationRequest, PushNotificationResponse, FCMNotification
from app.services.template_client import TemplateClient
from app.services.fcm_service import FCMService
from app.config import get_settings
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()


class NotificationService:
    """Main notification business logic"""
    
    def __init__(self):
        self.template_client = TemplateClient(settings.template_service_url)
        self.fcm_service = FCMService(settings.fcm_credentials_path)
    
    async def send_notification(
        self,
        request: PushNotificationRequest
    ) -> PushNotificationResponse:
        """
        Send push notification
        
        1. Render template
        2. Send via FCM
        3. Return result
        """
        try:
            # Step 1: Render template
            rendered = await self.template_client.render_template(
                template_id=request.template_id,
                data=request.template_data,
                language_code=request.language_code,
                correlation_id=request.correlation_id
            )
            
            if not rendered:
                logger.error(f"Failed to render template {request.template_id}")
                return PushNotificationResponse(
                    success=False,
                    message_id=request.message_id,
                    user_id=request.user_id,
                    error="TEMPLATE_RENDER_FAILED"
                )
            
            # Step 2: Build FCM notification
            notification = FCMNotification(
                title=rendered.get("subject", "Notification"),
                body=rendered["body"],
                data={
                    "message_id": request.message_id,
                    "template_id": request.template_id
                }
            )
            
            # Step 3: Send via FCM
            sent = await self.fcm_service.send_notification(
                device_token=request.device_token,
                notification=notification
            )
            
            if sent:
                return PushNotificationResponse(
                    success=True,
                    message_id=request.message_id,
                    user_id=request.user_id,
                    sent_at=datetime.utcnow()
                )
            else:
                return PushNotificationResponse(
                    success=False,
                    message_id=request.message_id,
                    user_id=request.user_id,
                    error="FCM_SEND_FAILED"
                )
        
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}", exc_info=True)
            return PushNotificationResponse(
                success=False,
                message_id=request.message_id,
                user_id=request.user_id,
                error=str(e)
            )