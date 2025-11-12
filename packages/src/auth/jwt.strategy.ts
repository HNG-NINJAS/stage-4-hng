// ============================================================================
// FILE: src/auth/jwt.strategy.ts
// ============================================================================
import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Strategy, ExtractJwt } from 'passport-jwt';
import { ConfigService } from '@nestjs/config';
import { AuthService } from './auth.service';

/**
 * JwtStrategy implements JWT bearer token authentication
 * - Extracts token from "Authorization: Bearer {token}" header
 * - Validates token signature using JWT_SECRET
 * - Returns user object for authenticated requests
 */
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(
    config_service: ConfigService,
    private auth_service: AuthService,
  ) {
    super({
      // Extract JWT from "Authorization: Bearer {token}" header
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),

      // Use secret from environment variables
      secretOrKey: config_service.get<string>('JWT_SECRET'),

      // Whether to ignore expiration (keep false for security)
      ignoreExpiration: false,
    });
  }

  /**
   * Called after token is verified
   * Validates that the user still exists in database
   *
   * @param payload - Decoded JWT token payload
   * @returns User object if valid
   */
  async validate(payload: any) {
    // payload contains: { sub: user_id, email: user_email, iat, exp }
    return this.auth_service.validateUser(payload.sub);
  }
}

