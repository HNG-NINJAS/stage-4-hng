## Language-Specific Examples

### Python Integration (for Email/Push Services)

#### Complete Client Implementation

Create a file: `template_client.py`
```python
"""
Template Service Client for Python services
Usage: from template_client import TemplateClient
"""

import httpx
from typing import Dict, Any, Optional, List
import logging

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
        """
        Initialize Template Service client
        
        Args:
            base_url: Template service URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={"Content-Type": "application/json"}
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
            Dictionary with 'subject', 'body', 'variables_used'
            or None if failed
        
        Example:
            rendered = await client.render_template(
                template_id="welcome_email",
                data={
                    "name": "John Doe",
                    "company_name": "Acme Corp",
                    "verification_link": "https://example.com/verify/123"
                },
                correlation_id="user-signup-123"
            )
            
            if rendered:
                print(f"Subject: {rendered['subject']}")
                print(f"Body: {rendered['body']}")
        """
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
            return None
        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            return None
    
    async def get_template(
        self, 
        template_id: str,
        correlation_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get template metadata
        
        Args:
            template_id: Template identifier
            correlation_id: For distributed tracing
            
        Returns:
            Template details or None if not found
        """
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
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        List templates with pagination and filters
        
        Args:
            page: Page number
            limit: Items per page
            template_type: Filter by type (email, push, sms)
            category: Filter by category
            search: Search term
            
        Returns:
            Dictionary with 'templates' list and 'meta' pagination info
        """
        params = {"page": page, "limit": limit}
        if template_type:
            params["type"] = template_type
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        
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
        """
        Check if Template Service is healthy
        
        Returns:
            True if service is healthy
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200 and response.json().get("success")
        except Exception:
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Usage Example in Email Service
async def send_welcome_email(user_id: str, user_email: str, user_name: str):
    """Example: Send welcome email using Template Service"""
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
            # Send email with rendered content
            await send_email_via_smtp(
                to=user_email,
                subject=rendered["subject"],
                body=rendered["body"]
            )
            logger.info(f"✅ Welcome email sent to {user_email}")
            return True
        else:
            logger.error(f"❌ Failed to render welcome template")
            return False
    
    finally:
        await client.close()


# Example with fallback template
async def send_notification_with_fallback(
    user_id: str,
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
            rendered = await client.render_template(
                "generic_notification",
                data
            )
        
        if rendered:
            # Send notification
            await send_notification(rendered["subject"], rendered["body"])
            return True
        else:
            # Last resort: hardcoded message
            logger.error("All templates failed, using hardcoded message")
            await send_notification(
                "Notification",
                f"Hello {data.get('name', 'User')}, you have a new notification."
            )
            return True
    
    finally:
        await client.close()
```

---

### Node.js/TypeScript Integration (for API Gateway)

#### Complete Client Implementation

