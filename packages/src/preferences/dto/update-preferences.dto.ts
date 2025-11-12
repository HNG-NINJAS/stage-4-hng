// ============================================================================
// src/preferences/dto/update-preferences.dto.ts
// ============================================================================
import { IsOptional, IsBoolean, IsIn } from 'class-validator';

/**
 * Data Transfer Object for updating notification preferences
 * All fields are optional for flexible preference updates
 */
export class UpdatePreferencesDto {
  // Email notification settings
  @IsOptional()
  @IsBoolean({ message: 'email_enabled must be a boolean' })
  email_enabled?: boolean;

  @IsOptional()
  @IsIn(['instant', 'daily', 'weekly', 'never'], {
    message: 'email_frequency must be one of: instant, daily, weekly, never',
  })
  email_frequency?: string;

  // Push notification settings
  @IsOptional()
  @IsBoolean({ message: 'push_enabled must be a boolean' })
  push_enabled?: boolean;

  @IsOptional()
  @IsIn(['instant', 'daily', 'weekly', 'never'], {
    message: 'push_frequency must be one of: instant, daily, weekly, never',
  })
  push_frequency?: string;

  // SMS notification settings (future feature)
  @IsOptional()
  @IsBoolean({ message: 'sms_enabled must be a boolean' })
  sms_enabled?: boolean;

  @IsOptional()
  @IsIn(['instant', 'daily', 'weekly', 'never'], {
    message: 'sms_frequency must be one of: instant, daily, weekly, never',
  })
  sms_frequency?: string;

  // Quick unsubscribe from all notifications
  @IsOptional()
  @IsBoolean({ message: 'unsubscribe_all must be a boolean' })
  unsubscribe_all?: boolean;
}
