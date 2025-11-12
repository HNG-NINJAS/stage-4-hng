// ============================================================================
// FILE: src/users/dto/update-user.dto.ts
// ============================================================================
import { IsOptional, IsString, IsEmail, MinLength, MaxLength } from 'class-validator';

/**
 * Data Transfer Object for updating user information
 * All fields are optional to allow partial updates
 */
export class UpdateUserDto {
  // Optional: Update user's name
  @IsOptional()
  @IsString({ message: 'Name must be a string' })
  @MinLength(2, { message: 'Name must be at least 2 characters' })
  @MaxLength(100, { message: 'Name must not exceed 100 characters' })
  name?: string;

  // Optional: Update user's email (must be unique)
  @IsOptional()
  @IsEmail({}, { message: 'Email must be a valid email address' })
  email?: string;

  // Optional: Update user's phone number
  @IsOptional()
  @IsString({ message: 'Phone number must be a string' })
  @MaxLength(20, { message: 'Phone number must not exceed 20 characters' })
  phone_number?: string;
}

