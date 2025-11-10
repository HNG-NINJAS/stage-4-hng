import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { UpdateStatusDto } from './Dto/update-notification';
import { NotificationEventType } from '@prisma/client';

@Injectable()
export class NotificationRepository {
  private readonly logger = new Logger(NotificationRepository.name);
  constructor(private db: PrismaService) {}
  //   Create Notification
  async createNotication(data: {
    notification_id: string;
    user_id: string;
    template_id: string;
  }) {
    return await this.db.notificationLog.create({
      data: {
        ...data,
        type: 'EMAIL',
        status: 'PROCESSING',
      },
    });
  }

  /// update to sent

  async updateToSent(data:UpdateStatusDto){
    return await this.db.notificationLog.update({
        where:{notification_id:data.notification_id},
        data:{
            status:'SENT',
            email_to:data.email_to,
            email_from:data.email_from,
            subject:data.subject,
            provider:data.provider,
            provider_message_id:data.provider_message_id,
            provider_status_code:data.provider_status_code,
            provider_response:data.provider_response,
            sent_at:new Date(),
            attempts:{increment:1}
            
        }
    })
  }
  /// update to delivered

  async updateToDelivered(notification_id:string){
    return await this.db.notificationLog.update({
        where:{notification_id},
        data:{
            status:"DELIVERED",
            delivered_at: new Date()
        }

    })
  }
  async updateToFailed(notification_id:string,error_message:string){
    return await this.db.notificationLog.update({
        where:{notification_id},
        data:{
            status:"FAILED",
            error_message,
            attempts:{increment:1}
        }
    })
  }
  async insertVariables(notification_id:string,variables:Record<string,string>){
    const data = Object.entries(variables).map(([key,value])=>({
            notification_id,
            variable_key:key,
            variable_value:value
    }))
    return await this.db.notificationVariable.createMany({data})
  }
  async logEvent(data:{
    notification_id:string,
    event_type:NotificationEventType,
    descriptions?:string,
    metadata?:any
  }){
    return this.db.notificationEvent.create({
        data
    })
  }
  async findByNotificationId(notification_id:string){
    return await this.db.notificationLog.findUnique({
        where:{notification_id},
        include:{
            variables:true,
            events:{orderBy:{created_at:'desc'}},
            tracking_events:{orderBy:{timeStamp:'desc'}}
        }
    })
  }
  async findUserById(user_id:string,limit=20){
    return await this.db.notificationLog.findMany({
        where:{user_id,type:"EMAIL",
        },
        orderBy:{created_at:'desc'},
        take:limit,
        select:{
            notification_id:true,
            status:true,
            subject:true,
            created_at:true,
            delivered_at:true
        }
    })
  }
  async getStats(hours=24){
    const since  = new Date(Date.now()-hours*60*60*1000)
    return await this.db.notificationLog.groupBy({
        by:['status'],
        where:{
            type:'EMAIL',
            created_at:{gte:since}
        },
        _count:true
    })
  }
}
