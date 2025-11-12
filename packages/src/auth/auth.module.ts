// ============================================================================
// FILE: src/auth/auth.module.ts
// ============================================================================
import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { ConfigService } from '@nestjs/config';
import { AuthService } from './auth.service';
import { AuthController } from './auth.controller';
import { JwtStrategy } from './jwt.strategy';
import { UsersModule } from '../users/users.module';

/**
 * AuthModule provides authentication functionality
 * - JWT token generation and validation
 * - Login endpoint
 * - Passport strategies for securing routes
 *
 * Dependencies:
 * - UsersModule: to access user lookup and verification methods
 * - PassportModule: for authentication strategy support
 * - JwtModule: for JWT token creation and validation
 */
@Module({
  imports: [
    // Import UsersModule to access user lookup methods
    UsersModule,

    // Configure Passport with JWT strategy support
    PassportModule.register({
      defaultStrategy: 'jwt',
    }),

    // Configure JWT module with secret from environment
    JwtModule.registerAsync({
      inject: [ConfigService],
      useFactory: (config_service: ConfigService) => ({
        // Secret key for signing tokens
        secret: config_service.get<string>('JWT_SECRET'),
        // Token options
        signOptions: {
          expiresIn: 3600, // 1 hour in seconds
        },
      }),
    }),
  ],
  // Services provided by this module
  providers: [AuthService, JwtStrategy],
  // Controllers exposed by this module
  controllers: [AuthController],
  // Exports for use by other modules
  exports: [AuthService, JwtModule],
})
export class AuthModule {}

