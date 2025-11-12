// ============================================================================
// src/preferences/preferences.module.ts
// ============================================================================
import { Module } from '@nestjs/common';
import { PreferencesService } from './preferences.service';
import { PreferencesController } from './preferences.controller';
import { PrismaService } from '../prisma/prisma.service';

/**
 * PreferencesModule provides notification preference management
 * - Get user preferences
 * - Update notification settings
 * - Check if notifications are enabled
 */
@Module({
  providers: [PreferencesService, PrismaService],
  controllers: [PreferencesController],
  exports: [PreferencesService],
})
export class PreferencesModule {}
