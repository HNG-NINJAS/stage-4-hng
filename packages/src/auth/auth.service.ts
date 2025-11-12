// ============================================================================
// FILE: src/auth/auth.service.ts
// ============================================================================
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { UsersService } from '../users/users.service';
import { LoginDto } from './dto/login.dto';
import { LoginResponseDto } from './dto/login.response';

/**
 * AuthService handles all authentication logic
 * - Login (credentials verification)
 * - JWT token generation and validation
 * - Password verification using bcryptjs
 */
@Injectable()
export class AuthService {
  constructor(
    private users_service: UsersService,
    private jwt_service: JwtService,
  ) {}

  /**
   * Login a user with email and password
   * Verifies credentials and returns JWT token
   *
   * @param login_dto - Contains email and password
   * @returns User info and JWT token
   * @throws UnauthorizedException if credentials are invalid
   */
  async login(login_dto: LoginDto): Promise<LoginResponseDto> {
    const { email, password } = login_dto;

    // Find user by email
    const user = await this.users_service.findByEmail(email);

    // Verify the password matches the stored hash
    // bcryptjs.compare() works exactly the same as bcrypt.compare()
    const password_valid = await this.users_service.verifyPassword(
      password,
      user.password_hash,
    );

    if (!password_valid) {
      throw new UnauthorizedException('Invalid credentials');
    }

    // Generate JWT token with user ID and email as claims
    // Token expires in 1 hour (3600 seconds)
    const payload = {
      sub: user.id,           // Subject (user ID) - standard JWT claim
      email: user.email,      // Include email for convenience
    };

    const token = this.jwt_service.sign(payload);
    const expires_in = 3600; // 1 hour in seconds

    // Return user info and token (exclude password_hash)
    return {
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
      },
      token,
      expires_in,
      token_type: 'Bearer',
    };
  }

  /**
   * Verify a JWT token and extract the payload
   * Used by JwtStrategy to validate requests
   *
   * @param token - JWT token string
   * @returns Decoded token payload or throws error if invalid
   */
  async validateToken(token: string) {
    try {
      return this.jwt_service.verify(token);
    } catch (error) {
      throw new UnauthorizedException('Invalid or expired token');
    }
  }

  /**
   * Validate user for JWT passport strategy
   * Called after token verification to ensure user still exists
   *
   * @param user_id - User's UUID from JWT token
   * @returns User object if found
   * @throws UnauthorizedException if user doesn't exist
   */
  async validateUser(user_id: string) {
    try {
      return await this.users_service.findById(user_id);
    } catch (error) {
      throw new UnauthorizedException('User not found');
    }
  }
}