Create a file: `templateClient.ts`
```typescript
/**
 * Template Service Client for Node.js/TypeScript services
 * Usage: import { TemplateServiceClient } from './templateClient';
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

interface RenderData {
  [key: string]: any;
}

interface RenderedTemplate {
  subject: string | null;
  body: string;
  variables_used: string[];
}

interface Template {
  id: string;
  template_id: string;
  name: string;
  type: string;
  description?: string;
  category?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  current_version?: {
    version: string;
    subject?: string;
    body: string;
    variables: string[];
  };
}

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message: string;
  meta: {
    total: number;
    limit: number;
    page: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
}

interface ListTemplatesResponse {
  templates: Template[];
  meta: {
    total: number;
    limit: number;
    page: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
}

export class TemplateServiceClient {
  private client: AxiosInstance;

  /**
   * Initialize Template Service client
   * 
   * @param baseURL - Template service URL (default: http://template-service:3004)
   * @param timeout - Request timeout in milliseconds (default: 10000)
   */
  constructor(
    baseURL: string = 'http://template-service:3004',
    timeout: number = 10000
  ) {
    this.client = axios.create({
      baseURL,
      timeout,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  /**
   * Render a template with data
   * 
   * @param templateId - Template identifier (e.g., 'welcome_email')
   * @param data - Variables to substitute
   * @param languageCode - Language for translation (default: 'en')
   * @param correlationId - For distributed tracing
   * @returns Rendered template or null if failed
   * 
   * @example
   * const rendered = await client.renderTemplate('welcome_email', {
   *   name: 'John Doe',
   *   company_name: 'Acme Corp',
   *   verification_link: 'https://example.com/verify/123'
   * });
   */
  async renderTemplate(
    templateId: string,
    data: RenderData,
    languageCode: string = 'en',
    correlationId?: string
  ): Promise<RenderedTemplate | null> {
    try {
      const headers: any = {};
      if (correlationId) {
        headers['X-Correlation-ID'] = correlationId;
      }

      const response = await this.client.post<ApiResponse<RenderedTemplate>>(
        `/api/v1/templates/${templateId}/render`,
        { data, language_code: languageCode },
        { headers }
      );

      if (response.data.success && response.data.data) {
        console.log(`✅ Template '${templateId}' rendered successfully`);
        return response.data.data;
      } else {
        console.error(`❌ Template render failed: ${response.data.error}`);
        return null;
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error(`Error rendering template: ${error.message}`);
      } else {
        console.error('Error rendering template:', error);
      }
      return null;
    }
  }

  /**
   * Get template metadata
   * 
   * @param templateId - Template identifier
   * @param correlationId - For distributed tracing
   * @returns Template details or null if not found
   */
  async getTemplate(
    templateId: string,
    correlationId?: string
  ): Promise<Template | null> {
    try {
      const headers: any = {};
      if (correlationId) {
        headers['X-Correlation-ID'] = correlationId;
      }

      const response = await this.client.get<ApiResponse<Template>>(
        `/api/v1/templates/${templateId}`,
        { headers }
      );

      return response.data.success && response.data.data 
        ? response.data.data 
        : null;
    } catch (error) {
      console.error('Error getting template:', error);
      return null;
    }
  }

  /**
   * List templates with pagination and filters
   * 
   * @param page - Page number (default: 1)
   * @param limit - Items per page (default: 10)
   * @param type - Filter by type (email, push, sms)
   * @param category - Filter by category
   * @param search - Search term
   * @returns Templates list with pagination or null if failed
   */
  async listTemplates(
    page: number = 1,
    limit: number = 10,
    type?: string,
    category?: string,
    search?: string
  ): Promise<ListTemplatesResponse | null> {
    try {
      const params: any = { page, limit };
      if (type) params.type = type;
      if (category) params.category = category;
      if (search) params.search = search;

      const response = await this.client.get<ApiResponse<Template[]>>(
        '/api/v1/templates',
        { params }
      );

      if (response.data.success && response.data.data) {
        return {
          templates: response.data.data,
          meta: response.data.meta
        };
      }
      return null;
    } catch (error) {
      console.error('Error listing templates:', error);
      return null;
    }
  }

  /**
   * Check service health
   * 
   * @returns True if service is healthy
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200 && response.data.success === true;
    } catch (error) {
      return false;
    }
  }
}

// Usage Example in API Gateway
const templateService = new TemplateServiceClient();

// Express.js endpoint example
app.post('/api/notifications/send', async (req, res) => {
  const { userId, templateId, data, type } = req.body;

  try {
    // Validate template exists
    const template = await templateService.getTemplate(templateId);
    
    if (!template) {
      return res.status(404).json({
        success: false,
        error: 'TEMPLATE_NOT_FOUND',
        message: 'Template not found'
      });
    }

    // Publish to queue for async processing
    await publishToQueue('notifications', {
      userId,
      templateId,
      data,
      type,
      correlationId: req.headers['x-correlation-id']
    });

    res.json({
      success: true,
      message: 'Notification queued',
      data: { templateId, userId }
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Failed to process notification'
    });
  }
});

// Health check aggregation
app.get('/health', async (req, res) => {
  const templateServiceHealthy = await templateService.healthCheck();
  
  res.json({
    status: templateServiceHealthy ? 'healthy' : 'degraded',
    services: {
      'api-gateway': 'up',
      'template-service': templateServiceHealthy ? 'up' : 'down'
    }
  });
});
```

---

### C# (.NET) Integration (for User Service)

#### Complete Client Implementation

