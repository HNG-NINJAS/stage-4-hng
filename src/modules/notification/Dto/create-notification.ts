import {IsString,IsUUID,IsObject,IsEnum,IsOptional} from 'class-validator'
export enum NotificationPriority{
    HIGH ='high',
    NORMAL ="normal",
    LOW ="low"
}
export class CreateNotificationDto{
    @IsUUID()
    notification_id:string
    @IsString()
    user_id:string
    @IsString()
    template_id:string
    @IsObject()
    variables:Record<string,string>
    @IsEnum(NotificationPriority)
    @IsOptional()
    priority?: NotificationPriority

}