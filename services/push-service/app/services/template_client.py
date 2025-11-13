import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TemplateClient:
    """Client for Template Service"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def render_template(
        self,
        template_id: str,
        data: Dict[str, Any],
        language_code: str = "en",
        correlation_id: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """Render template"""
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/templates/{template_id}/render",
                json={
                    "data": data,
                    "language_code": language_code
                },
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    return result["data"]
            
            logger.error(f"Template render failed: {response.text}")
            return None
        
        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            return None
    
    async def close(self):
        await self.client.aclose()