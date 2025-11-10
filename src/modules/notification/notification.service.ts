import { HttpException, HttpStatus, Injectable, Logger } from '@nestjs/common';
import { NotificationRepository } from './notification.repository';

@Injectable()
export class NotificationService {
  private logger = new Logger();
  constructor(private readonly sf: NotificationRepository) {}
  async geNotificationById(id: string) {
    const notification = await this.sf.findByNotificationId(id);
    if (!notification)
      throw new HttpException(
        'notification not found for this id',
        HttpStatus.BAD_REQUEST,
      );

    return {
      success: true,
      data: {
        notification_id: notification.notification_id,
        user_id: notification.user_id,
        status: notification.status,
        email_to: notification.email_to,
        subject: notification.subject,
        attempts: notification.attempts,
        error_message: notification.error_message,
        created_at: notification.created_at,
        sent_at: notification.sent_at,
        delivered_at: notification.delivered_at,
        opened_at: notification.opened_at,
        clicked_at: notification.clicked_at,
        variables: notification.variables,
        events: notification.events,
      },
      message: 'Notification status retrieved',
      meta: {
        total: 1,
        limit: 1,
        page: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    };
  }
  async getUserNotifications(user_id:string){
        const notification = await this.sf.findUserById(user_id)
        if (!notification) throw new HttpException("Notification not found for this user ", HttpStatus.BAD_REQUEST)
            return {
        success:true,
        data:notification,
        message: "User notification retrieved",
        meta:{
            total:notification.length,
            limit:20,
            page:1,
            total_pages:1,
            has_next:false,
            has_previous:false
        }
            }
}
async getstats(){
    const stats =await this.sf.getStats(24)
    return{
        success:true,
        data:stats,
        message:"Notification Statistics retrieved",
        meta:{
            total:stats.length,
            limit:10,
            page:1,
            total_pages:1,
            has_next:false,
            has_previous:false
        } 
    }
}
}
