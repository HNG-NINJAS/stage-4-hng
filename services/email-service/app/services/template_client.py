"""Template Service HTTP client"""
import logging
import httpx
from typing import Dict, Any, Optional
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TemplateClient:
    """HTTP client for Template Service"""
    
    def __init__(self):
        self.base_url = settings.template_service_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def render_template(
        self,
        template_id: str,
        data: Dict[str, Any],
        language_code: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Render template via Template Service
        
        Args:
            template_id: Template identifier
            data: Data for template rendering
            language_code: Language code
            
        Returns:
            Dict with rendered subject and body, or None if failed
        """
        try:
            url = f"{self.base_url}/api/v1/templates/{template_id}/render"
            payload = {
                "data": data,
                "language_code": language_code
            }
            
            logger.info(f"🔄 Rendering template: {template_id}")
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                rendered_data = result.get("data", {})
                logger.info(f"✅ Template rendered: {template_id}")
                return rendered_data
            else:
                logger.error(f"❌ Template render failed: {result.get('message')}")
                return None
                
        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error rendering template: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Error rendering template: {str(e)}")
            return None
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
