// ============================================================================
// PUSH TOKENS MODULE - FILE 6: src/push-tokens/push-tokens.module.ts
// ============================================================================
import { Module } from '@nestjs/common';
import { PushTokensService } from './push-tokens.service';
import { PushTokensController } from './push-tokens.controller';
import { PrismaService } from '../prisma/prisma.service';

/**
 * PushTokensModule provides push token management
 * - Register device tokens
 * - Retrieve tokens for sending notifications
 * - Deactivate or delete tokens
 */
@Module({
  providers: [PushTokensService, PrismaService],
  controllers: [PushTokensController],
  exports: [PushTokensService],
})
export class PushTokensModule {}