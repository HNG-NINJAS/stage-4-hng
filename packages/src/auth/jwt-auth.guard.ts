// ============================================================================
// FILE: src/auth/jwt-auth.guard.ts
// ============================================================================
import { Injectable } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

/**
 * JwtAuthGuard protects routes from unauthenticated requests
 * Usage: @UseGuards(JwtAuthGuard) on controller methods
 *
 * Returns 401 Unauthorized if:
 * - No Authorization header provided
 * - Token is invalid or expired
 * - User doesn't exist in database
 */
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}

