import { Controller, Get, Logger, Param } from '@nestjs/common';
import { NotificationService } from './notification.service';

@Controller('notification')
export class NotificationController {
    private readonly logger = new Logger(NotificationController.name)
    constructor(private readonly notificationService:NotificationService){}
    @Get(':notification_id/status')
    async getStatus(@Param('notification_id') notification_id:string){
        this.logger.log(`Getting status for notification: ${notification_id}`)
        return this.notificationService.geNotificationById(notification_id)
    }
    @Get('user/:user_id')
    async getUserNotifications(@Param('user_id') user_id:string){
        this.logger.log(`Getting status for user: ${user_id} `)
        return this.notificationService.getUserNotifications(user_id)
    }
    @Get('stats')
    async getStats(){
        this.logger.log(`Getting notification statistics`)
        return this.notificationService.getstats()
    }
}
