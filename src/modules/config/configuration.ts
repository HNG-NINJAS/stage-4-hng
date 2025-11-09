export default () => ({
  port: parseInt(process.env.PORT ?? '3002', 10),
  database: {
    url: process.env.DATABASE_URL
  }
,
  rabbitmq: {
    url: process.env.RABBITMQ_URL,
    queue: process.env.EMAIL_QUEUE_NAME,
    exchange: process.env.RABBITMQ_EXCHANGE,
    routingkey: process.env.RABBITMQ_ROUTING_KEY,
    prefetchCount: parseInt(process.env.RABBITMQ_PREFETCH ?? '5', 10),
  },
  email: {
    provider: process.env.EMAIL_PROVIDER || 'smtp',
    from: process.env.EMAIL_FROM || 'noreply@notifyhub.com',
    fromName: process.env.EMAIL_TO || 'NotifyHub',
  },

  smtp: {
    mail_host: process.env.MAIL_HOST,
    mail_port: process.env.MAIL_PORT,
    mailUser: process.env.MAIL_USER,
    mailPassword: process.env.MAIL_PASSWORD,
  },
  services:{
    userService: process.env.USER_SERVICE_URL ,
    templateService:process.env.TEMPLATE_SERVICE_URL,
  },
  circuitBreaker:{
    threshhold:parseInt(process.env.CIRCUIT_BREAKER_THRESHHOLD ?? "5",10),
    timeout: parseInt(process.env.CIRCUIT_BREAKER_TIMEOUT ?? "10000",10),
  },
  retry:{
    maxretry: parseInt(process.env.MAX_RETRIES ?? "5", 10),
    delay:parseInt(process.env.RETRY_DELAY ?? "5000" ,10),
}
});
