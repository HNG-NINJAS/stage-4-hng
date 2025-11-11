import {
  Injectable,
  Logger,
  HttpException,
  HttpStatus,
  OnModuleInit,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom, catchError, timeout, retry } from 'rxjs';
import { AxiosError, AxiosResponse } from 'axios';
import { IUser, IUserResponse } from '../user-client/interface/user.interface';

@Injectable()
export class UserClientService implements OnModuleInit {
  private readonly logger = new Logger(UserClientService.name);
  private readonly baseUrl: string;
  private readonly timeout: number = 5000;
  private readonly maxRetries: number = 3;

  constructor(
    private configService: ConfigService,
    private httpService: HttpService,
  ) {
    this.baseUrl = this.configService.get<string>('services.userService')!!;
  }

  onModuleInit() {
    this.logger.log(`User Service Client initialized: ${this.baseUrl}`);
  }

  /**
   * Get user by ID
   */
  async getUserById(user_id: string): Promise<IUser> {
    try {
      this.logger.log(`Fetching user: ${user_id}`);

      const response = await firstValueFrom(
        this.httpService
          .get<IUserResponse>(`${this.baseUrl}/api/users/${user_id}`, {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              'X-Service-Name': 'email-service',
            },
          })
          .pipe(
            timeout(this.timeout),
            retry({ count: 2, delay: 1000 }),
            catchError((error: AxiosError) => {
              return this.handleError(error, `fetch user ${user_id}`);
            }),
          ),
      );

      this.validateResponse(response);

      this.logger.log(
        `✅ User fetched successfully: ${response.data.data.email}`,
      );

      return response.data.data;
    } catch (error) {
      this.logger.error(`Error fetching user ${user_id}:`, error.message);
      throw error;
    }
  }

  /**
   * Get user preferences by user ID
   */
  async getUserPreferences(user_id: string) {
    const user = await this.getUserById(user_id);
    return user.preferences;
  }

  /**
   * Check if user has email notifications enabled
   */
  async isEmailEnabled(user_id: string): Promise<boolean> {
    try {
      const preferences = await this.getUserPreferences(user_id);
      return preferences.email_enabled;
    } catch (error) {
      this.logger.error(
        `Error checking email preference for user ${user_id}:`,
        error.message,
      );
      throw error;
    }
  }

  /**
   * Check if current time is within user's quiet hours
   */
  async isInQuietHours(user_id: string): Promise<boolean> {
    try {
      const preferences = await this.getUserPreferences(user_id);

      if (!preferences.quiet_hours) {
        return false;
      }

      const now = new Date();
      const currentTime = now.toTimeString().slice(0, 5); // "HH:MM"

      const { start, end } = preferences.quiet_hours;

      // Handle quiet hours that span midnight
      if (start < end) {
        return currentTime >= start && currentTime < end;
      } else {
        return currentTime >= start || currentTime < end;
      }
    } catch (error) {
      this.logger.warn(
        `Could not check quiet hours for user ${user_id}, defaulting to false`,
      );
      return false;
    }
  }

  /**
   * Validate user can receive email
   */
  async validateUserCanReceiveEmail(user_id: string): Promise<{
    can_receive: boolean;
    reason?: string;
  }> {
    try {
      const user = await this.getUserById(user_id);

      // Check if email enabled
      if (!user.preferences.email_enabled) {
        return {
          can_receive: false,
          reason: 'User has disabled email notifications',
        };
      }

      // Check quiet hours
      const inQuietHours = await this.isInQuietHours(user_id);
      if (inQuietHours) {
        return {
          can_receive: false,
          reason: 'User is in quiet hours',
        };
      }

      // Validate email format
      if (!this.isValidEmail(user.email)) {
        return {
          can_receive: false,
          reason: 'Invalid email address',
        };
      }

      return { can_receive: true };
    } catch (error) {
      this.logger.error(
        `Error validating user ${user_id}:`,
        error.message,
      );
      throw error;
    }
  }

  /**
   * Batch get users by IDs
   */
  async getUsersByIds(user_ids: string[]): Promise<IUser[]> {
    try {
      this.logger.log(`Fetching ${user_ids.length} users in batch`);

      const promises = user_ids.map((user_id) => this.getUserById(user_id));
      const results = await Promise.allSettled(promises);

      const users: IUser[] = [];
      const failed: string[] = [];

      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          users.push(result.value);
        } else {
          failed.push(user_ids[index]);
          this.logger.warn(
            `Failed to fetch user ${user_ids[index]}: ${result.reason}`,
          );
        }
      });

      if (failed.length > 0) {
        this.logger.warn(
          `Failed to fetch ${failed.length} users: ${failed.join(', ')}`,
        );
      }

      this.logger.log(`✅ Successfully fetched ${users.length} users`);

      return users;
    } catch (error) {
      this.logger.error('Error in batch user fetch:', error.message);
      throw error;
    }
  }

  /**
   * Get user's preferred language
   */
  async getUserLanguage(user_id: string): Promise<string> {
    try {
      const preferences = await this.getUserPreferences(user_id);
      return preferences.language || 'en';
    } catch (error) {
      this.logger.warn(
        `Could not get language for user ${user_id}, defaulting to 'en'`,
      );
      return 'en';
    }
  }

  /**
   * Get user's timezone
   */
  async getUserTimezone(user_id: string): Promise<string> {
    try {
      const preferences = await this.getUserPreferences(user_id);
      return preferences.timezone || 'UTC';
    } catch (error) {
      this.logger.warn(
        `Could not get timezone for user ${user_id}, defaulting to 'UTC'`,
      );
      return 'UTC';
    }
  }

  /**
   * Health check - verify connection to User Service
   */
  async healthCheck(): Promise<{ status: string; message: string }> {
    try {
      const response = await firstValueFrom(
        this.httpService
          .get(`${this.baseUrl}/health`, {
            timeout: 3000,
          })
          .pipe(
            catchError((error: AxiosError) => {
              throw new HttpException(
                'User service is unavailable',
                HttpStatus.SERVICE_UNAVAILABLE,
              );
            }),
          ),
      );

      return {
        status: 'healthy',
        message: 'User service is reachable',
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: error.message,
      };
    }
  }

  /**
   * Private helper methods
   */

  private validateResponse(response: AxiosResponse<IUserResponse>): void {
    if (!response.data) {
      throw new HttpException(
        'Empty response from User Service',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }

    if (!response.data.success) {
      throw new HttpException(
        response.data.message || 'User service returned error',
        HttpStatus.BAD_REQUEST,
      );
    }

    if (!response.data.data) {
      throw new HttpException(
        'No user data in response',
        HttpStatus.NOT_FOUND,
      );
    }
  }

  private handleError(error: AxiosError, operation: string): never {
    const status = error.response?.status || HttpStatus.INTERNAL_SERVER_ERROR;
    const message =
      (error.response?.data as any)?.message ||
      error.message ||
      'Unknown error';

    this.logger.error(`Failed to ${operation}:`, {
      status,
      message,
      url: error.config?.url,
    });

    // Map common HTTP errors
    switch (status) {
      case 404:
        throw new HttpException(
          `User not found: ${message}`,
          HttpStatus.NOT_FOUND,
        );
      case 400:
        throw new HttpException(
          `Invalid request: ${message}`,
          HttpStatus.BAD_REQUEST,
        );
      case 401:
      case 403:
        throw new HttpException(
          `Authentication failed: ${message}`,
          HttpStatus.UNAUTHORIZED,
        );
      case 429:
        throw new HttpException(
          'Rate limit exceeded',
          HttpStatus.TOO_MANY_REQUESTS,
        );
      case 503:
        throw new HttpException(
          'User service unavailable',
          HttpStatus.SERVICE_UNAVAILABLE,
        );
      default:
        throw new HttpException(
          `User service error: ${message}`,
          status,
        );
    }
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}