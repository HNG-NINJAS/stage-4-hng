import firebase_admin
from firebase_admin import credentials, messaging
import logging
from typing import Optional, Dict
from app.models import FCMNotification

logger = logging.getLogger(__name__)


class FCMService:
    """Firebase Cloud Messaging service"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize FCM
        
        Args:
            credentials_path: Path to Firebase service account JSON
                             If None, will use mock mode for testing
        """
        self.initialized = False
        self.mock_mode = credentials_path is None
        
        if not self.mock_mode:
            try:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
                self.initialized = True
                logger.info("✅ Firebase FCM initialized")
            except Exception as e:
                logger.error(f"Failed to initialize FCM: {str(e)}")
                logger.warning("Running in MOCK mode")
                self.mock_mode = True
        else:
            logger.warning("⚠️ FCM running in MOCK mode (no credentials)")
    
    async def send_notification(
        self,
        device_token: str,
        notification: FCMNotification
    ) -> bool:
        """
        Send push notification via FCM
        
        Args:
            device_token: FCM device token
            notification: Notification content
            
        Returns:
            True if sent successfully
        """
        if self.mock_mode:
            # Mock mode for testing
            logger.info(f"📱 [MOCK] Sending push notification:")
            logger.info(f"   Token: {device_token[:20]}...")
            logger.info(f"   Title: {notification.title}")
            logger.info(f"   Body: {notification.body[:50]}...")
            return True
        
        try:
            # Build FCM message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.body,
                    image=notification.image
                ),
                data=notification.data or {},
                token=device_token,
                android=messaging.AndroidConfig(
                    priority='high' if notification.click_action else 'normal',
                    notification=messaging.AndroidNotification(
                        click_action=notification.click_action
                    ) if notification.click_action else None
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            badge=1,
                            sound='default'
                        )
                    )
                )
            )
            
            # Send message
            response = messaging.send(message)
            logger.info(f"✅ Push notification sent: {response}")
            return True
        
        except messaging.UnregisteredError:
            logger.warning(f"Invalid device token: {device_token}")
            return False
        
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
    
    async def send_batch(
        self,
        device_tokens: list,
        notification: FCMNotification
    ) -> Dict[str, int]:
        """Send to multiple devices"""
        if self.mock_mode:
            logger.info(f"📱 [MOCK] Sending to {len(device_tokens)} devices")
            return {"success": len(device_tokens), "failure": 0}
        
        try:
            messages = [
                messaging.Message(
                    notification=messaging.Notification(
                        title=notification.title,
                        body=notification.body
                    ),
                    token=token
                )
                for token in device_tokens
            ]
            
            response = messaging.send_all(messages)
            
            return {
                "success": response.success_count,
                "failure": response.failure_count
            }
        
        except Exception as e:
            logger.error(f"Batch send failed: {str(e)}")
            return {"success": 0, "failure": len(device_tokens)}