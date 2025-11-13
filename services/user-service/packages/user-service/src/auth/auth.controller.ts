// ============================================================================
// FILE: src/auth/auth.controller.ts
// ============================================================================
import { Controller, Post, Body, HttpCode, HttpStatus } from '@nestjs/common';
import { AuthService } from './auth.service';
import { LoginDto } from './dto/login.dto';
import { LoginResponseDto } from './dto/login.response';
import { ApiResponse } from '../common/dto/response.dto';

/**
 * AuthController handles all authentication endpoints
 * POST /auth/login - Login with email and password
 */
@Controller('auth')
export class AuthController {
  constructor(private auth_service: AuthService) {}

  /**
   * Login endpoint
   * Validates credentials and returns JWT token
   *
   * Request body:
   * {
   *   "email": "user@example.com",
   *   "password": "password123"
   * }
   *
   * Response:
   * {
   *   "success": true,
   *   "data": {
   *     "user": { "id": "...", "name": "...", "email": "..." },
   *     "token": "eyJhbGc...",
   *     "expires_in": 3600,
   *     "token_type": "Bearer"
   *   },
   *   "message": "Login successful",
   *   "error": null,
   *   "meta": { ... }
   * }
   *
   * @param login_dto - Email and password from request body
   * @returns JWT token and user info
   */
  @Post('login')
  @HttpCode(HttpStatus.OK)
  async login(@Body() login_dto: LoginDto): Promise<ApiResponse<LoginResponseDto>> {
    const login_response = await this.auth_service.login(login_dto);

    return new ApiResponse(
      true,
      'Login successful',
      login_response,
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
