import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';
import amqp from 'amqplib';
import { v4 as uuidv4 } from 'uuid';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Configuration
const TEMPLATE_SERVICE_URL = process.env.TEMPLATE_SERVICE_URL || 'http://template-service:3004';
const PUSH_SERVICE_URL = process.env.PUSH_SERVICE_URL || 'http://push-service:3003';
const EMAIL_SERVICE_URL = process.env.EMAIL_SERVICE_URL || 'http://email-service:3005';
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://user-service:3001';
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://admin:admin123@rabbitmq:5672/';

// RabbitMQ connection
let rabbitChannel: amqp.Channel | null = null;

async function connectRabbitMQ() {
    try {
        const connection = await amqp.connect(RABBITMQ_URL);
        rabbitChannel = await connection.createChannel();

        // Declare queues
        await rabbitChannel.assertQueue('push.queue', { durable: true });
        await rabbitChannel.assertQueue('email.queue', { durable: true });

        console.log('✅ Connected to RabbitMQ');
    } catch (error) {
        console.error('❌ RabbitMQ connection failed:', error);
        console.log('⚠️ Will retry in 5 seconds...');
        setTimeout(connectRabbitMQ, 5000);
    }
}

// Logging middleware
app.use((req: Request, res: Response, next: NextFunction) => {
    const correlationId = req.headers['x-correlation-id'] as string || uuidv4();
    req.headers['x-correlation-id'] = correlationId;
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - Correlation ID: ${correlationId}`);
    next();
});

// Root endpoint
app.get('/', (req: Request, res: Response) => {
    res.json({
        service: 'API Gateway',
        version: '1.0.0',
        status: 'running',
        endpoints: {
            push: 'POST /notify/push',
            email: 'POST /notify/email',
            health: 'GET /health'
        }
    });
});

// Health check
app.get('/health', async (req: Request, res: Response) => {
    const health = {
        service: 'api-gateway',
        status: 'healthy',
        timestamp: new Date().toISOString(),
        dependencies: {
            rabbitmq: rabbitChannel ? 'connected' : 'disconnected',
            template_service: 'unknown',
            push_service: 'unknown',
            email_service: 'unknown'
        }
    };

    // Check services
    try {
        await axios.get(`${TEMPLATE_SERVICE_URL}/health`, { timeout: 2000 });
        health.dependencies.template_service = 'healthy';
    } catch (error) {
        health.dependencies.template_service = 'unhealthy';
    }

    try {
        await axios.get(`${PUSH_SERVICE_URL}/health`, { timeout: 2000 });
        health.dependencies.push_service = 'healthy';
    } catch (error) {
        health.dependencies.push_service = 'unhealthy';
    }

    try {
        await axios.get(`${EMAIL_SERVICE_URL}/health`, { timeout: 2000 });
        health.dependencies.email_service = 'healthy';
    } catch (error) {
        health.dependencies.email_service = 'unhealthy';
    }

    res.json(health);
});

// Push notification endpoint
app.post('/notify/push', async (req: Request, res: Response) => {
    try {
        const { user_id, template_id, template_data, device_token, language_code = 'en', priority = 'normal' } = req.body;

        // Validate required fields
        if (!user_id || !template_id || !device_token) {
            return res.status(400).json({
                success: false,
                error: 'VALIDATION_ERROR',
                message: 'Missing required fields: user_id, template_id, device_token'
            });
        }

        const correlationId = req.headers['x-correlation-id'] as string;
        const messageId = uuidv4();

        // Publish to RabbitMQ queue
        const message = {
            message_id: messageId,
            correlation_id: correlationId,
            user_id,
            template_id,
            template_data: template_data || {},
            device_token,
            language_code,
            priority,
            retry_count: 0,
            timestamp: new Date().toISOString()
        };

        if (rabbitChannel) {
            rabbitChannel.sendToQueue(
                'push.queue',
                Buffer.from(JSON.stringify(message)),
                { persistent: true }
            );

            console.log(`📤 Push notification queued: ${messageId}`);

            res.status(202).json({
                success: true,
                message: 'Push notification queued successfully',
                data: {
                    message_id: messageId,
                    correlation_id: correlationId,
                    status: 'queued'
                }
            });
        } else {
            throw new Error('RabbitMQ not connected');
        }
    } catch (error: any) {
        console.error('❌ Push notification error:', error);
        res.status(500).json({
            success: false,
            error: 'INTERNAL_ERROR',
            message: error.message || 'Failed to queue push notification'
        });
    }
});

// Email notification endpoint
app.post('/notify/email', async (req: Request, res: Response) => {
    try {
        const { user_id, template_id, template_data, recipient_email, language_code = 'en', priority = 'normal' } = req.body;

        // Validate required fields
        if (!user_id || !template_id || !recipient_email) {
            return res.status(400).json({
                success: false,
                error: 'VALIDATION_ERROR',
                message: 'Missing required fields: user_id, template_id, recipient_email'
            });
        }

        const correlationId = req.headers['x-correlation-id'] as string;
        const messageId = uuidv4();

        // Publish to RabbitMQ queue
        const message = {
            message_id: messageId,
            correlation_id: correlationId,
            user_id,
            template_id,
            template_data: template_data || {},
            recipient_email,
            language_code,
            priority,
            retry_count: 0,
            timestamp: new Date().toISOString()
        };

        if (rabbitChannel) {
            rabbitChannel.sendToQueue(
                'email.queue',
                Buffer.from(JSON.stringify(message)),
                { persistent: true }
            );

            console.log(`📤 Email notification queued: ${messageId}`);

            res.status(202).json({
                success: true,
                message: 'Email notification queued successfully',
                data: {
                    message_id: messageId,
                    correlation_id: correlationId,
                    status: 'queued'
                }
            });
        } else {
            throw new Error('RabbitMQ not connected');
        }
    } catch (error: any) {
        console.error('❌ Email notification error:', error);
        res.status(500).json({
            success: false,
            error: 'INTERNAL_ERROR',
            message: error.message || 'Failed to queue email notification'
        });
    }
});

// Start server
async function start() {
    await connectRabbitMQ();

    app.listen(PORT, () => {
        console.log('='.repeat(50));
        console.log(`🚀 API Gateway running on port ${PORT}`);
        console.log(`📍 Environment: ${process.env.NODE_ENV || 'development'}`);
        console.log('='.repeat(50));
    });
}

start();
