import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe,Logger } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const logger = new Logger("Bootstrap")

  //Global Prefix
  app.setGlobalPrefix("api")
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist:true,
      forbidNonWhitelisted:true,
      transform:true
    })
  )
  app.enableCors()
  await app.listen(process.env.PORT ?? 3000);
  logger.log(`🫰🫰 Email Service running `)
  logger.log(`💫 Ready to consume from RabbitMQ`)
}
bootstrap();
