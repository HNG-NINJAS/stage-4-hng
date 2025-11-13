// ============================================================================
// src/preferences/preferences.controller.ts
// ============================================================================
import {
  Controller,
  Get,
  Put,
  Param,
  Body,
  UseGuards,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { PreferencesService } from './preferences.service';
import { UpdatePreferencesDto, PreferencesResponseDto } from './dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { ApiResponse } from '../common/dto/response.dto';

/**
 * PreferencesController exposes notification preference endpoints
 * Routes: /users/:user_id/preferences
 */
@Controller('users/:user_id/preferences')
export class PreferencesController {
  constructor(private preferences_service: PreferencesService) {}

  /**
   * Get user's notification preferences
   * Authenticated endpoint
   *
   * GET /users/:user_id/preferences
   * Header: Authorization: Bearer {token}
   *
   * Response: 200 OK
   * {
   *   "success": true,
   *   "data": {
   *     "id": "...",
   *     "user_id": "...",
   *     "email_enabled": true,
   *     "email_frequency": "instant",
   *     "push_enabled": true,
   *     "push_frequency": "daily",
   *     ...
   *   },
   *   "message": "Preferences retrieved successfully"
   * }
   *
   * @param user_id - User's UUID
   * @returns User's notification preferences
   */
  @Get()
  @UseGuards(JwtAuthGuard)
  async getPreferences(
    @Param('user_id') user_id: string,
  ): Promise<ApiResponse<PreferencesResponseDto>> {
    const preferences = await this.preferences_service.getPreferences(user_id);

    return new ApiResponse(
      true,
      'Preferences retrieved successfully',
      preferences,
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
   * Update notification preferences
   * Authenticated endpoint
   *
   * PUT /users/:user_id/preferences
   * Header: Authorization: Bearer {token}
   * Body: { email_enabled?, email_frequency?, push_enabled?, ... } (all optional)
   *
   * Example:
   * {
   *   "email_enabled": false,
   *   "push_frequency": "weekly",
   *   "unsubscribe_all": true
   * }
   *
   * @param user_id - User's UUID
   * @param update_preferences_dto - Preferences to update
   * @returns Updated preferences
   */
  @Put()
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  async updatePreferences(
    @Param('user_id') user_id: string,
    @Body() update_preferences_dto: UpdatePreferencesDto,
  ): Promise<ApiResponse<PreferencesResponseDto>> {
    const preferences = await this.preferences_service.updatePreferences(
      user_id,
      update_preferences_dto,
    );

    return new ApiResponse(
      true,
      'Preferences updated successfully',
      preferences,
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
}
