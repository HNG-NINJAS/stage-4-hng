import {
  Injectable,
  Logger,
  HttpException,
  HttpStatus,
  OnModuleInit,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom, catchError, timeout, retry } from 'rxjs';
import { AxiosError, AxiosResponse } from 'axios';
import {
  ITemplate,
  ITemplateResponse,
  ITemplateListResponse,
  ITemplateValidation,
} from './interface/template.interface';

@Injectable()
export class TemplateClientService implements OnModuleInit {
  private readonly logger = new Logger(TemplateClientService.name);
  private readonly baseUrl: string;
  private readonly timeout: number = 5000;
  private readonly maxRetries: number = 3;

  constructor(
    private configService: ConfigService,
    private httpService: HttpService,
    // private cacheService: TemplateCacheService,
  ) {
    this.baseUrl = this.configService.get<string>('services.templateService')!;
  }

  onModuleInit() {
    this.logger.log(`Template Service Client initialized: ${this.baseUrl}`);
  }

  /**
   * Get template by key and language
   */
  async getTemplate(
    template_key: string,
    language: string = 'en',
  ): Promise<ITemplate> {
    try {
      // Check cache first
    //   const cached = this.cacheService.get(template_key, language);
    //   if (cached) {
    //     this.logger.debug(`Using cached template: ${template_key} (${language})`);
    //     return cached;
    //   }

      this.logger.log(`Fetching template: ${template_key} (language: ${language})`);

      const response = await firstValueFrom(
        this.httpService
          .get<ITemplateResponse>(
            `${this.baseUrl}/api/templates/${template_key}`,
            {
              params: { language },
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Service-Name': 'email-service',
              },
            },
          )
          .pipe(
            timeout(this.timeout),
            retry({ count: 2, delay: 1000 }),
            catchError((error: AxiosError) => {
              return this.handleError(error, `fetch template ${template_key}`);
            }),
          ),
      );

      this.validateResponse(response);

      const template = response.data.data;

      // Cache the template 
    //  this.cacheService.set(template);

      this.logger.log(`✅ Template fetched: ${template.name} (${template.type})`);

      return template;
    } catch (error) {
      this.logger.error(
        `Error fetching template ${template_key}:`,
        error.message,
      );
      throw error;
    }
  }

  /**
   * Get template by ID
   */
  async getTemplateById(template_id: number): Promise<ITemplate> {
    try {
      this.logger.log(`Fetching template by ID: ${template_id}`);

      const response = await firstValueFrom(
        this.httpService
          .get<ITemplateResponse>(`${this.baseUrl}/api/templates/id/${template_id}`, {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          })
          .pipe(
            timeout(this.timeout),
            retry({ count: 2, delay: 1000 }),
            catchError((error: AxiosError) => {
              return this.handleError(error, `fetch template ID ${template_id}`);
            }),
          ),
      );

      this.validateResponse(response);

      return response.data.data;
    } catch (error) {
      this.logger.error(`Error fetching template ID ${template_id}:`, error.message);
      throw error;
    }
  }

  /**
   * List all templates with filters
   */
  async listTemplates(filters?: {
    type?: string;
    language?: string;
    page?: number;
    limit?: number;
  }): Promise<ITemplate[]> {
    try {
      this.logger.log('Fetching template list', filters);

      const response = await firstValueFrom(
        this.httpService
          .get<ITemplateListResponse>(`${this.baseUrl}/api/templates`, {
            params: filters,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          })
          .pipe(
            timeout(this.timeout),
            catchError((error: AxiosError) => {
              return this.handleError(error, 'list templates');
            }),
          ),
      );

      if (!response.data.success) {
        throw new HttpException(
          response.data.message || 'Failed to list templates',
          HttpStatus.INTERNAL_SERVER_ERROR,
        );
      }

      this.logger.log(`✅ Fetched ${response.data.data.length} templates`);

      return response.data.data;
    } catch (error) {
      this.logger.error('Error listing templates:', error.message);
      throw error;
    }
  }

  /**
   * Validate if provided variables match template requirements
   */
  async validateTemplateVariables(
    template_key: string,
    variables: Record<string, string>,
    language: string = 'en',
  ): Promise<ITemplateValidation> {
    try {
      const template = await this.getTemplate(template_key, language);

      const providedVars = Object.keys(variables);
      const requiredVars = template.variables;

      // Find missing required variables
      const missing_variables = requiredVars.filter(
        (variable) => !providedVars.includes(variable),
      );

      // Find extra variables not in template
      const extra_variables = providedVars.filter(
        (variable) => !requiredVars.includes(variable),
      );

      const valid = missing_variables.length === 0;

      if (!valid) {
        this.logger.warn(
          `Template validation failed for ${template_key}. Missing: ${missing_variables.join(', ')}`,
        );
      }

      if (extra_variables.length > 0) {
        this.logger.debug(
          `Extra variables provided for ${template_key}: ${extra_variables.join(', ')}`,
        );
      }

      return {
        valid,
        missing_variables,
        extra_variables,
      };
    } catch (error) {
      this.logger.error('Template validation error:', error.message);
      throw error;
    }
  }

  /**
   * Get available languages for a template
   */
  async getAvailableLanguages(template_key: string): Promise<string[]> {
    try {
      this.logger.log(`Getting available languages for: ${template_key}`);

      // Fetch templates with same key but different languages
      const templates = await this.listTemplates();
      const languages = templates
        .filter((t) => t.template_key === template_key)
        .map((t) => t.language);

      const uniqueLanguages = [...new Set(languages)];

      this.logger.log(
        `✅ Available languages for ${template_key}: ${uniqueLanguages.join(', ')}`,
      );

      return uniqueLanguages;
    } catch (error) {
      this.logger.error('Error getting available languages:', error.message);
      throw error;
    }
  }

  /**
   * Check if template exists
   */
  async templateExists(
    template_key: string,
    language: string = 'en',
  ): Promise<boolean> {
    try {
      await this.getTemplate(template_key, language);
      return true;
    } catch (error) {
      if (error instanceof HttpException && error.getStatus() === 404) {
        return false;
      }
      throw error;
    }
  }

  /**
   * Get template with fallback language
   */
  async getTemplateWithFallback(
    template_key: string,
    preferred_language: string,
    fallback_language: string = 'en',
  ): Promise<ITemplate> {
    try {
      // Try preferred language first
      return await this.getTemplate(template_key, preferred_language);
    } catch (error) {
      if (error instanceof HttpException && error.getStatus() === 404) {
        this.logger.warn(
          `Template ${template_key} not found in ${preferred_language}, trying fallback ${fallback_language}`,
        );
        // Try fallback language
        return await this.getTemplate(template_key, fallback_language);
      }
      throw error;
    }
  }

  /**
   * Batch get templates
   */
  async getTemplatesByKeys(
    template_keys: string[],
    language: string = 'en',
  ): Promise<ITemplate[]> {
    try {
      this.logger.log(`Batch fetching ${template_keys.length} templates`);

      const promises = template_keys.map((key) =>
        this.getTemplate(key, language),
      );

      const results = await Promise.allSettled(promises);

      const templates: ITemplate[] = [];
      const failed: string[] = [];

      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          templates.push(result.value);
        } else {
          failed.push(template_keys[index]);
          this.logger.warn(
            `Failed to fetch template ${template_keys[index]}: ${result.reason}`,
          );
        }
      });

      if (failed.length > 0) {
        this.logger.warn(
          `Failed to fetch ${failed.length} templates: ${failed.join(', ')}`,
        );
      }

      this.logger.log(`✅ Successfully fetched ${templates.length} templates`);

      return templates;
    } catch (error) {
      this.logger.error('Error in batch template fetch:', error.message);
      throw error;
    }
  }

  /**
   * Invalidate cache for specific template
   */
