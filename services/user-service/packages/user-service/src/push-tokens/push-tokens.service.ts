// ============================================================================
// src/push-tokens/push-tokens.service.ts
// ============================================================================
import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { RegisterTokenDto, PushTokenResponseDto } from './dto';

/**
 * PushTokensService manages push notification device tokens
 * - Register new device tokens from mobile/web apps
 * - List all tokens for a user
 * - Invalidate tokens when devices unregister
 * - Retrieve tokens for sending push notifications
 */
@Injectable()
export class PushTokensService {
  constructor(private prisma: PrismaService) {}

  /**
   * Register a new push token for a user
   * Can be called multiple times from different devices
   * Automatically deactivates old tokens from the same device if needed
   *
   * @param user_id - User's UUID
   * @param register_token_dto - Token from push service (FCM, OneSignal, etc.)
   * @returns The registered token details
   * @throws NotFoundException if user doesn't exist
   */
  async registerToken(
    user_id: string,
    register_token_dto: RegisterTokenDto,
  ): Promise<PushTokenResponseDto> {
    // Verify the user exists
    await this.prisma.user.findUniqueOrThrow({
      where: { id: user_id },
    });

    // Check if this exact token already exists for this user
    const existing_token = await this.prisma.pushToken.findUnique({
      where: { token: register_token_dto.token },
    });

    // If token exists and belongs to same user, just update it
    if (existing_token && existing_token.user_id === user_id) {
      return this.prisma.pushToken.update({
        where: { id: existing_token.id },
        data: {
          is_active: true,
          device_name: register_token_dto.device_name,
          updated_at: new Date(),
        },
      });
    }

    // If token exists but belongs to different user, remove it from that user
    if (existing_token && existing_token.user_id !== user_id) {
      await this.prisma.pushToken.delete({
        where: { id: existing_token.id },
      });
    }

    // Create new token for this user
    const push_token = await this.prisma.pushToken.create({
      data: {
        user_id,
        token: register_token_dto.token,
        device_type: register_token_dto.device_type,
        device_name: register_token_dto.device_name || null,
        is_active: true,
      },
    });

    return push_token;
  }

  /**
   * Get all active push tokens for a user
   * Used to retrieve all devices the user wants to send notifications to
   *
   * @param user_id - User's UUID
   * @returns Array of user's push tokens
   * @throws NotFoundException if user doesn't exist
   */
  async getUserTokens(user_id: string): Promise<PushTokenResponseDto[]> {
    // Verify user exists
    await this.prisma.user.findUniqueOrThrow({
      where: { id: user_id },
    });

    // Get all active tokens for the user
    return this.prisma.pushToken.findMany({
      where: {
        user_id,
        is_active: true,
      },
    });
  }

  /**
   * Deactivate a specific push token
   * Called when a device unregisters or token becomes invalid
   *
   * @param token_id - Push token's UUID
   * @returns The deactivated token
   * @throws NotFoundException if token doesn't exist
   */
  async deactivateToken(token_id: string): Promise<PushTokenResponseDto> {
    // Verify token exists
    await this.prisma.pushToken.findUniqueOrThrow({
      where: { id: token_id },
    });

    // Mark token as inactive but don't delete (keep history)
    return this.prisma.pushToken.update({
      where: { id: token_id },
      data: {
        is_active: false,
        updated_at: new Date(),
      },
    });
  }

  /**
   * Delete a push token permanently
   * Removes the token record from database
   *
   * @param token_id - Push token's UUID
   * @throws NotFoundException if token doesn't exist
   */
  async deleteToken(token_id: string): Promise<void> {
    // Verify token exists
    await this.prisma.pushToken.findUniqueOrThrow({
      where: { id: token_id },
    });

    // Delete the token
    await this.prisma.pushToken.delete({
      where: { id: token_id },
    });
  }

  /**
   * Internal method: Get all active tokens for a user (for service-to-service)
   * Used by push notification service to send notifications
   *
   * @param user_id - User's UUID
   * @returns Array of tokens or empty array if none exist
   */
  async getUserTokensInternal(user_id: string): Promise<any[]> {
    return this.prisma.pushToken.findMany({
      where: {
        user_id,
        is_active: true,
      },
      select: {
        token: true,
        device_type: true,
      },
    });
  }
}
