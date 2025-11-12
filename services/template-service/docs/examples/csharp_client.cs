/**
 * C# client example for Template Service integration
 */
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;

namespace TemplateService.Client
{
    public class TemplateServiceClient
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiUrl;

        public TemplateServiceClient(string baseUrl = "http://template-service:3004")
        {
            _httpClient = new HttpClient();
            _apiUrl = $"{baseUrl}/api/v1";
        }

        /// <summary>
        /// Render a template with provided data
        /// </summary>
        public async Task<RenderedTemplate> RenderTemplateAsync(
            string templateId, 
            Dictionary<string, object> data, 
            string languageCode = "en")
        {
            try
            {
                var payload = new
                {
                    data = data,
                    language_code = languageCode
                };

                var response = await _httpClient.PostAsJsonAsync(
                    $"{_apiUrl}/templates/{templateId}/render",
                    payload
                );

                response.EnsureSuccessStatusCode();
                var result = await response.Content.ReadFromJsonAsync<ApiResponse<RenderedTemplate>>();

                if (!result.Success)
                {
                    throw new Exception($"Template render failed: {result.Error}");
                }

                return result.Data;
            }
            catch (HttpRequestException ex)
            {
                Console.WriteLine($"Failed to render template {templateId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get template details
        /// </summary>
        public async Task<Template> GetTemplateAsync(string templateId)
        {
            var response = await _httpClient.GetAsync($"{_apiUrl}/templates/{templateId}");
            response.EnsureSuccessStatusCode();
            
            var result = await response.Content.ReadFromJsonAsync<ApiResponse<Template>>();
            
            if (!result.Success)
            {
                throw new Exception($"Template not found: {templateId}");
            }
            
            return result.Data;
        }

        /// <summary>
        /// List templates with pagination
        /// </summary>
        public async Task<PaginatedResponse<Template>> ListTemplatesAsync(
            int page = 1, 
            int limit = 10, 
            string type = null)
        {
            var queryParams = $"?page={page}&limit={limit}";
            if (!string.IsNullOrEmpty(type))
            {
                queryParams += $"&type={type}";
            }

            var response = await _httpClient.GetAsync($"{_apiUrl}/templates{queryParams}");
            response.EnsureSuccessStatusCode();
            
            return await response.Content.ReadFromJsonAsync<PaginatedResponse<Template>>();
        }

        /// <summary>
        /// Check if service is healthy
        /// </summary>
        public async Task<bool> HealthCheckAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_apiUrl.Replace("/api/v1", "")}/health");
                var health = await response.Content.ReadFromJsonAsync<ApiResponse<HealthStatus>>();
                return health.Data.Status == "healthy";
            }
            catch
            {
                return false;
            }
        }
    }

    // Data models
    public class ApiResponse<T>
    {
        public bool Success { get; set; }
        public T Data { get; set; }
        public string Error { get; set; }
        public string Message { get; set; }
    }

    public class PaginatedResponse<T> : ApiResponse<List<T>>
    {
        public PaginationMeta Meta { get; set; }
    }

    public class PaginationMeta
    {
        public int Total { get; set; }
        public int Limit { get; set; }
        public int Page { get; set; }
        public int TotalPages { get; set; }
        public bool HasNext { get; set; }
        public bool HasPrevious { get; set; }
    }

    public class RenderedTemplate
    {
        public string Subject { get; set; }
        public string Body { get; set; }
        public List<string> VariablesUsed { get; set; }
    }

    public class Template
    {
        public string Id { get; set; }
        public string TemplateId { get; set; }
        public string Name { get; set; }
        public string Type { get; set; }
        public string Description { get; set; }
        public bool IsActive { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }
    }

    public class HealthStatus
    {
        public string Status { get; set; }
        public DateTime Timestamp { get; set; }
        public string Version { get; set; }
    }

    // Example usage
    class Program
    {
        static async Task Main(string[] args)
        {
            // Initialize client
            var client = new TemplateServiceClient("http://localhost:3004");

            // Check health
            var isHealthy = await client.HealthCheckAsync();
            if (!isHealthy)
            {
                Console.WriteLine("Template service is not healthy!");
                return;
            }

            // Render welcome email
            var rendered = await client.RenderTemplateAsync(
                "welcome_email",
                new Dictionary<string, object>
                {
                    ["name"] = "John Doe",
                    ["company_name"] = "Acme Corp",
                    ["verification_link"] = "https://example.com/verify/abc123"
                }
            );

            Console.WriteLine($"Subject: {rendered.Subject}");
            Console.WriteLine($"Body: {rendered.Body}");
            Console.WriteLine($"Variables used: {string.Join(", ", rendered.VariablesUsed)}");

            // Render in Spanish
            var renderedEs = await client.RenderTemplateAsync(
                "welcome_email",
                new Dictionary<string, object>
                {
                    ["name"] = "Juan Pérez",
                    ["company_name"] = "Acme Corp",
                    ["verification_link"] = "https://example.com/verify/xyz789"
                },
                "es"
            );

            Console.WriteLine("\nSpanish version:");
            Console.WriteLine($"Subject: {renderedEs.Subject}");
            Console.WriteLine($"Body: {renderedEs.Body}");

            // List all email templates
            var templates = await client.ListTemplatesAsync(1, 10, "email");
            Console.WriteLine($"\nFound {templates.Meta.Total} email templates");
        }
    }
}
