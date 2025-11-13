# TypeScript/NestJS Client Integration

Complete guide for integrating Template Service with TypeScript/NestJS applications.

## Installation

```bash
npm install axios
# or
yarn add axios
```

## Client Implementation

Create `template-client.ts`:

```typescript
import axios, { AxiosInstance } from 'axios';

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

export class TemplateServiceClient {
  private client: AxiosInstance;

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
      }
      return null;
    }
  }

  /**
   * Get template metadata
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
   * List templates with pagination
   */
  async listTemplates(
    page: number = 1,
    limit: number = 10,
    type?: string,
    category?: string
  ): Promise<{ templates: Template[]; meta: any } | null> {
    try {
      const params: any = { page, limit };
      if (type) params.type = type;
      if (category) params.category = category;

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
```

## NestJS Integration

### Module Setup

Create `template/template.module.ts`:

```typescript
import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { TemplateService } from './template.service';
import { TemplateController } from './template.controller';

@Module({
  imports: [
    HttpModule.register({
      baseURL: process.env.TEMPLATE_SERVICE_URL || 'http://template-service:3004',
      timeout: 10000,
    }),
  ],
  providers: [TemplateService],
  controllers: [TemplateController],
  exports: [TemplateService],
})
export class TemplateModule {}
```

### Service Implementation

Create `template/template.service.ts`:

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { AxiosError } from 'axios';

interface RenderTemplateDto {
  data: Record<string, any>;
  language_code?: string;
}

interface RenderedTemplate {
  subject: string | null;
  body: string;
  variables_used: string[];
}

@Injectable()
export class TemplateService {
  private readonly logger = new Logger(TemplateService.name);

  constructor(private readonly httpService: HttpService) {}

  async renderTemplate(
    templateId: string,
    data: Record<string, any>,
    languageCode: string = 'en',
    correlationId?: string
  ): Promise<RenderedTemplate | null> {
    try {
      const headers: any = { 'Content-Type': 'application/json' };
      if (correlationId) {
        headers['X-Correlation-ID'] = correlationId;
      }

      const response = await firstValueFrom(
        this.httpService.post(
          `/api/v1/templates/${templateId}/render`,
          { data, language_code: languageCode },
          { headers }
        )
      );

      if (response.data.success && response.data.data) {
        this.logger.log(`Template '${templateId}' rendered successfully`);
        return response.data.data;
      }

      this.logger.error(`Template render failed: ${response.data.error}`);
      return null;
    } catch (error) {
      this.handleError(error, `Error rendering template '${templateId}'`);
      return null;
    }
  }

  async getTemplate(
    templateId: string,
    correlationId?: string
  ): Promise<any | null> {
    try {
      const headers: any = {};
      if (correlationId) {
        headers['X-Correlation-ID'] = correlationId;
      }

      const response = await firstValueFrom(
        this.httpService.get(`/api/v1/templates/${templateId}`, { headers })
      );

      return response.data.success ? response.data.data : null;
    } catch (error) {
      this.handleError(error, `Error getting template '${templateId}'`);
      return null;
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await firstValueFrom(
        this.httpService.get('/health')
      );
      return response.status === 200 && response.data.success;
    } catch (error) {
      return false;
    }
  }

  private handleError(error: any, message: string): void {
    if (error instanceof AxiosError) {
      this.logger.error(`${message}: ${error.message}`, error.stack);
    } else {
      this.logger.error(message, error);
    }
  }
}
```

### Controller Example

Create `template/template.controller.ts`:

```typescript
import { Controller, Post, Body, Get, Param, HttpException, HttpStatus } from '@nestjs/common';
import { TemplateService } from './template.service';

@Controller('notifications')
export class TemplateController {
  constructor(private readonly templateService: TemplateService) {}

