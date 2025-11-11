import { Module } from '@nestjs/common';
import { EmailService } from './email.service';
import { NotificationModule } from '../notification/notification.module';
import { EmailConsumerService } from './email-consumer.service';
import { TemplateRendererService } from './template/template-render.service';
import { SmtpProvider } from './providers/smtp.provider';
import { UserClientModule } from 'src/external-services/user-client/user-client.module';
import { TemplateClientModule } from 'src/external-services/template-client/template-client.module';

@Module({
  imports:[NotificationModule,UserClientModule,TemplateClientModule],
  providers: [EmailService,
    EmailConsumerService,
    TemplateRendererService,
    SmtpProvider
  ]
})
export class EmailModule {}
