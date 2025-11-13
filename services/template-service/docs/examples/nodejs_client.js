/**
 * Node.js client example for Template Service integration
 */
const axios = require('axios');

class TemplateServiceClient {
    /**
     * Initialize Template Service client
     * @param {string} baseUrl - Base URL of template service
     */
    constructor(baseUrl = 'http://template-service:3004') {
        this.baseUrl = baseUrl;
        this.apiUrl = `${baseUrl}/api/v1`;
        this.client = axios.create({
            baseURL: this.apiUrl,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    /**
     * Render a template with provided data
     * @param {string} templateId - Template identifier
     * @param {object} data - Variables to substitute
     * @param {string} languageCode - Language code (default: 'en')
     * @returns {Promise<object>} Rendered template
     */
    async renderTemplate(templateId, data, languageCode = 'en') {
        try {
            const response = await this.client.post(
                `/templates/${templateId}/render`,
                { data, language_code: languageCode }
            );

            if (!response.data.success) {
                throw new Error(`Template render failed: ${response.data.error}`);
            }

            return response.data.data;
        } catch (error) {
            console.error(`Failed to render template ${templateId}:`, error.message);
            throw error;
        }
    }

    /**
     * Get template details
     * @param {string} templateId - Template identifier
     * @returns {Promise<object>} Template details
     */
    async getTemplate(templateId) {
        const response = await this.client.get(`/templates/${templateId}`);

        if (!response.data.success) {
            throw new Error(`Template not found: ${templateId}`);
        }

        return response.data.data;
    }

    /**
     * List templates with pagination
     * @param {number} page - Page number
     * @param {number} limit - Items per page
     * @param {string} type - Filter by type
     * @returns {Promise<object>} Paginated templates
     */
    async listTemplates(page = 1, limit = 10, type = null) {
        const params = { page, limit };
        if (type) params.type = type;

        const response = await this.client.get('/templates', { params });
        return response.data;
    }

    /**
     * Check if service is healthy
     * @returns {Promise<boolean>} Health status
     */
    async healthCheck() {
        try {
            const response = await axios.get(`${this.baseUrl}/health`, {
                timeout: 5000
            });
            return response.data.data.status === 'healthy';
        } catch {
            return false;
        }
    }
}

// Example usage
async function main() {
    // Initialize client
    const client = new TemplateServiceClient('http://localhost:3004');

    // Check health
    const isHealthy = await client.healthCheck();
    if (!isHealthy) {
        console.error('Template service is not healthy!');
        process.exit(1);
    }

    // Render welcome email
    const rendered = await client.renderTemplate('welcome_email', {
        name: 'John Doe',
        company_name: 'Acme Corp',
        verification_link: 'https://example.com/verify/abc123'
    });

    console.log('Subject:', rendered.subject);
    console.log('Body:', rendered.body);
    console.log('Variables used:', rendered.variables_used);

    // Render in Spanish
    const renderedEs = await client.renderTemplate(
        'welcome_email',
        {
            name: 'Juan Pérez',
            company_name: 'Acme Corp',
            verification_link: 'https://example.com/verify/xyz789'
        },
        'es'
    );

    console.log('\nSpanish version:');
    console.log('Subject:', renderedEs.subject);
    console.log('Body:', renderedEs.body);

    // List all email templates
    const templates = await client.listTemplates(1, 10, 'email');
    console.log(`\nFound ${templates.meta.total} email templates`);
}

// Run example
if (require.main === module) {
    main().catch(console.error);
}

module.exports = TemplateServiceClient;
