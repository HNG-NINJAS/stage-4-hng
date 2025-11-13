// ============================================================================
// FILE: src/auth/dto/login.response.ts
// ============================================================================
/**
 * Data Transfer Object for login response
 * Returns user data and JWT token
 */
export class LoginResponseDto {
  user!: {
    id: string;
    name: string;
    email: string;
  };
  token!: string;           // JWT access token
  expires_in!: number;      // Token expiration time in seconds
  token_type!: string;      // Always "Bearer"
}