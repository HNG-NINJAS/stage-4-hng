// ============================================================================
// src/preferences/preferences.service.ts
// ============================================================================
import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { UpdatePreferencesDto, PreferencesResponseDto } from './dto';

/**
 * PreferencesService manages user notification preferences
 * Controls how and when users receive notifications via different channels
 * - Email frequency (instant, daily, weekly, never)
 * - Push notification frequency
 * - SMS preferences
 */
@Injectable()
export class PreferencesService {
  constructor(private prisma: PrismaService) {}

  /**
   * Get notification preferences for a user
   * Returns all preference settings for the user
   *
   * @param user_id - User's UUID
   * @returns User's notification preferences
   * @throws NotFoundException if user doesn't exist
   */
  async getPreferences(user_id: string): Promise<PreferencesResponseDto> {
    // First verify the user exists
    await this.prisma.user.findUniqueOrThrow({
      where: { id: user_id },
    });

    // Get the user's notification preferences
    const preferences = await this.prisma.notificationPreference.findUniqueOrThrow({
      where: { user_id },
    });

    return preferences;
  }

  /**
   * Update user's notification preferences
   * Allows partial updates (only specified fields are changed)
   *
   * @param user_id - User's UUID
   * @param update_preferences_dto - Preferences to update
   * @returns Updated preferences
   * @throws NotFoundException if user doesn't exist
   */
  async updatePreferences(
    user_id: string,
    update_preferences_dto: UpdatePreferencesDto,
  ): Promise<PreferencesResponseDto> {
    // Verify user exists first
    await this.prisma.user.findUniqueOrThrow({
      where: { id: user_id },
    });

    // Update only the provided fields
    const updated_preferences = await this.prisma.notificationPreference.update({
      where: { user_id },
      data: update_preferences_dto,
    });

    return updated_preferences;
  }

  /**
   * Internal method: Get preferences for service-to-service communication
   * Called by notification services to check if notifications are enabled
   *
   * @param user_id - User's UUID
   * @returns User's preferences or null
   */
  async getPreferencesInternal(user_id: string) {
    return this.prisma.notificationPreference.findUnique({
      where: { user_id },
    });
  }

  /**
   * Check if a specific notification type is enabled for the user
   * Used by notification services before sending
   *
   * @param user_id - User's UUID
   * @param notification_type - Type of notification ("email" or "push")
   * @returns True if enabled, false otherwise
   */
  async isNotificationEnabled(
    user_id: string,
    notification_type: 'email' | 'push',
  ): Promise<boolean> {
    const preferences = await this.getPreferencesInternal(user_id);

    if (!preferences) {
      return false;
    }

    if (preferences.unsubscribe_all) {
      return false;
    }

    if (notification_type === 'email') {
      return preferences.email_enabled && preferences.email_frequency !== 'never';
    }

    if (notification_type === 'push') {
      return preferences.push_enabled && preferences.push_frequency !== 'never';
    }

    return false;
  }
}