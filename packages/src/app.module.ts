// ============================================================================
// src/app.module.ts - ROOT MODULE
// ============================================================================
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { PreferencesModule } from './preferences/preferences.module';
import { PushTokensModule } from './push-tokens/push-tokens.module';
import { HealthController } from './health/health.controller';

/**
 * AppModule is the root module of the User Service
 * Imports and configures all feature modules
 */
@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),
    AuthModule,
    UsersModule,
    PreferencesModule,
    PushTokensModule,
  ],
  controllers: [HealthController],
})
export class AppModule {}