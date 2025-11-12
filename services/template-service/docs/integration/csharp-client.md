# C#/.NET Client Integration

Complete guide for integrating Template Service with C#/.NET applications.

## Installation

```bash
dotnet add package Microsoft.Extensions.Http
dotnet add package System.Text.Json
```

## Client Implementation

Create `TemplateServiceClient.cs`:

```csharp
using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Logging;

namespace NotificationSystem.Services
{
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
        /// List templates with pagination
        /// </summary>
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

## Dependency Injection Setup

### Program.cs (.NET 6+)

```csharp
using NotificationSystem.Services;

var builder = WebApplication.CreateBuilder(args);

// Add Template Service Client
builder.Services.AddHttpClient<TemplateServiceClient>(client =>
{
    client.BaseAddress = new Uri(
        builder.Configuration["TemplateService:Url"] 
        ?? "http://template-service:3004"
    );
    client.Timeout = TimeSpan.FromSeconds(10);
});

builder.Services.AddControllers();

var app = builder.Build();

app.MapControllers();
app.Run();
```

### appsettings.json

```json
{
  "TemplateService": {
    "Url": "http://template-service:3004"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "NotificationSystem.Services": "Debug"
    }
  }
}
```

## Usage Examples

### Basic Usage

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

    private async Task SendEmailAsync(string to, string subject, string body)
    {
        // Email sending logic
        await Task.CompletedTask;
    }
}
```

### With Fallback Strategy

```csharp
public async Task<bool> SendNotificationWithFallbackAsync(
    string templateId,
    Dictionary<string, object> data)
{
    try
    {
        // Try primary template
        var rendered = await _templateClient.RenderTemplateAsync(templateId, data);

        if (rendered == null)
        {
            // Fallback to generic template
            _logger.LogWarning(
                "Template {TemplateId} failed, using fallback",
                templateId
            );
            rendered = await _templateClient.RenderTemplateAsync(
                "generic_notification",
                data
            );
        }

        if (rendered == null)
        {
            // Last resort: hardcoded message
            _logger.LogError("All templates failed, using hardcoded message");
            rendered = new RenderedTemplate
            {
                Subject = "Notification",
                Body = $"Hello {data.GetValueOrDefault("name", "User")}, " +
                       "you have a notification."
            };
        }

        await SendNotificationAsync(rendered);
        return true;
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Error sending notification");
        return false;
    }
}
```

### ASP.NET Core Controller

```csharp
using Microsoft.AspNetCore.Mvc;
using NotificationSystem.Services;

namespace NotificationSystem.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class NotificationsController : ControllerBase
    {
        private readonly TemplateServiceClient _templateClient;
        private readonly ILogger<NotificationsController> _logger;

        public NotificationsController(
            TemplateServiceClient templateClient,
            ILogger<NotificationsController> logger)
        {
            _templateClient = templateClient;
            _logger = logger;
        }

        [HttpPost("send")]
        public async Task<IActionResult> SendNotification(
            [FromBody] SendNotificationRequest request)
        {
            try
            {
                // Validate template exists
                var template = await _templateClient.GetTemplateAsync(
                    request.TemplateId
                );

                if (template == null)
                {
                    return NotFound(new
                    {
                        success = false,
                        error = "TEMPLATE_NOT_FOUND",
                        message = "Template not found"
                    });
                }

                // Render template
                var rendered = await _templateClient.RenderTemplateAsync(
                    request.TemplateId,
                    request.Data,
                    "en",
                    HttpContext.Request.Headers["X-Correlation-ID"]
                );

                if (rendered == null)
                {
                    return StatusCode(500, new
                    {
                        success = false,
                        error = "RENDER_FAILED",
                        message = "Failed to render template"
                    });
                }

                // Send notification (queue or direct)
                await SendNotificationAsync(rendered);

                return Ok(new
                {
                    success = true,
                    message = "Notification sent",
                    data = new { request.TemplateId }
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing notification");
                return StatusCode(500, new
                {
                    success = false,
                    error = "INTERNAL_ERROR",
                    message = "Failed to process notification"
                });
            }
        }

        [HttpGet("templates/{id}")]
        public async Task<IActionResult> GetTemplate(string id)
        {
            var template = await _templateClient.GetTemplateAsync(id);

            if (template == null)
            {
                return NotFound(new
                {
                    success = false,
                    error = "TEMPLATE_NOT_FOUND",
                    message = "Template not found"
                });
            }

            return Ok(new
            {
                success = true,
                data = template
            });
        }

        [HttpGet("health")]
        public async Task<IActionResult> HealthCheck()
        {
            var templateHealthy = await _templateClient.HealthCheckAsync();

            return Ok(new
            {
                status = templateHealthy ? "healthy" : "degraded",
                services = new
                {
                    api = "up",
                    template_service = templateHealthy ? "up" : "down"
                }
            });
        }

        private async Task SendNotificationAsync(RenderedTemplate rendered)
        {
            // Notification sending logic
            await Task.CompletedTask;
        }
    }

    public class SendNotificationRequest
    {
        public string TemplateId { get; set; } = "";
        public Dictionary<string, object> Data { get; set; } = new();
    }
}
```

