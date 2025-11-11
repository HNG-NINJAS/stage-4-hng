import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import {ConfigModule} from '@nestjs/config'
import configuration from "./modules/config/configuration"
import { AppService } from './app.service';
import { PrismaService } from './modules/prisma/prisma.service';
import { PrismaModule } from './modules/prisma/prisma.module';
import { HealthModule } from './modules/health/health.module';
import { NotificationModule } from './modules/notification/notification.module';
import { EmailModule } from './modules/email/email.module';
import { RabbitMQModule } from '@golevelup/nestjs-rabbitmq';
import { RabbitmqModule } from './modules/rabbitmq/rabbitmq.module';



@Module({
  imports: [
     ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
      
    }),
   RabbitMQModule.forRoot({
      exchanges: [{ name: 'notifications', type: 'topic' }],
      uri: `amqp://${process.env.RABBITMQ_USER}:${process.env.RABBITMQ_PASS}@${process.env.RABBITMQ_HOST}:${process.env.RABBITMQ_PORT}`,
      connectionInitOptions: { wait: false },
    })
    ,PrismaModule,NotificationModule, EmailModule, RabbitmqModule,HealthModule ],
  controllers: [AppController],
  providers: [AppService, PrismaService],
})
export class AppModule {}
