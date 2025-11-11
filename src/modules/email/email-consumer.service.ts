import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as amqp from 'amqplib';
import { EmailService } from './email.service';

interface EmailQueueMessage {
  notification_id: string;
  user_id: string;
  type: 'email';
  template_id: string;
  variables: Record<string, string>;
  priority: 'high' | 'normal' | 'low';
  timestamp: string;
  metadata?: any;
}

@Injectable()
export class EmailConsumerService implements OnModuleInit, OnModuleDestroy {
  private logger = new Logger(EmailConsumerService.name);

  private connection: any;
  private channel: amqp.Channel;

  constructor(
    private readonly configService: ConfigService,
    private readonly emailService: EmailService,
  ) {}

  async onModuleInit() {
    await this.connectToRabbitMQ();
    await this.startConsuming();
  }

  private async connectToRabbitMQ(retryAttempt = 0) {
    const uri = this.configService.get<string>('RABBITMQ_URL')!;
    const retryDelay = this.configService.get<number>('RABBITMQ_RECONNECT_DELAY') ?? 5000;

    try {
      this.connection = await amqp.connect(uri);
      this.channel = await this.connection.createChannel();

      this.logger.log('✅ Connected to RabbitMQ');

      // Handle connection errors
      this.connection.on('error', (err) => {
        this.logger.error('RabbitMQ connection error:', err);
      });

      // Reconnect on close
      this.connection.on('close', async () => {
        const backoff = Math.min(retryDelay * Math.pow(2, retryAttempt), 30000);
        this.logger.warn(`RabbitMQ connection closed. Reconnecting in ${backoff}ms...`);
        setTimeout(() => this.connectToRabbitMQ(retryAttempt + 1), backoff);
      });
    } catch (err) {
      const backoff = Math.min(retryDelay * Math.pow(2, retryAttempt), 30000);
      this.logger.error(`Failed to connect to RabbitMQ, retrying in ${backoff}ms:`, err);
      setTimeout(() => this.connectToRabbitMQ(retryAttempt + 1), backoff);
    }
  }

  private async startConsuming() {
    const queueName = this.configService.get<string>('RABBITMQ_QUEUE') ?? 'email_queue';
    const prefetchCount = this.configService.get<number>('RABBITMQ_PREFETCHCOUNT') ?? 10;
    const maxRetries = this.configService.get<number>('RETRY_MAX_RETRIES') ?? 5;
    const retryBaseDelay = this.configService.get<number>('RETRY_BASE_DELAY') ?? 1000;

    // Ensure the queue exists
    await this.channel.assertQueue(queueName, { durable: true });
    this.channel.prefetch(prefetchCount);

    // Optional: Dead-letter queue
    const dlqName = `${queueName}_dlq`;
    await this.channel.assertQueue(dlqName, { durable: true });

    this.logger.log(`📥 Consuming messages from queue: ${queueName}`);

    this.channel.consume(
      queueName,
      async (msg) => {
        if (!msg) return;

        try {
          const message: EmailQueueMessage = JSON.parse(msg.content.toString());
          this.logger.log(`Received message: ${message.notification_id}`);

          // Process the email
          await this.emailService.processEmail(message);

          // ACK message
          this.channel.ack(msg);
          this.logger.log(`Processed: ${message.notification_id}`);
        } catch (error) {
          this.logger.error('Error processing message:', error);

          const retryCount = (msg.properties.headers['x-retry-count'] as number) || 0;

          if (retryCount < maxRetries) {
            const delay = retryBaseDelay * Math.pow(2, retryCount);
            this.logger.warn(`Retrying message in ${delay}ms (attempt ${retryCount + 1}/${maxRetries})`);

            setTimeout(() => {
              this.channel.sendToQueue(queueName, msg.content, {
                ...msg.properties,
                headers: { ...msg.properties.headers, 'x-retry-count': retryCount + 1 },
              });
              this.channel.ack(msg);
            }, delay);
          } else {
            // Move to dead-letter queue
            this.logger.error(`💀 Max retries exceeded for message ${msg.content.toString()}. Moving to DLQ.`);
            this.channel.sendToQueue(dlqName, msg.content, msg.properties);
            this.channel.ack(msg);
          }
        }
      },
      { noAck: false },
    );
  }

  async onModuleDestroy() {
    await this.channel?.close();
    await this.connection?.close();
    this.logger.log('Disconnected from RabbitMQ');
  }
}
