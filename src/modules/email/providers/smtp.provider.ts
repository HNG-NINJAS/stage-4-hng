import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as nodemailer from 'nodemailer'
import { Transporter } from 'nodemailer';

interface SendEmailOptions {
  to: string;
  from: string;
  subject: string;
  html: string;
  text?: string;
  notification_id?: string;
}
@Injectable()
export class SmtpProvider {
  private readonly logger = new Logger(SmtpProvider.name);
  private transporter: Transporter;
  constructor(private configService: ConfigService) {
    this.initializeTransporter();
  }

  private initializeTransporter() {
    const host = this.configService.get<string>('EMAIL_SMTP_HOST');
    const port = this.configService.get<number>('EMAIL_SMTP_PORT');
    const secure = this.configService.get<boolean>('EMAIL_SMTP_SECURE');
    const user = this.configService.get<string>('EMAIL_SMTP_USER')
    const pass = this.configService.get<string>('EMAIL_SMTP_PASS')
    this.transporter = nodemailer.createTransport({
      host,
      port,
      secure,
      auth:{
        user,
        pass
      }
    })
    //verify connection
    this.transporter.verify((error,success)=>{
      if(error){
        this.logger.error('❌ SMTP connection failed:',error)
      }else{
        this.logger.log(' ✅ SMTP server is ready to send emails')
      }
    })
  }
  async sendEmail(options:SendEmailOptions){
    try{
      const info = await this.transporter.sendMail({
        from:options.from,
        to:options.to,
        subject:options.subject,
        html:options.html,
        text:options.text,
        headers: {
    "X-Notification-ID": options.notification_id ?? "" // ✅ correct
  }
      })
      this.logger.log(`Email sent: ${info.messageId}`)
      return {
        message_id:info.messasgeId,
        status_code:250,
        accepted:info.accepted,
        rejected:info.rejected,
        response:info.response
      }
    }catch(error){
      this.logger.error('SMTP ERROR',error)
      throw error
    }
  }
  async verifyConnection() {
    try {
      await this.transporter.verify();
      return true;
    } catch (error) {
      this.logger.error('SMTP verification failed:', error);
      return false;
    }
  }
}
