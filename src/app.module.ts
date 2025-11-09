import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { PrismaService } from './modules/prisma/prisma.service';
import { PrismaModule } from './modules/prisma/prisma.module';
import { HealthModule } from './modules/health/health.module';
import { NotificationModule } from './modules/notification/notification.module';
import { EmailModule } from './modules/email/email.module';
import { RabbitmqModule } from './modules/rabbitmq/rabbitmq.module';
import { ConfigModule } from './modules/config/config.module';

@Module({
  imports: [PrismaModule, HealthModule, NotificationModule, EmailModule, RabbitmqModule, ConfigModule],
  controllers: [AppController],
  providers: [AppService, PrismaService],
})
export class AppModule {}
