// ============================================================================
// FILE: src/users/dto/user.response.ts
// ============================================================================
/**
 * Data Transfer Object for user responses
 * This is what gets returned to clients (no sensitive data)
 */
export class UserResponseDto {
  id!: string;
  name!: string;
  email!: string;
  phone_number!: string | null;
  created_at!: Date;
  updated_at!: Date;
}