## Testing

### Unit Tests (xUnit)

```csharp
using Xunit;
using Moq;
using Moq.Protected;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using NotificationSystem.Services;

public class TemplateServiceClientTests
{
    [Fact]
    public async Task RenderTemplate_Success_ReturnsRenderedTemplate()
    {
        // Arrange
        var mockResponse = new
        {
            success = true,
            data = new
            {
                subject = "Welcome John!",
                body = "Hi John!",
                variables_used = new[] { "name" }
            }
        };

        var mockHttpMessageHandler = new Mock<HttpMessageHandler>();
        mockHttpMessageHandler
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>()
            )
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK,
                Content = JsonContent.Create(mockResponse)
            });

        var httpClient = new HttpClient(mockHttpMessageHandler.Object)
        {
            BaseAddress = new Uri("http://localhost:3004")
        };

        var logger = Mock.Of<ILogger<TemplateServiceClient>>();
        var client = new TemplateServiceClient(httpClient, logger);

        // Act
        var result = await client.RenderTemplateAsync(
            "welcome_email",
            new Dictionary<string, object> { { "name", "John" } }
        );

        // Assert
        Assert.NotNull(result);
        Assert.Equal("Welcome John!", result.Subject);
    }

    [Fact]
    public async Task RenderTemplate_NotFound_ReturnsNull()
    {
        // Arrange
        var mockResponse = new
        {
            success = false,
            error = "TEMPLATE_NOT_FOUND"
        };

        var mockHttpMessageHandler = new Mock<HttpMessageHandler>();
        mockHttpMessageHandler
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>()
            )
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.NotFound,
                Content = JsonContent.Create(mockResponse)
            });

        var httpClient = new HttpClient(mockHttpMessageHandler.Object)
        {
            BaseAddress = new Uri("http://localhost:3004")
        };

        var logger = Mock.Of<ILogger<TemplateServiceClient>>();
        var client = new TemplateServiceClient(httpClient, logger);

        // Act
        var result = await client.RenderTemplateAsync(
            "invalid_template",
            new Dictionary<string, object> { { "name", "John" } }
        );

        // Assert
        Assert.Null(result);
    }
}
```

### Integration Tests

```csharp
using Xunit;
using Microsoft.Extensions.DependencyInjection;
using NotificationSystem.Services;

public class TemplateServiceIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly TemplateServiceClient _client;

    public TemplateServiceIntegrationTests()
    {
        var services = new ServiceCollection();
        services.AddHttpClient<TemplateServiceClient>(client =>
        {
            client.BaseAddress = new Uri("http://localhost:3004");
        });
        services.AddLogging();

        var serviceProvider = services.BuildServiceProvider();
        _client = serviceProvider.GetRequiredService<TemplateServiceClient>();
    }

    [Fact]
    public async Task RenderTemplate_Integration_Success()
    {
        // Act
        var result = await _client.RenderTemplateAsync(
            "welcome_email",
            new Dictionary<string, object>
            {
                { "name", "Test User" },
                { "company_name", "Test Corp" },
                { "verification_link", "https://example.com/verify/123" }
            }
        );

        // Assert
        Assert.NotNull(result);
        Assert.Contains("Test User", result.Body);
    }

    [Fact]
    public async Task HealthCheck_Integration_Success()
    {
        // Act
        var isHealthy = await _client.HealthCheckAsync();

        // Assert
        Assert.True(isHealthy);
    }
}
```

## Best Practices

1. **Use dependency injection** for better testability
2. **Implement retry logic** with Polly library
3. **Always include correlation IDs** for distributed tracing
4. **Handle exceptions gracefully** with fallback strategies
5. **Cache template metadata** to reduce API calls
6. **Monitor health checks** regularly
7. **Use strongly-typed models** for type safety
8. **Log all operations** with structured logging

## Next Steps

- Review [API Reference](../api-reference.md)
- Explore [Event Integration](./events.md)
- Set up [Monitoring](../operations/monitoring.md)
