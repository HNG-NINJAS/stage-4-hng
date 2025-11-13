// ============================================================================
// FILE: src/users/users.module.ts
// ============================================================================
import { Module } from '@nestjs/common';
import { UsersService } from './users.service';
import { UsersController } from './users.controller';
import { PrismaService } from '../prisma/prisma.service';

/**
 * UsersModule provides user management functionality
 * - User registration and profile management
 * - User retrieval and updates
 */
@Module({
  providers: [UsersService, PrismaService],
  controllers: [UsersController],
  exports: [UsersService],
})
export class UsersModule {}