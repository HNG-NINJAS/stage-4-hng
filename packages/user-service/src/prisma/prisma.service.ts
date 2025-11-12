// ============================================================================
// src/prisma/prisma.service.ts - DATABASE SERVICE
// ============================================================================
import { Injectable, OnModuleInit, INestApplication } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

/**
 * PrismaService manages the database connection
 */
@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  async onModuleInit() {
    await this.$connect();
  }

  async enableShutdownHooks(app: INestApplication) {
    this.$on('beforeExit' as never, async () => {
      await app.close();
    });
  }
}