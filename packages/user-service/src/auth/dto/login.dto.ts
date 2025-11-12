// ============================================================================
// FILE: src/auth/dto/login.dto.ts
// ============================================================================
import { IsEmail, IsNotEmpty, IsString } from 'class-validator';

/**
 * Data Transfer Object for login requests
 * Validates that email and password are provided
 */
export class LoginDto {
  // User's email address
  @IsNotEmpty({ message: 'Email is required' })
  @IsEmail({}, { message: 'Email must be a valid email address' })
  email!: string;

  // User's password
  @IsNotEmpty({ message: 'Password is required' })
  @IsString({ message: 'Password must be a string' })
  password!: string;
}