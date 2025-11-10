import { HttpException, HttpStatus, Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NotificationRepository } from '../notification/notification.repository';
import { Subject } from 'rxjs';
import { error } from 'console';

interface EmailMessageQueue{
    notification_id:string,
    user_id:string,
    template_id:string
    variables:Record<string,string>
}
@Injectable()
export class EmailService {
    private readonly logger = new Logger(EmailService.name)
    constructor(
        private ConfigService:ConfigService,
        private notificationRepo:NotificationRepository,
        private userClient: UserClientService,
        private templateClient:TemplateClientService,
        private templateRenderer:TemplateRenderService,
        private sendSmtpProvider:SmtpProvider
    ){}
    async processEmail(message:EmailMessageQueue){
            const {notification_id,user_id,template_id,variables} = message
            try{
                await this.notificationRepo.createNotication({
                    notification_id,
                    user_id,
                    template_id
                })
                await this.notificationRepo.logEvent({
                    notification_id,
                    event_type:'PROCESSING_STARTED',
                    descriptions:'Started processing email notification'
                })
                this.logger.log(`Processing notification: ${notification_id}`)
                 // Get user email
                 const user = await this.userClient.getUserById(user_id)
                 if(!user.preferences.email_enabled){
                    throw new HttpException("User preference is not enabled for email notifications",HttpStatus.BAD_REQUEST)
                 };
                 await this.notificationRepo.logEvent({
                    notification_id,
                    event_type:'USER_FETCHED',
                    descriptions:` User email :${user.email}`
                 })
                 //Get template 
                 const template = await this.templateClient.getTemplate(
                    template_id,
                    user.preference.language
                 )
                 await this.notificationRepo.logEvent({
                    notification_id,
                    event_type:'TEMPLATE_FETCHED',
                    descriptions:`Template: ${template.name}`
                })
                // Save variables
                await this.notificationRepo.insertVariables(notification_id,variables)
                //Render template
                const rendered = this.templateRenderer.render(template,variables)
                await this.notificationRepo.logEvent({
                    notification_id,
                    event_type:'EMAIL_RENDERED',
                    descriptions:"Template rendered successfully"
                })
                //send email
                const response = await this.sendSmtpProvider.sendEmail({
                    to:user.email,
                    from:this.ConfigService.get<string>('email.from'),
                    subject:rendered.subject,
                    html:rendered.html_body,
                    customArgs:{notification_id}

                })
                //update to sent
                await this.notificationRepo.updateToSent({
                    notification_id,
                    email_to:user.email,
                    email_from: this.ConfigService.get<string>('email.from')!!,
                    subject: rendered.subject,
                    provider:'SMTP',
                    provider_message_id:response.message_id,
                    provider_status_code:response.status_code,
                    provider_response:response
                })
                //await to delivered
                await this.notificationRepo.updateToDelivered(notification_id)
                await this.notificationRepo.logEvent({
                    notification_id,
                    event_type:'DELIVERED',
                    descriptions:'Email delivered successfully',
                })
                this.logger.log(`Email sent successfully:${notification_id}`)
            }catch(error){
                this.logger.error(`Failed to process notificatino:${notification_id}`,error.stack)
                await this.notificationRepo.updateToFailed(notification_id,error.message)
                await this.notificationRepo.logEvent({
                    notification_id,
                    event_type:'FAILED',
                    descriptions:error.message,
                    metadata:{
                        stack:error.stack
                    }
                })
                throw error
            }
    }
    
}
