# Monitoring & Observability

Guide for monitoring Template Service in production.

## Health Checks

### Endpoints

#### Health Check
```bash
GET /health
```

Returns overall service health including dependencies:

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "template-service",
    "version": "1.0.0",
    "dependencies": {
      "database": "up",
      "redis": "up",
      "rabbitmq": "up"
    }
  }
}
```

#### Readiness Probe (Kubernetes)
```bash
GET /ready
```

Returns 200 when service is ready to accept traffic.

#### Liveness Probe (Kubernetes)
```bash
GET /live
```

Returns 200 when service is alive.

### Kubernetes Configuration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: template-service
spec:
  containers:
  - name: template-service
    image: template-service:1.0.0
    ports:
    - containerPort: 3004
    livenessProbe:
      httpGet:
        path: /live
        port: 3004
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /ready
        port: 3004
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 3
```

## Prometheus Metrics

### Available Metrics

#### HTTP Metrics
```
# Total HTTP requests
template_http_requests_total{method="POST",endpoint="/api/v1/templates/render",status="200"}

# Request duration
template_http_request_duration_seconds{method="POST",endpoint="/api/v1/templates/render"}
```

#### Template Operations
```
# Total template operations
template_operations_total{operation="create",status="success"}
template_operations_total{operation="render",status="success"}

# Render duration by template
template_render_duration_seconds{template_id="welcome_email"}

# Active templates count
template_active_templates_total
```

#### Cache Metrics
```
# Cache hits/misses
template_cache_hits_total
template_cache_misses_total

# Cache operations
template_cache_operations_total{operation="get",status="hit"}
```

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'template-service'
    static_configs:
      - targets: ['template-service:3004']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Dashboard

Example queries:

```promql
# Request rate
rate(template_http_requests_total[5m])

# Error rate
rate(template_http_requests_total{status=~"5.."}[5m])

# P95 latency
histogram_quantile(0.95, rate(template_http_request_duration_seconds_bucket[5m]))

# Template render success rate
rate(template_operations_total{operation="render",status="success"}[5m])
/ rate(template_operations_total{operation="render"}[5m])

# Active templates
template_active_templates_total
```

## Structured Logging

### Log Format

All logs are JSON-formatted with correlation IDs:

```json
{
  "timestamp": "2025-11-12T10:30:00Z",
  "level": "INFO",
  "service": "template-service",
  "message": "Template rendered successfully",
  "correlation_id": "abc-123",
  "template_id": "welcome_email",
  "duration_ms": 45.2,
  "user_id": "user-456"
}
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical issues requiring immediate attention

### Log Aggregation

#### ELK Stack Configuration

```yaml
# filebeat.yml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
    - add_kubernetes_metadata:
        host: ${NODE_NAME}
        matchers:
        - logs_path:
            logs_path: "/var/lib/docker/containers/"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "template-service-%{+yyyy.MM.dd}"
```

#### Kibana Queries

```
# Find errors for specific correlation ID
correlation_id:"abc-123" AND level:"ERROR"

# Template render failures
message:"Template render failed" AND level:"ERROR"

# Slow renders (>1s)
duration_ms:>1000 AND message:"Template rendered"
```

## Alerting

### Prometheus Alerts

```yaml
# alerts.yml
groups:
- name: template-service
  rules:
  - alert: HighErrorRate
    expr: rate(template_http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate in template-service"
      description: "Error rate is {{ $value }} errors/sec"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(template_http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency in template-service"
      description: "P95 latency is {{ $value }}s"

  - alert: ServiceDown
    expr: up{job="template-service"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Template service is down"

  - alert: DatabaseConnectionFailed
    expr: template_health_check{dependency="database"} == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Database connection failed"

  - alert: LowCacheHitRate
    expr: rate(template_cache_hits_total[5m]) / (rate(template_cache_hits_total[5m]) + rate(template_cache_misses_total[5m])) < 0.7
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Low cache hit rate"
      description: "Cache hit rate is {{ $value }}"
```

### AlertManager Configuration

```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-notifications'
  routes:
  - match:
      severity: critical
    receiver: 'pagerduty'
  - match:
      severity: warning
    receiver: 'slack'

receivers:
- name: 'team-notifications'
  email_configs:
  - to: 'team@example.com'

- name: 'pagerduty'
  pagerduty_configs:
  - service_key: '<pagerduty-key>'

- name: 'slack'
  slack_configs:
  - api_url: '<slack-webhook-url>'
    channel: '#alerts'
```

## Distributed Tracing

### Correlation IDs

Always include correlation IDs in requests:

```bash
curl -X POST http://template-service:3004/api/v1/templates/welcome_email/render \
  -H "X-Correlation-ID: user-signup-123" \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "John"}}'
```

### Jaeger Integration

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

# Use in code
with tracer.start_as_current_span("render_template"):
    result = await render_template(template_id, data)
```

## Performance Monitoring

### Key Metrics to Monitor

1. **Request Rate**: Requests per second
2. **Error Rate**: Percentage of failed requests
3. **Latency**: P50, P95, P99 response times
4. **Cache Hit Rate**: Percentage of cache hits
5. **Database Connection Pool**: Active/idle connections
6. **Memory Usage**: Heap size and GC activity
7. **CPU Usage**: CPU utilization percentage

### SLIs/SLOs

**Service Level Indicators:**
- Availability: 99.9% uptime
- Latency: P95 < 500ms
- Error Rate: < 0.1%
- Cache Hit Rate: > 80%

**Service Level Objectives:**
```yaml
availability:
  target: 99.9%
  window: 30d

latency:
  p95: 500ms
  p99: 1000ms

error_rate:
  target: 0.1%
  window: 1h
```

## Monitoring Checklist

- [ ] Health checks configured
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards created
- [ ] Alerts configured in AlertManager
- [ ] Log aggregation setup (ELK/Loki)
- [ ] Distributed tracing enabled
- [ ] SLIs/SLOs defined
- [ ] On-call rotation established
- [ ] Runbooks documented
- [ ] Incident response plan ready

## Troubleshooting

### High Error Rate

1. Check logs for error patterns
2. Verify database connectivity
3. Check Redis/RabbitMQ status
4. Review recent deployments
5. Check resource utilization

### High Latency

1. Check database query performance
2. Verify cache hit rate
3. Review template complexity
4. Check network latency
5. Analyze slow query logs

### Service Down

1. Check pod/container status
2. Review recent logs
3. Verify database connectivity
4. Check resource limits
5. Review deployment configuration

## Next Steps

- Configure [Deployment](./deployment.md)
- Review [Database Operations](./database.md)
- Set up [Integration](../integration/overview.md)
