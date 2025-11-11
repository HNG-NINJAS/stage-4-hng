import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
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
export class EmailConsumerService implements OnModuleInit {
  private logger = new Logger(EmailConsumerService.name);
  private connection: amqp.Connection;
  private channel: amqp.Channel;
  constructor(
    private configService: ConfigService,
    private emailService: EmailService,
  ) {}

  async onModuleInit() {
    await this.conectToRabbitMQ();
    await this.startConsuming();
  }
  private async conectToRabbitMQ() {
    try {
      const url = this.configService.get<string>('RABBITMQ_URL');
      this.connection = await amqp.connect(url);
      this.channel = await this.connection.createChannel();
      this.logger.log('Connected to RabbitMQ');
      this.connection.on('error', (err) => {
        this.logger.error(`RabbitMQ connection error:`, err);
      });
      this.connection.on('close', () => {
        this.logger.warn('RabbitMq Connection Closed,Reconnecting....');
        setTimeout(() => this.conectToRabbitMQ(), 5000);
      });
    } catch (err) {
      this.logger.error('Failed to connect to RabbitMQ:', err);
      setTimeout(() => this.conectToRabbitMQ(), 5000);
    }
  }
  private async startConsuming() {
    const queueName = this.configService.get<string>('RABBITMQ_QUEUE');
    const prefetchCount = this.configService.get<number>(
      'RABBITMQ_PREFETCHCOUNT',
    );
    // Ensure the queue exists
    await this.channel.assertQueue(queueName, { durable: true });
    this.channel.prefetch(prefetchCount);
    this.logger.log(`Consume from queue:${queueName}`);
    //consume message
    this.channel.consume(queueName, async (msg) => {
      if (!msg) return;
      try {
        const message: EmailQueueMessage = JSON.parse(msg.content.toString());
        this.logger.log(`Recieved message:${message.notification_id}`);
        //Process email
        await this.emailService.processEmail(message);
        // ACK message
        this.channel.ack(msg);
        this.logger.log(`Processed :${message.notification_id}`);
      } catch (error) {
        this.logger.error('Error processing message:', error);
        const retryCount =
          (msg.properties.headers['x-retry-count'] as number) || 0;
        const maxRetries = this.configService.get<number>('RETRY_MAX_RETRIES')!;
        if (retryCount < maxRetries) {
          const delay =
            Math.pow(2, retryCount) *
            this.configService.get<number>('retry.delay')!;
          this.logger.log(
            `Retrying in ${delay}ms (attempt ${retryCount + 1}/${maxRetries})`,
          );

          setTimeout(() => {
            this.channel.publish('', queueName, msg.content, {
              ...msg.properties,
              headers: {
                ...msg.properties.headers,
                'x-retry-count': retryCount + 1,
              },
            });
            this.channel.ack(msg);
          }, delay);
        } else {
          // Move to dead letter queue
          this.logger.error(`💀 Max retries exceeded. Moving to DLQ`);
          this.channel.nack(msg, false, false);
        }
      }
    },{
        noAck:false
    });
  }

  async onModuleDestroy() {
    await this.channel?.close();
    await this.connection?.close();
    this.logger.log('Disconnected from RabbitMQ');
  }
}
