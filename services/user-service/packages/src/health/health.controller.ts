// ============================================================================
// src/health/health.controller.ts - HEALTH CHECK
// ============================================================================
import { Controller, Get } from '@nestjs/common';
import { ApiResponse } from '../common/dto/response.dto';

@Controller()
export class HealthController {
  @Get('health')
  getHealth(): ApiResponse {
    return new ApiResponse(
      true,
      'User Service is healthy',
      {
        status: 'ok',
        timestamp: new Date().toISOString(),
        service: 'user-service',
        version: '1.0.0',
      },
      null,
      {
        total: 1,
        limit: 1,
        page: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    );
  }
}
