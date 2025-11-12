// ============================================================================
// src/main.ts - APPLICATION ENTRY POINT
// ============================================================================
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  // Create the NestJS application
  const app = await NestFactory.create(AppModule);

  // Enable global validation using class-validator decorators
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  // Enable CORS for cross-origin requests
  app.enableCors();

  // Start listening on port from environment or default 3001
  const port = process.env.PORT || 3001;
  await app.listen(port);
  console.log(`User Service running on port ${port}`);
}

bootstrap();