  @Post('send')
  async sendNotification(
    @Body() body: { templateId: string; data: Record<string, any> }
  ) {
    const { templateId, data } = body;

    const rendered = await this.templateService.renderTemplate(
      templateId,
      data
    );

    if (!rendered) {
      throw new HttpException(
        'Failed to render template',
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }

    // Send notification logic here
    return {
      success: true,
      message: 'Notification sent',
      data: { templateId }
    };
  }

  @Get('templates/:id')
  async getTemplate(@Param('id') id: string) {
    const template = await this.templateService.getTemplate(id);

    if (!template) {
      throw new HttpException('Template not found', HttpStatus.NOT_FOUND);
    }

    return {
      success: true,
      data: template
    };
  }
}
```

## Usage Examples

### Basic Usage

```typescript
import { TemplateServiceClient } from './template-client';

const client = new TemplateServiceClient('http://template-service:3004');

async function sendWelcomeEmail(userId: string, userName: string, userEmail: string) {
  const rendered = await client.renderTemplate(
    'welcome_email',
    {
      name: userName,
      company_name: 'Acme Corp',
      verification_link: `https://example.com/verify/${userId}`
    },
    'en',
    `welcome-${userId}`
  );

  if (rendered) {
    await sendEmail(userEmail, rendered.subject, rendered.body);
    console.log(`Welcome email sent to ${userEmail}`);
  } else {
    console.error('Failed to render welcome template');
  }
}
```

### With Fallback Strategy

```typescript
async function sendNotificationWithFallback(
  templateId: string,
  data: Record<string, any>
) {
  const client = new TemplateServiceClient();

  // Try primary template
  let rendered = await client.renderTemplate(templateId, data);

  if (!rendered) {
    // Fallback to generic template
    console.warn(`Template ${templateId} failed, using fallback`);
    rendered = await client.renderTemplate('generic_notification', data);
  }

  if (!rendered) {
    // Last resort: hardcoded message
    console.error('All templates failed, using hardcoded message');
    rendered = {
      subject: 'Notification',
      body: `Hello ${data.name || 'User'}, you have a notification.`,
      variables_used: []
    };
  }

  await sendNotification(rendered.subject, rendered.body);
}
```

### Express.js Integration

```typescript
import express from 'express';
import { TemplateServiceClient } from './template-client';

const app = express();
const templateClient = new TemplateServiceClient();

app.use(express.json());

app.post('/api/notifications/send', async (req, res) => {
  const { userId, templateId, data } = req.body;

  try {
    // Validate template exists
    const template = await templateClient.getTemplate(templateId);
    
    if (!template) {
      return res.status(404).json({
        success: false,
        error: 'TEMPLATE_NOT_FOUND',
        message: 'Template not found'
      });
    }

    // Render template
    const rendered = await templateClient.renderTemplate(
      templateId,
      data,
      'en',
      req.headers['x-correlation-id'] as string
    );

    if (!rendered) {
      return res.status(500).json({
        success: false,
        error: 'RENDER_FAILED',
        message: 'Failed to render template'
      });
    }

    // Send notification (queue or direct)
    await sendNotification(rendered);

    res.json({
      success: true,
      message: 'Notification sent',
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

app.get('/health', async (req, res) => {
  const templateHealthy = await templateClient.healthCheck();
  
  res.json({
    status: templateHealthy ? 'healthy' : 'degraded',
    services: {
      'api-gateway': 'up',
      'template-service': templateHealthy ? 'up' : 'down'
    }
  });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Testing

### Unit Tests

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { HttpService } from '@nestjs/axios';
import { of, throwError } from 'rxjs';
import { TemplateService } from './template.service';

describe('TemplateService', () => {
  let service: TemplateService;
  let httpService: HttpService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        TemplateService,
        {
          provide: HttpService,
          useValue: {
            post: jest.fn(),
            get: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<TemplateService>(TemplateService);
    httpService = module.get<HttpService>(HttpService);
  });

  it('should render template successfully', async () => {
    const mockResponse = {
      data: {
        success: true,
        data: {
          subject: 'Welcome John!',
          body: 'Hi John!',
          variables_used: ['name']
        }
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    };

    jest.spyOn(httpService, 'post').mockReturnValue(of(mockResponse as any));

    const result = await service.renderTemplate('welcome_email', { name: 'John' });

    expect(result).not.toBeNull();
    expect(result?.subject).toBe('Welcome John!');
  });

  it('should return null when template not found', async () => {
    const mockResponse = {
      data: {
        success: false,
        error: 'TEMPLATE_NOT_FOUND'
      },
      status: 404,
      statusText: 'Not Found',
      headers: {},
      config: {}
    };

    jest.spyOn(httpService, 'post').mockReturnValue(of(mockResponse as any));

    const result = await service.renderTemplate('invalid_template', { name: 'John' });

    expect(result).toBeNull();
  });
});
```

### Integration Tests

```typescript
import { TemplateServiceClient } from './template-client';

describe('Template Service Integration', () => {
  let client: TemplateServiceClient;

  beforeAll(() => {
    client = new TemplateServiceClient('http://localhost:3004');
  });

  it('should render template successfully', async () => {
    const rendered = await client.renderTemplate(
      'welcome_email',
      {
        name: 'Test User',
        company_name: 'Test Corp',
        verification_link: 'https://example.com/verify/123'
      }
    );

    expect(rendered).not.toBeNull();
    expect(rendered?.subject).toContain('Test User');
    expect(rendered?.body).toContain('Test User');
  });

  it('should check health successfully', async () => {
    const isHealthy = await client.healthCheck();
    expect(isHealthy).toBe(true);
  });
});
```

## Best Practices

1. **Use dependency injection** in NestJS for better testability
2. **Implement retry logic** with exponential backoff
3. **Always include correlation IDs** for distributed tracing
4. **Handle errors gracefully** with fallback strategies
5. **Cache template metadata** to reduce API calls
6. **Monitor health checks** regularly
7. **Use TypeScript interfaces** for type safety
8. **Log all operations** with appropriate context

## Next Steps

- Review [API Reference](../api-reference.md)
- Explore [Event Integration](./events.md)
- Set up [Monitoring](../operations/monitoring.md)
