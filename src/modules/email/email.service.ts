import { 
  BadRequestException, 
  HttpException, 
  HttpStatus, 
  Injectable, 
  Logger 
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NotificationRepository } from '../notification/notification.repository';
import { UserClientService } from '../../external-services/user-client/user-client.service';
import { TemplateClientService } from '../../external-services/template-client/template-client.service';
import { TemplateRendererService } from './template/template-render.service';
import { SmtpProvider } from './providers/smtp.provider';

interface EmailMessageQueue {
  notification_id: string;
  user_id: string;
  template_id: string;
  variables: Record<string, string>;
  priority?: 'high' | 'normal' | 'low';
  timestamp?: string;
  metadata?: {
    correlation_id?: string;
    source?: string;
    retry_count?: number;
  };
}

@Injectable()
export class EmailService {
  private readonly logger = new Logger(EmailService.name);

  constructor(
    private configService: ConfigService,
    private notificationRepo: NotificationRepository,
    private userClient: UserClientService,
    private templateClient: TemplateClientService,
    private templateRenderer: TemplateRendererService,
    private smtpProvider: SmtpProvider,
  ) {}

  async processEmail(message: EmailMessageQueue): Promise<void> {
    const { notification_id, user_id, template_id, variables } = message;

    try {
      // 1. Create notification log
      await this.notificationRepo.createNotication({
        notification_id,
        user_id,
        template_id,
      });

      await this.notificationRepo.logEvent({
        notification_id,
        event_type: 'PROCESSING_STARTED',
        descriptions: 'Started processing email notification',
      });

      this.logger.log(`Processing notification: ${notification_id}`);

      // 2. Validate user can receive email (comprehensive check)
      const validation = await this.userClient.validateUserCanReceiveEmail(user_id);
      
      if (!validation.can_receive) {
        throw new BadRequestException(validation.reason);
      }

      // 3. Get user details from User Service
      const user = await this.userClient.getUserById(user_id);

      await this.notificationRepo.logEvent({
        notification_id,
        event_type: 'USER_FETCHED',
        descriptions: `User email: ${user.email}`,
      });

      this.logger.log(`✅ Fetched user: ${user.email}`);

      // 4. Get user language for template
      const language = await this.userClient.getUserLanguage(user_id);

      // 5. Get template from Template Service with fallback
      const template = await this.templateClient.getTemplateWithFallback(
        template_id,
        language,
        'en', // Fallback to English if user's language not available
      );

      await this.notificationRepo.logEvent({
        notification_id,
        event_type: 'TEMPLATE_FETCHED',
        descriptions: `Template: ${template.name} (${template.language})`,
        metadata: {
          template_key: template.template_key,
          type: template.type,
          variables: template.variables,
        },
      });

      this.logger.log(`✅ Fetched template: ${template.name}`);

      // 6. Validate template variables
      const variableValidation = await this.templateClient.validateTemplateVariables(
        template_id,
        variables,
        language,
      );

      if (!variableValidation.valid) {
        throw new BadRequestException(
          `Missing required variables: ${variableValidation.missing_variables.join(', ')}`,
        );
      }

      if (variableValidation.extra_variables.length > 0) {
        this.logger.warn(
          `Extra variables provided: ${variableValidation.extra_variables.join(', ')}`,
        );
      }

      // 7. Save variables to database
      await this.notificationRepo.insertVariables(notification_id, variables);

      // 8. Render template with variables
      const rendered = this.templateRenderer.render(template, variables);

      await this.notificationRepo.logEvent({
        notification_id,
        event_type: 'EMAIL_RENDERED',
        descriptions: 'Template rendered successfully',
        metadata: {
          subject: rendered.subject,
        },
      });

      this.logger.log(`✅ Template rendered with subject: ${rendered.subject}`);

      // 9. Send email via SMTP
      const response = await this.smtpProvider.sendEmail({
        to: user.email,
        from: this.configService.get<string>('EMAIL_FROM')!,
        subject: rendered.subject,
        html: rendered.html_body, // Plain text version
        notification_id
      });

      // 10. Update status to SENT
      await this.notificationRepo.updateToSent({
        notification_id,
        email_to: user.email,
        email_from: this.configService.get<string>('EMAIL_FROM')!,
        subject: rendered.subject,
        provider: 'SMTP',
        provider_message_id: response.message_id,
        provider_status_code: response.status_code,
        provider_response: response,
      });

      await this.notificationRepo.logEvent({
        notification_id,
        event_type: 'SENT_TO_PROVIDER',
        descriptions: 'Email sent via SMTP',
        metadata: {
          message_id: response.message_id,
          accepted: response.accepted,
        },
      });

      // 11. Update status to DELIVERED
      await this.notificationRepo.updateToDelivered(notification_id);

      await this.notificationRepo.logEvent({
        notification_id,
        event_type: 'DELIVERED',
        descriptions: 'Email delivered successfully',
      });

      this.logger.log(`✅ Email sent successfully: ${notification_id}`);
    } catch (error) {
      this.logger.error(
        `❌ Failed to process notification: ${notification_id}`,
        error.stack,
      );

      // Update status to FAILED
      await this.notificationRepo.updateToFailed(
        notification_id,
        error.message,
      );

      await this.notificationRepo.logEvent({
        notification_id,
        event_type: 'FAILED',
        descriptions: error.message,
        metadata: {
          stack: error.stack,
          error_type: error.constructor.name,
        },
      });

      // Re-throw to trigger RabbitMQ retry
      throw error;
    }
  }

  /**
   * Batch process multiple emails (for future use)
   */
  async processBatchEmails(messages: EmailMessageQueue[]): Promise<void> {
    this.logger.log(`Processing batch of ${messages.length} emails`);

    const results = await Promise.allSettled(
      messages.map((message) => this.processEmail(message)),
    );

    const succeeded = results.filter((r) => r.status === 'fulfilled').length;
    const failed = results.filter((r) => r.status === 'rejected').length;

    this.logger.log(
      `Batch processing complete: ${succeeded} succeeded, ${failed} failed`,
    );
  }

  /**
   * Preview email without sending (for testing)
   */
  async previewEmail(
    user_id: string,
    template_id: string,
    variables: Record<string, string>,
  ): Promise<{ subject: string; html_body: string; text_body?: string }> {
    try {
      // Get user language
      const language = await this.userClient.getUserLanguage(user_id);

      // Get template
      const template = await this.templateClient.getTemplate(
        template_id,
        language,
      );

      // Validate variables
      const validation = await this.templateClient.validateTemplateVariables(
        template_id,
        variables,
        language,
      );

      if (!validation.valid) {
        throw new BadRequestException(
          `Missing required variables: ${validation.missing_variables.join(', ')}`,
        );
      }

      // Render template
      const rendered = this.templateRenderer.render(template, variables);

      return rendered;
    } catch (error) {
      this.logger.error('Preview email failed:', error);
      throw error;
    }
  }

  /**
   * Get notification status
   */
  async getNotificationStatus(notification_id: string) {
    return await this.notificationRepo.findByNotificationId(notification_id);
  }
}