//   invalidateCache(template_key: string, language?: string): void {
//     this.cacheService.invalidate(template_key, language);
//   }

  /**
   * Clear all template cache
   */
//   clearCache(): void {
//     this.cacheService.clear();
//   }

  /**
   * Get cache statistics
   */
//   getCacheStats() {
//     return this.cacheService.getStats();
//   }

  /**
   * Health check - verify connection to Template Service
   */
  async healthCheck(): Promise<{ status: string; message: string }> {
    try {
      const response = await firstValueFrom(
        this.httpService
          .get(`${this.baseUrl}/health`, {
            timeout: 3000,
          })
          .pipe(
            catchError((error: AxiosError) => {
              throw new HttpException(
                'Template service is unavailable',
                HttpStatus.SERVICE_UNAVAILABLE,
              );
            }),
          ),
      );

      return {
        status: 'healthy',
        message: 'Template service is reachable',
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: error.message,
      };
    }
  }

  /**
   * Private helper methods
   */

  private validateResponse(response: AxiosResponse<ITemplateResponse>): void {
    if (!response.data) {
      throw new HttpException(
        'Empty response from Template Service',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }

    if (!response.data.success) {
      throw new HttpException(
        response.data.message || 'Template service returned error',
        HttpStatus.BAD_REQUEST,
      );
    }

    if (!response.data.data) {
      throw new HttpException(
        'No template data in response',
        HttpStatus.NOT_FOUND,
      );
    }
  }

  private handleError(error: AxiosError, operation: string): never {
    const status = error.response?.status || HttpStatus.INTERNAL_SERVER_ERROR;
    const message =
      (error.response?.data as any)?.message ||
      error.message ||
      'Unknown error';

    this.logger.error(`Failed to ${operation}:`, {
      status,
      message,
      url: error.config?.url,
    });

    // Map common HTTP errors
    switch (status) {
      case 404:
        throw new HttpException(
          `Template not found: ${message}`,
          HttpStatus.NOT_FOUND,
        );
      case 400:
        throw new HttpException(
          `Invalid request: ${message}`,
          HttpStatus.BAD_REQUEST,
        );
      case 401:
      case 403:
        throw new HttpException(
          `Authentication failed: ${message}`,
          HttpStatus.UNAUTHORIZED,
        );
      case 429:
        throw new HttpException(
          'Rate limit exceeded',
          HttpStatus.TOO_MANY_REQUESTS,
        );
      case 503:
        throw new HttpException(
          'Template service unavailable',
          HttpStatus.SERVICE_UNAVAILABLE,
        );
      default:
        throw new HttpException(
          `Template service error: ${message}`,
          status,
        );
    }
  }
}