import { IsString,IsInt } from "class-validator";
import { EmailProvider } from "@prisma/client";
export class UpdateStatusDto{
    @IsString()
     notification_id: string;
    @IsString()
    email_to: string;
    @IsString()
    email_from: string;
    @IsString()
    subject: string;
    provider: EmailProvider;
    @IsString()
    provider_message_id: string;
    @IsInt()
    provider_status_code: number;
    provider_response: any;
}