Create a file: `TemplateServiceClient.cs`
```csharp
using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Logging;

namespace NotificationSystem.Services
{
    /// <summary>
    /// Client for Template Service integration
    /// </summary>
    public class TemplateServiceClient
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<TemplateServiceClient> _logger;

        public TemplateServiceClient(
            HttpClient httpClient,
            ILogger<TemplateServiceClient> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
        }

        /// <summary>
        /// Render a template with provided data
        /// </summary>
        /// <param name="templateId">Template identifier (e.g., 'welcome_email')</param>
        /// <param name="data">Variables to substitute</param>
        /// <param name="languageCode">Language for translation (default: 'en')</param>
        /// <param name="correlationId">For distributed tracing</param>
        /// <returns>Rendered template or null if failed</returns>
        /// <example>
        /// var rendered = await client.RenderTemplateAsync(
        ///     "welcome_email",
        ///     new Dictionary&lt;string, object&gt; {
        ///         { "name", "John Doe" },
        ///         { "company_name", "Acme Corp" }
        ///     }
        /// );
        /// </example>
        public async Task<RenderedTemplate?> RenderTemplateAsync(
            string templateId,
            Dictionary<string, object> data,
            string languageCode = "en",
            string? correlationId = null)
        {
            try
            {
                var payload = new
                {
                    data = data,
                    language_code = languageCode
                };

                var request = new HttpRequestMessage(
                    HttpMethod.Post,
                    $"/api/v1/templates/{templateId}/render")
                {
                    Content = JsonContent.Create(payload)
                };

                if (!string.IsNullOrEmpty(correlationId))
                {
                    request.Headers.Add("X-Correlation-ID", correlationId);
                }

                var response = await _httpClient.SendAsync(request);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content
                        .ReadFromJsonAsync<ApiResponse<RenderedTemplate>>();

                    if (result?.Success == true && result.Data != null)
                    {
                        _logger.LogInformation(
                            "Template '{TemplateId}' rendered successfully",
                            templateId
                        );
                        return result.Data;
                    }
                    else
                    {
                        _logger.LogError(
                            "Template render failed: {Error}",
                            result?.Error
                        );
                        return null;
                    }
                }

                _logger.LogError(
                    "HTTP {StatusCode} from template service",
                    response.StatusCode
                );
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(
                    ex,
                    "Error rendering template '{TemplateId}'",
                    templateId
                );
                return null;
            }
        }

        /// <summary>
        /// Get template metadata
        /// </summary>
        /// <param name="templateId">Template identifier</param>
        /// <param name="correlationId">For distributed tracing</param>
        /// <returns>Template details or null if not found</returns>
        public async Task<Template?> GetTemplateAsync(
            string templateId,
            string? correlationId = null)
        {
            try
            {
                var request = new HttpRequestMessage(
                    HttpMethod.Get,
                    $"/api/v1/templates/{templateId}");

                if (!string.IsNullOrEmpty(correlationId))
                {
                    request.Headers.Add("X-Correlation-ID", correlationId);
                }

                var response = await _httpClient.SendAsync(request);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content
                        .ReadFromJsonAsync<ApiResponse<Template>>();

                    return result?.Success == true ? result.Data : null;
                }

                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(
                    ex,
                    "Error getting template '{TemplateId}'",
                    templateId
                );
                return null;
            }
        }

        /// <summary>
        /// List templates with pagination and filters
        /// </summary>
        /// <param name="page">Page number (default: 1)</param>
        /// <param name="limit">Items per page (default: 10)</param>
        /// <param name="type">Filter by type (email, push, sms)</param>
        /// <param name="category">Filter by category</param>
        /// <returns>List of templates with pagination or null if failed</returns>
        public async Task<ListTemplatesResponse?> ListTemplatesAsync(
            int page = 1,
            int limit = 10,
            string? type = null,
            string? category = null)
        {
            try
            {
                var queryParams = new List<string>
                {
                    $"page={page}",
                    $"limit={limit}"
                };

                if (!string.IsNullOrEmpty(type))
                    queryParams.Add($"type={type}");
                
                if (!string.IsNullOrEmpty(category))
                    queryParams.Add($"category={category}");

                var query = string.Join("&", queryParams);
                var response = await _httpClient.GetAsync(
                    $"/api/v1/templates?{query}"
                );

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content
                        .ReadFromJsonAsync<ApiResponse<List<Template>>>();

                    if (result?.Success == true && result.Data != null)
                    {
                        return new ListTemplatesResponse
                        {
                            Templates = result.Data,
                            Meta = result.Meta
                        };
                    }
                }

                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error listing templates");
                return null;
            }
        }

        /// <summary>
        /// Check if Template Service is healthy
        /// </summary>
        /// <returns>True if service is healthy</returns>
        public async Task<bool> HealthCheckAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/health");
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }
    }

    #region Models

    public class RenderedTemplate
    {
        [JsonPropertyName("subject")]
        public string? Subject { get; set; }

        [JsonPropertyName("body")]
        public string Body { get; set; } = "";

        [JsonPropertyName("variables_used")]
        public List<string> VariablesUsed { get; set; } = new();
    }

    public class Template
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = "";

        [JsonPropertyName("template_id")]
        public string TemplateId { get; set; } = "";

        [JsonPropertyName("name")]
        public string Name { get; set; } = "";

        [JsonPropertyName("type")]
        public string Type { get; set; } = "";

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("category")]
        public string? Category { get; set; }

        [JsonPropertyName("is_active")]
        public bool IsActive { get; set; }

        [JsonPropertyName("current_version")]
        public TemplateVersion? CurrentVersion { get; set; }
    }

    public class TemplateVersion
    {
        [JsonPropertyName("version")]
        public string Version { get; set; } = "";

        [JsonPropertyName("subject")]
        public string? Subject { get; set; }

        [JsonPropertyName("body")]
        public string Body { get; set; } = "";

        [JsonPropertyName("variables")]
        public List<string> Variables { get; set; } = new();
    }

    public class ApiResponse<T>
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("data")]
        public T? Data { get; set; }

        [JsonPropertyName("error")]
        public string? Error { get; set; }

        [JsonPropertyName("message")]
        public string Message { get; set; } = "";

        [JsonPropertyName("meta")]
        public PaginationMeta Meta { get; set; } = new();
    }

    public class PaginationMeta
    {
        [JsonPropertyName("total")]
        public int Total { get; set; }

        [JsonPropertyName("limit")]
        public int Limit { get; set; }

        [JsonPropertyName("page")]
        public int Page { get; set; }

        [JsonPropertyName("total_pages")]
        public int TotalPages { get; set; }

        [JsonPropertyName("has_next")]
        public bool HasNext { get; set; }

        [JsonPropertyName("has_previous")]
        public bool HasPrevious { get; set; }
    }

    public class ListTemplatesResponse
    {
        public List<Template> Templates { get; set; } = new();
        public PaginationMeta Meta { get; set; } = new();
    }

    #endregion
}
```

