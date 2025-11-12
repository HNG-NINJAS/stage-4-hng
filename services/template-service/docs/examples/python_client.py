"""
Python client example for Template Service integration
"""
import requests
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TemplateServiceClient:
    """Client for interacting with Template Service"""
    
    def __init__(self, base_url: str = "http://template-service:3004"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def render_template(
        self, 
        template_id: str, 
        data: Dict, 
        language_code: str = "en"
    ) -> Dict:
        """
        Render a template with provided data
        
        Args:
            template_id: Template identifier
            data: Variables to substitute in template
            language_code: Language code (default: "en")
            
        Returns:
            Rendered template with subject and body
            
        Raises:
            requests.HTTPError: If request fails
            ValueError: If template render fails
        """
        try:
            response = self.session.post(
                f"{self.api_url}/templates/{template_id}/render",
                json={"data": data, "language_code": language_code}
            )
            response.raise_for_status()
            result = response.json()
            
            if not result["success"]:
                raise ValueError(f"Template render failed: {result.get('error')}")
            
            return result["data"]
            
        except requests.RequestException as e:
            logger.error(f"Failed to render template {template_id}: {e}")
            raise
    
    def get_template(self, template_id: str) -> Dict:
        """Get template details"""
        response = self.session.get(f"{self.api_url}/templates/{template_id}")
        response.raise_for_status()
        result = response.json()
        
        if not result["success"]:
            raise ValueError(f"Template not found: {template_id}")
        
        return result["data"]
    
    def list_templates(
        self, 
        page: int = 1, 
        limit: int = 10,
        template_type: Optional[str] = None
    ) -> Dict:
        """List templates with pagination"""
        params = {"page": page, "limit": limit}
        if template_type:
            params["type"] = template_type
        
        response = self.session.get(f"{self.api_url}/templates", params=params)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> bool:
        """Check if service is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            health = response.json()
            return health["data"]["status"] == "healthy"
        except:
            return False


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = TemplateServiceClient("http://localhost:3004")
    
    # Check health
    if not client.health_check():
        print("Template service is not healthy!")
        exit(1)
    
    # Render welcome email
    rendered = client.render_template(
        "welcome_email",
        {
            "name": "John Doe",
            "company_name": "Acme Corp",
            "verification_link": "https://example.com/verify/abc123"
        }
    )
    
    print("Subject:", rendered["subject"])
    print("Body:", rendered["body"])
    print("Variables used:", rendered["variables_used"])
    
    # Render in Spanish
    rendered_es = client.render_template(
        "welcome_email",
        {
            "name": "Juan Pérez",
            "company_name": "Acme Corp",
            "verification_link": "https://example.com/verify/xyz789"
        },
        language_code="es"
    )
    
    print("\nSpanish version:")
    print("Subject:", rendered_es["subject"])
    print("Body:", rendered_es["body"])
