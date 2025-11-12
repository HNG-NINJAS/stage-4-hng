// ============================================================================
// src/push-tokens/dto/register-token.dto.ts
// ============================================================================
import { IsNotEmpty, IsString, IsIn, IsOptional } from 'class-validator';

/**
 * Data Transfer Object for registering a push token
 * Validates device token from push service providers
 */
export class RegisterTokenDto {
  // Device token from FCM, OneSignal, or other push service
  @IsNotEmpty({ message: 'Token is required' })
  @IsString({ message: 'Token must be a string' })
  token!: string;

  // Type of device sending the token
  @IsNotEmpty({ message: 'Device type is required' })
  @IsIn(['ios', 'android', 'web', 'desktop'], {
    message: 'device_type must be one of: ios, android, web, desktop',
  })
  device_type!: string;

  // Optional friendly name for the device
  @IsOptional()
  @IsString({ message: 'Device name must be a string' })
  device_name?: string;
}