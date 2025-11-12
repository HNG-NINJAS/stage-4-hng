# Python Client Integration

Complete guide for integrating Template Service with Python/FastAPI applications.

## Installation

```bash
pip install httpx tenacity pybreaker
```

## Client Implementation

Create `template_client.py`:

```python
"""
Template Service Client for Python
"""

import httpx
from typing import Dict, Any, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class TemplateClient:
    """
    Client for Template Service integration
    
    Example:
        client = TemplateClient(base_url="http://template-service:3004")
        rendered = await client.render_template("welcome_email", {"name": "John"})
    """
    
    def __init__(
        self, 
        base_url: str = "http://template-service:3004",
        timeout: float = 10.0
    ):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def render_template(
        self,
        template_id: str,
        data: Dict[str, Any],
        language_code: str = "en",
        correlation_id: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Render a template with provided data
        
        Args:
            template_id: Template identifier (e.g., 'welcome_email')
            data: Variables to substitute
            language_code: Language for translation (default: 'en')
            correlation_id: For distributed tracing
            
        Returns:
            Dictionary with 'subject', 'body', 'variables_used' or None if failed
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/templates/{template_id}/render",
                json={"data": data, "language_code": language_code},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    logger.info(f"Template '{template_id}' rendered successfully")
                    return result["data"]
                else:
                    logger.error(f"Template render failed: {result.get('error')}")
                    return None
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return None
        
        except httpx.TimeoutException:
            logger.error(f"Timeout rendering template '{template_id}'")
            raise
        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            raise
    
    async def get_template(
        self, 
        template_id: str,
        correlation_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Get template metadata"""
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/templates/{template_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["data"] if result["success"] else None
            
            return None
        except Exception as e:
            logger.error(f"Error getting template: {str(e)}")
            return None
    
    async def list_templates(
        self,
        page: int = 1,
        limit: int = 10,
        template_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """List templates with pagination"""
        params = {"page": page, "limit": limit}
        if template_type:
            params["type"] = template_type
        if category:
            params["category"] = category
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/templates",
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    return {
                        "templates": result["data"],
                        "meta": result["meta"]
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return None
    
    async def health_check(self) -> bool:
        """Check if Template Service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200 and response.json().get("success")
        except Exception:
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
```

## Usage Examples

### Basic Usage

```python
from template_client import TemplateClient

async def send_welcome_email(user_id: str, user_email: str, user_name: str):
    """Send welcome email using Template Service"""
    client = TemplateClient()
    
    try:
        # Render template
        rendered = await client.render_template(
            template_id="welcome_email",
            data={
                "name": user_name,
                "company_name": "Acme Corp",
                "verification_link": f"https://example.com/verify/{user_id}"
            },
            correlation_id=f"welcome-{user_id}"
        )
        
        if rendered:
            # Send email
            await send_email_via_smtp(
                to=user_email,
                subject=rendered["subject"],
                body=rendered["body"]
            )
            logger.info(f"Welcome email sent to {user_email}")
            return True
        else:
            logger.error("Failed to render welcome template")
            return False
    
    finally:
        await client.close()
```

### With Fallback Strategy

```python
async def send_notification_with_fallback(
    template_id: str,
    data: Dict[str, Any]
):
    """Send notification with fallback to generic template"""
    client = TemplateClient()
    
    try:
        # Try primary template
        rendered = await client.render_template(template_id, data)
        
        if not rendered:
            # Fallback to generic template
            logger.warning(f"Template {template_id} failed, using fallback")
            rendered = await client.render_template("generic_notification", data)
        
        if not rendered:
            # Last resort: hardcoded message
            logger.error("All templates failed, using hardcoded message")
            rendered = {
                "subject": "Notification",
                "body": f"Hello {data.get('name', 'User')}, you have a notification."
            }
        
        await send_notification(rendered["subject"], rendered["body"])
        return True
    
    finally:
        await client.close()
```

### With Circuit Breaker

```python
from pybreaker import CircuitBreaker

template_breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60
)

@template_breaker
async def render_template_protected(
    client: TemplateClient,
    template_id: str,
    data: Dict[str, Any]
):
    """Render with circuit breaker protection"""
    return await client.render_template(template_id, data)
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from template_client import TemplateClient

app = FastAPI()

# Dependency
async def get_template_client():
    client = TemplateClient()
    try:
        yield client
    finally:
        await client.close()

@app.post("/notifications/send")
async def send_notification(
    template_id: str,
    data: dict,
    client: TemplateClient = Depends(get_template_client)
):
    """Send notification endpoint"""
    rendered = await client.render_template(template_id, data)
    
    if not rendered:
        raise HTTPException(status_code=500, detail="Failed to render template")
    
    # Send notification
    await send_notification_service(rendered)
    
    return {"success": True, "message": "Notification sent"}

@app.get("/health")
async def health_check(client: TemplateClient = Depends(get_template_client)):
    """Health check with dependency status"""
    template_healthy = await client.health_check()
    
    return {
        "status": "healthy" if template_healthy else "degraded",
        "dependencies": {
            "template_service": "up" if template_healthy else "down"
        }
    }
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch
from template_client import TemplateClient

@pytest.mark.asyncio
async def test_render_template_success():
    """Test successful template rendering"""
    mock_response = {
        "success": True,
        "data": {
            "subject": "Welcome John!",
            "body": "Hi John, welcome!",
            "variables_used": ["name"]
        }
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        client = TemplateClient()
        result = await client.render_template("welcome_email", {"name": "John"})
        
        assert result is not None
        assert result["subject"] == "Welcome John!"
        await client.close()

@pytest.mark.asyncio
async def test_render_template_not_found():
    """Test template not found"""
    mock_response = {
        "success": False,
        "error": "TEMPLATE_NOT_FOUND",
        "message": "Template not found"
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 404
        mock_post.return_value.json.return_value = mock_response
        
        client = TemplateClient()
        result = await client.render_template("invalid_template", {"name": "John"})
        
        assert result is None
        await client.close()

@pytest.mark.asyncio
async def test_health_check():
    """Test health check"""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"success": True}
        
        client = TemplateClient()
        is_healthy = await client.health_check()
        
        assert is_healthy is True
        await client.close()
```

### Integration Tests

```python
import pytest
from template_client import TemplateClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_render_template_integration():
    """Integration test with real Template Service"""
    client = TemplateClient(base_url="http://localhost:3004")
    
    try:
        rendered = await client.render_template(
            template_id="welcome_email",
            data={
                "name": "Test User",
                "company_name": "Test Corp",
                "verification_link": "https://example.com/verify/123"
            }
        )
        
        assert rendered is not None
        assert "subject" in rendered
        assert "body" in rendered
        assert "Test User" in rendered["body"]
    
    finally:
        await client.close()
```

## Best Practices

1. **Always use correlation IDs** for distributed tracing
2. **Implement retry logic** with exponential backoff
3. **Use circuit breakers** to prevent cascading failures
4. **Cache template metadata** to reduce API calls
5. **Implement fallback strategies** for critical paths
6. **Close clients properly** to avoid resource leaks
7. **Log all operations** with appropriate context
8. **Monitor health checks** regularly

## Next Steps

- Review [API Reference](../api-reference.md)
- Explore [Event Integration](./events.md)
- Set up [Monitoring](../operations/monitoring.md)
