// ============================================================================
// src/preferences/dto/preferences.response.ts
// ============================================================================
/**
 * Data Transfer Object for preferences response
 * Returns all notification preference settings
 */
export class PreferencesResponseDto {
  id!: string;
  user_id!: string;
  email_enabled!: boolean;
  email_frequency!: string;
  push_enabled!: boolean;
  push_frequency!: string;
  sms_enabled!: boolean;
  sms_frequency!: string;
  unsubscribe_all!: boolean;
  created_at!: Date;
  updated_at!: Date;
}