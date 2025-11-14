"""Email service - Mock implementation"""
import logging
from typing import Dict, Any
from app.config import get_settings
from app.services.template_client import TemplateClient

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Mock email service that logs instead of sending"""
    
    def __init__(self):
        self.template_client = TemplateClient()
        self.mock_mode = settings.mock_mode
    
    async def send_email(
        self,
        message_id: str,
        correlation_id: str,
        user_id: str,
        template_id: str,
        template_data: Dict[str, Any],
        recipient_email: str,
        language_code: str = "en"
    ) -> bool:
        """
        Send email notification (mock mode - just logs)
        
        Args:
            message_id: Unique message ID
            correlation_id: Correlation ID for tracing
            user_id: User ID
            template_id: Template identifier
            template_data: Data for template rendering
            recipient_email: Recipient email address
            language_code: Language code for template
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(
                f"📥 Processing email notification",
                extra={
                    "message_id": message_id,
                    "correlation_id": correlation_id,
                    "user_id": user_id,
                    "template_id": template_id,
                    "recipient": recipient_email
                }
            )
            
            # Fetch and render template
            rendered = await self.template_client.render_template(
                template_id=template_id,
                data=template_data,
                language_code=language_code
            )
            
            if not rendered:
                logger.error(f"❌ Failed to render template: {template_id}")
                return False
            
            # Mock email sending - just log the content
            if self.mock_mode:
                logger.info("=" * 60)
                logger.info("📧 [MOCK] Sending Email:")
                logger.info(f"   To: {recipient_email}")
                logger.info(f"   Subject: {rendered['subject']}")
                logger.info(f"   Body Preview: {rendered['body'][:100]}...")
                logger.info(f"   Template: {template_id}")
                logger.info(f"   Language: {language_code}")
                logger.info(f"   Message ID: {message_id}")
                logger.info(f"   Correlation ID: {correlation_id}")
                logger.info("=" * 60)
            else:
                # In real mode, you would send actual email here
                # e.g., using SMTP, SendGrid, AWS SES, etc.
                logger.info(f"📧 Sending real email to {recipient_email}")
            
            logger.info(
                f"✅ Email sent successfully to {recipient_email}",
                extra={
                    "message_id": message_id,
                    "correlation_id": correlation_id,
                    "user_id": user_id
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"❌ Failed to send email: {str(e)}",
                extra={
                    "message_id": message_id,
                    "correlation_id": correlation_id,
                    "error": str(e)
                },
                exc_info=True
            )
            return False
