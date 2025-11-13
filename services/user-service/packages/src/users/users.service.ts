// ============================================================================
// FILE: src/users/users.service.ts
// ============================================================================
import { Injectable, BadRequestException, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateUserDto, UpdateUserDto, UserResponseDto } from './dto';
import * as bcrypt from 'bcryptjs';

/**
 * UsersService handles all user-related business logic
 * - User registration (account creation)
 * - User retrieval by ID or email
 * - User profile updates
 * - User deletion
 */
@Injectable()
export class UsersService {
  constructor(private prisma: PrismaService) {}

  /**
   * Create a new user account
   * Validates email uniqueness and hashes the password
   * Also creates default notification preferences for the user
   *
   * @param create_user_dto - Contains name, email, password
   * @returns The newly created user (without password_hash)
   * @throws BadRequestException if email already exists
   */
  async create(create_user_dto: CreateUserDto): Promise<UserResponseDto> {
    // Check if user with this email already exists
    const existing_user = await this.prisma.user.findUnique({
      where: { email: create_user_dto.email },
    });

    if (existing_user) {
      throw new BadRequestException('Email already registered');
    }

    // Hash the password using bcryptjs (10 salt rounds for security)
    // Higher salt rounds = more secure but slower
    const password_hash = await bcrypt.hash(create_user_dto.password, 10);

    // Create user and their default notification preferences in a transaction
    // This ensures both are created together or neither are created
    const user = await this.prisma.user.create({
      data: {
        name: create_user_dto.name,
        email: create_user_dto.email,
        password_hash, // Store hashed password, not plain text

        // Create default notification preferences (1-to-1 relationship)
        notification_preference: {
          create: {
            email_enabled: true,
            push_enabled: true,
            email_frequency: 'instant',
            push_frequency: 'instant',
          },
        },
      },
      // Select what fields to return (exclude sensitive password_hash)
      select: {
        id: true,
        name: true,
        email: true,
        phone_number: true,
        created_at: true,
        updated_at: true,
      },
    });

    return user;
  }

  /**
   * Find a user by their unique ID
   * Used for retrieving user profile information
   *
   * @param id - User's UUID
   * @returns User data without password
   * @throws NotFoundException if user doesn't exist
   */
  async findById(id: string): Promise<UserResponseDto> {
    const user = await this.prisma.user.findUnique({
      where: { id },
      select: {
        id: true,
        name: true,
        email: true,
        phone_number: true,
        created_at: true,
        updated_at: true,
      },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    return user;
  }

  /**
   * Find a user by email address
   * Used during login to verify credentials
   * This returns password_hash because we need it for password verification
   *
   * @param email - User's email address
   * @returns User with password_hash (for authentication use only)
   * @throws NotFoundException if user doesn't exist
   */
  async findByEmail(email: string) {
    const user = await this.prisma.user.findUnique({
      where: { email },
      select: {
        id: true,
        name: true,
        email: true,
        password_hash: true, // Include password for auth verification
        created_at: true,
        updated_at: true,
      },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    return user;
  }

  /**
   * Verify a password against the user's stored hash
   * Used during login to validate credentials
   *
   * @param plain_password - The password the user provided during login
   * @param password_hash - The hashed password stored in database
   * @returns True if passwords match, false otherwise
   */
  async verifyPassword(plain_password: string, password_hash: string): Promise<boolean> {
    return bcrypt.compare(plain_password, password_hash);
  }

  /**
   * Update user information
   * Can update name, email, or phone number
   * Does NOT allow direct password updates (should use separate endpoint)
   *
   * @param id - User's UUID
   * @param update_user_dto - Partial user data to update
   * @returns Updated user data
   * @throws NotFoundException if user doesn't exist
   * @throws BadRequestException if email already taken by another user
   */
  async update(id: string, update_user_dto: UpdateUserDto): Promise<UserResponseDto> {
    // Verify user exists before updating
    await this.findById(id);

    // If trying to update email, verify it's not already taken
    if (update_user_dto.email) {
      const existing_user = await this.prisma.user.findUnique({
        where: { email: update_user_dto.email },
      });

      if (existing_user && existing_user.id !== id) {
        throw new BadRequestException('Email already in use');
      }
    }

    // Update only the fields provided (partial update)
    const updated_user = await this.prisma.user.update({
      where: { id },
      data: update_user_dto,
      select: {
        id: true,
        name: true,
        email: true,
        phone_number: true,
        created_at: true,
        updated_at: true,
      },
    });

    return updated_user;
  }

  /**
   * Delete a user account and all related data
   * Cascade delete removes notification preferences and push tokens
   *
   * @param id - User's UUID
   * @throws NotFoundException if user doesn't exist
   */
  async delete(id: string): Promise<void> {
    // Verify user exists before attempting deletion
    await this.findById(id);

    // Delete user (cascade will delete related records)
    await this.prisma.user.delete({
      where: { id },
    });
  }

  /**
   * Internal method: Get user by email for service-to-service communication
   * Returns minimal user data for other microservices
   *
   * @param email - User's email address
   * @returns User data or null if not found
   */
  async findByEmailInternal(email: string) {
    return this.prisma.user.findUnique({
      where: { email },
      select: {
        id: true,
        name: true,
        email: true,
        created_at: true,
      },
    });
  }
}