**Dependency Injection Setup (Program.cs or Startup.cs):**
```csharp
// Add in Program.cs or Startup.cs
services.AddHttpClient<TemplateServiceClient>(client =>
{
    client.BaseAddress = new Uri("http://template-service:3004");
    client.Timeout = TimeSpan.FromSeconds(10);
});
```

**Usage Example:**
```csharp
public class NotificationService
{
    private readonly TemplateServiceClient _templateClient;
    private readonly ILogger<NotificationService> _logger;

    public NotificationService(
        TemplateServiceClient templateClient,
        ILogger<NotificationService> logger)
    {
        _templateClient = templateClient;
        _logger = logger;
    }

    public async Task<bool> SendWelcomeEmailAsync(
        string userId,
        string userEmail,
        string userName)
    {
        try
        {
            // Render template
            var rendered = await _templateClient.RenderTemplateAsync(
                "welcome_email",
                new Dictionary<string, object>
                {
                    { "name", userName },
                    { "company_name", "Acme Corp" },
                    { "verification_link", $"https://example.com/verify/{userId}" }
                },
                "en",
                $"welcome-{userId}"
            );

            if (rendered != null)
            {
                // Send email
                await SendEmailAsync(
                    userEmail,
                    rendered.Subject ?? "Welcome",
                    rendered.Body
                );

                _logger.LogInformation(
                    "Welcome email sent to {Email}",
                    userEmail
                );
                return true;
            }

            _logger.LogError("Failed to render welcome template");
            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error sending welcome email");
            return false;
        }
    }
}
```

---

[← Previous](./INTEGRATION.md)