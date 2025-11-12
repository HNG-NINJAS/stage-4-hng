// ============================================================================
// src/push-tokens/dto/push-token.response.ts
// ============================================================================
/**
 * Data Transfer Object for push token response
 */
export class PushTokenResponseDto {
  id!: string;
  user_id!: string;
  token!: string;
  device_type!: string;
  device_name!: string | null;
  is_active!: boolean;
  created_at!: Date;
  updated_at!: Date;
}