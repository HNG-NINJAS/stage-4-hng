// ============================================================================
// src/push-tokens/push-tokens.controller.ts
// ============================================================================
import {
  Controller,
  Post,
  Get,
  Delete,
  Param,
  Body,
  UseGuards,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { PushTokensService } from './push-tokens.service';
import { RegisterTokenDto, PushTokenResponseDto } from './dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { ApiResponse } from '../common/dto/response.dto';

/**
 * PushTokensController exposes push token management endpoints
 * Routes: /users/:user_id/push-tokens
 */
@Controller('users/:user_id/push-tokens')
export class PushTokensController {
  constructor(private push_tokens_service: PushTokensService) {}

  /**
   * Register a new push token
   * Called by mobile/web apps to register for push notifications
   * Authenticated endpoint
   *
   * POST /users/:user_id/push-tokens
   * Header: Authorization: Bearer {token}
   * Body: { token, device_type, device_name? }
   *
   * Example:
   * {
   *   "token": "fF_XsDJEXXX:APA91bEkZDL0u2QH...",
   *   "device_type": "android",
   *   "device_name": "Samsung Galaxy S21"
   * }
   *
   * Response: 201 Created
   * {
   *   "success": true,
   *   "data": {
   *     "id": "...",
   *     "user_id": "...",
   *     "token": "fF_XsDJEXXX:APA91bEkZDL0u2QH...",
   *     "device_type": "android",
   *     "device_name": "Samsung Galaxy S21",
   *     "is_active": true,
   *     "created_at": "2024-01-01T00:00:00Z",
   *     "updated_at": "2024-01-01T00:00:00Z"
   *   },
   *   "message": "Token registered successfully"
   * }
   *
   * @param user_id - User's UUID
   * @param register_token_dto - Token and device info
   * @returns Registered token details
   */
  @Post()
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  async registerToken(
    @Param('user_id') user_id: string,
    @Body() register_token_dto: RegisterTokenDto,
  ): Promise<ApiResponse<PushTokenResponseDto>> {
    const token = await this.push_tokens_service.registerToken(user_id, register_token_dto);

    return new ApiResponse(
      true,
      'Token registered successfully',
      token,
      null,
      {
        total: 1,
        limit: 1,
        page: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    );
  }

  /**
   * Get all push tokens for a user
   * Returns list of all registered devices
   * Authenticated endpoint
   *
   * GET /users/:user_id/push-tokens
   * Header: Authorization: Bearer {token}
   *
   * Response: 200 OK - Array of push tokens
   *
   * @param user_id - User's UUID
   * @returns List of user's tokens
   */
  @Get()
  @UseGuards(JwtAuthGuard)
  async getUserTokens(
    @Param('user_id') user_id: string,
  ): Promise<ApiResponse<PushTokenResponseDto[]>> {
    const tokens = await this.push_tokens_service.getUserTokens(user_id);

    return new ApiResponse(
      true,
      'Tokens retrieved successfully',
      tokens,
      null,
      {
        total: tokens.length,
        limit: tokens.length,
        page: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    );
  }

  /**
   * Delete a specific push token
   * Called when user unregisters a device
   *
   * DELETE /users/:user_id/push-tokens/:token_id
   * Header: Authorization: Bearer {token}
   *
   * Response: 204 No Content
   *
   * @param user_id - User's UUID
   * @param token_id - Push token's UUID
   */
  @Delete(':token_id')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.NO_CONTENT)
  async deleteToken(
    @Param('user_id') user_id: string,
    @Param('token_id') token_id: string,
  ): Promise<void> {
    await this.push_tokens_service.deleteToken(token_id);
  }
}