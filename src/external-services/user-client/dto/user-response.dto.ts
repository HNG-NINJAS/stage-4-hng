import { IsString, IsEmail, IsBoolean, IsObject, ValidateNested, IsOptional } from 'class-validator';
import { Type } from 'class-transformer';

export class QuietHoursDto {
  @IsString()
  start: string; // "22:00"

  @IsString()
  end: string; // "08:00"
}

export class UserPreferencesDto {
  @IsBoolean()
  email_enabled: boolean;

  @IsBoolean()
  push_enabled: boolean;

  @IsBoolean()
  sms_enabled: boolean;

  @IsString()
  language: string; // "en", "es", "fr", etc.

  @IsString()
  timezone: string; // "America/New_York", "Europe/London", etc.

  @IsOptional()
  @ValidateNested()
  @Type(() => QuietHoursDto)
  quiet_hours?: QuietHoursDto;
}

export class UserDataDto {
  @IsString()
  user_id: string;

  @IsEmail()
  email: string;

  @IsOptional()
  @IsString()
  phone?: string;

  @ValidateNested()
  @Type(() => UserPreferencesDto)
  preferences: UserPreferencesDto;

  @IsString()
  created_at: string;

  @IsString()
  updated_at: string;
}

export class PaginationMetaDto {
  total: number;
  limit: number;
  page: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export class UserResponseDto {
  @IsBoolean()
  success: boolean;

  @ValidateNested()
  @Type(() => UserDataDto)
  data: UserDataDto;

  @IsString()
  message: string;

  @ValidateNested()
  @Type(() => PaginationMetaDto)
  meta: PaginationMetaDto;
}