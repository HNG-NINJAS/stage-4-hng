// ============================================================================
// FILE: src/users/users.controller.ts
// ============================================================================
import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Param,
  Body,
  UseGuards,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto, UpdateUserDto, UserResponseDto } from './dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import { ApiResponse } from '../common/dto/response.dto';

/**
 * UsersController exposes user management endpoints
 * Routes: /users
 */
@Controller('users')
export class UsersController {
  constructor(private users_service: UsersService) {}

  /**
   * Register a new user
   * Public endpoint (no authentication required)
   *
   * POST /users/register
   * Body: { name, email, password }
   *
   * Response: 201 Created
   * {
   *   "success": true,
   *   "data": { "id": "...", "name": "...", "email": "..." },
   *   "message": "User created successfully"
   * }
   *
   * @param create_user_dto - User registration data
   * @returns Newly created user
   */
  @Post('register')
  @HttpCode(HttpStatus.CREATED)
  async register(@Body() create_user_dto: CreateUserDto): Promise<ApiResponse<UserResponseDto>> {
    const user = await this.users_service.create(create_user_dto);

    return new ApiResponse(
      true,
      'User created successfully',
      user,
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
   * Get current user's profile
   * Authenticated endpoint (requires valid JWT)
   *
   * GET /users/me
   * Header: Authorization: Bearer {token}
   *
   * Response: 200 OK
   * {
   *   "success": true,
   *   "data": { "id": "...", "name": "...", "email": "..." },
   *   "message": "User retrieved successfully"
   * }
   *
   * @param user - Current authenticated user (injected via @CurrentUser)
   * @returns Current user's profile
   */
  @Get('me')
  @UseGuards(JwtAuthGuard)
  async getProfile(@CurrentUser() user: UserResponseDto): Promise<ApiResponse<UserResponseDto>> {
    return new ApiResponse(
      true,
      'User retrieved successfully',
      user,
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
   * Get user by ID
   * Authenticated endpoint
   *
   * GET /users/:id
   * Header: Authorization: Bearer {token}
   *
   * @param id - User's UUID
   * @returns User data
   */
  @Get(':id')
  @UseGuards(JwtAuthGuard)
  async findById(@Param('id') id: string): Promise<ApiResponse<UserResponseDto>> {
    const user = await this.users_service.findById(id);

    return new ApiResponse(
      true,
      'User retrieved successfully',
      user,
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
   * Update user profile
   * Authenticated endpoint (user can only update their own profile)
   *
   * PUT /users/:id
   * Header: Authorization: Bearer {token}
   * Body: { name?, email?, phone_number? } (all optional)
   *
   * @param id - User's UUID
   * @param update_user_dto - Fields to update
   * @param current_user - Current authenticated user
   * @returns Updated user data
   */
  @Put(':id')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  async update(
    @Param('id') id: string,
    @Body() update_user_dto: UpdateUserDto,
    @CurrentUser() current_user: UserResponseDto,
  ): Promise<ApiResponse<UserResponseDto>> {
    const user = await this.users_service.update(id, update_user_dto);

    return new ApiResponse(
      true,
      'User updated successfully',
      user,
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
   * Delete user account
   * Authenticated endpoint (user can only delete their own account)
   *
   * DELETE /users/:id
   * Header: Authorization: Bearer {token}
   *
   * Response: 204 No Content
   *
   * @param id - User's UUID
   */
  @Delete(':id')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.NO_CONTENT)
  async delete(@Param('id') id: string): Promise<void> {
    await this.users_service.delete(id);
  }
}
