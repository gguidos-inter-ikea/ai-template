# Monitoring

This document explains the monitoring setup in the FastAPI Microservice Boilerplate.

## Overview

The boilerplate includes a comprehensive monitoring setup using Prometheus and Grafana. This allows you to monitor the performance and health of your application in real-time.

## Components

### Prometheus

Prometheus is an open-source monitoring and alerting toolkit. It collects metrics from configured targets at given intervals, evaluates rule expressions, displays the results, and can trigger alerts when specified conditions are observed.

### Grafana

Grafana is an open-source platform for monitoring and observability. It allows you to query, visualize, alert on, and understand your metrics no matter where they are stored.

## Metrics Collection

The boilerplate uses the `prometheus-fastapi-instrumentator` package to automatically collect metrics from FastAPI:

```python
from prometheus_fastapi_instrumentator import Instrumentator

# Create the instrumentator
instrumentator = Instrumentator()

# Add it to your app
instrumentator.instrument(app)

# Expose the metrics endpoint
instrumentator.expose(app, endpoint="/internal/metrics", include_in_schema=False)
```

The following metrics are collected automatically:

- **HTTP Request Duration**: Tracks the time taken to process HTTP requests
- **HTTP Request Count**: Counts the number of HTTP requests
- **HTTP Request In Progress**: Tracks the number of in-progress HTTP requests
- **HTTP Response Size**: Measures the size of HTTP responses

## Setup

The monitoring setup is defined in the `docker-compose.yml` file:

```yaml
services:
  # Your API service
  api:
    # ...

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - monitoring
    restart: unless-stopped

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    networks:
      - monitoring
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped
```

## Prometheus Configuration

The Prometheus configuration is defined in the `prometheus.yml` file:

```yaml
global:
  scrape_interval: 15s  # How often to scrape targets

scrape_configs:
  - job_name: 'fastapi_microservice'
    scrape_interval: 5s  # How often to scrape this target
    metrics_path: '/internal/metrics'  # Path to the metrics endpoint
    static_configs:
      - targets: ['microservice:8000']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - 'alertmanager:9093'

rule_files:
  - 'alerts.yml'
```

## Accessing the Dashboards

- **Prometheus**: Access the Prometheus dashboard at http://localhost:9090
- **Grafana**: Access the Grafana dashboard at http://localhost:3000 (default login: admin/admin)

## Setting Up Grafana

After starting the services, you need to set up Grafana:

1. Log in to Grafana at http://localhost:3000 (default credentials: admin/admin)
2. Add a data source:
   - Click on "Add your first data source"
   - Select "Prometheus"
   - Set the URL to "http://prometheus:9090"
   - Click "Save & Test"
3. Import a dashboard:
   - Click on "+" icon and select "Import"
   - Enter dashboard ID 1860 (Node Exporter Full) or upload a custom dashboard JSON
   - Select your Prometheus data source
   - Click "Import"

## Custom Metrics

You can add custom metrics to your application:

```python
from prometheus_client import Counter, Histogram, Gauge

# Create metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
ACTIVE_REQUESTS = Gauge('api_active_requests', 'Active requests', ['method', 'endpoint'])

# Use metrics in your code
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    # Track request count and latency
    method = request.method
    endpoint = request.url.path
    
    # Track active requests
    ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
    
    try:
        # Record request latency
        start_time = time.time()
        response = await call_next(request)
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
        
        # Track request count
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
        
        return response
    finally:
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
```

## Alerting

You can set up alerts in Prometheus by creating an `alerts.yml` file:

```yaml
groups:
  - name: example
    rules:
      - alert: HighRequestLatency
        expr: api_request_latency_seconds{quantile="0.9"} > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High request latency on {{ $labels.instance }}"
          description: "{{ $labels.instance }} has a request latency above 1s (current value: {{ $value }}s)"
```

## Health Checks

The boilerplate includes health check endpoints:

- **/internal/health**: Basic health check that returns 200 OK if the service is running
- **/internal/readiness**: Advanced health check that verifies dependencies like MongoDB are connected

These endpoints can be used by Kubernetes or other orchestration systems to check the health of your service.

## Best Practices

1. **Set up alerting**: Configure alerts to notify you of issues
2. **Monitor resource usage**: Track CPU, memory, and disk usage
3. **Set appropriate thresholds**: Define thresholds based on expected behavior
4. **Regularly review dashboards**: Check dashboards to identify trends
5. **Use logging with metrics**: Combine metrics with logging for better debugging
6. **Monitor dependencies**: Track the health of dependencies like MongoDB and Redis

## Security Monitoring Integration

The security monitoring system exposes the following Prometheus metrics:

- **security_unauthorized_access_total**: Counter of unauthorized access attempts
- **security_rate_limit_violations_total**: Counter of rate limit violations
- **security_suspicious_ip_count**: Gauge of current suspicious IPs
- **security_error_count**: Counter of security-related errors
- **security_alert_sent_total**: Counter of security alerts sent

### Grafana Dashboard

A dedicated security dashboard is available in Grafana that includes:

- **Security Events Overview**:
  - Unauthorized access attempts over time
  - Rate limit violations by endpoint
  - Suspicious IP activity
  - Alert history
  - Error rates and patterns

- **Real-time Monitoring**:
  - Active suspicious IPs
  - Current rate limit status
  - Recent security events
  - Alert status

To import the security dashboard:

1. Log in to Grafana
2. Click "+" and select "Import"
3. Enter dashboard ID 1860 (Security Monitoring Dashboard)
4. Select your Prometheus data source
5. Click "Import"

### Alert Integration

Security alerts are integrated with Prometheus alerting:

```yaml
groups:
  - name: security
    rules:
      - alert: HighUnauthorizedAccess
        expr: rate(security_unauthorized_access_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High rate of unauthorized access attempts"
          description: "{{ $value }} unauthorized access attempts in the last 5 minutes"

      - alert: RateLimitViolations
        expr: rate(security_rate_limit_violations_total[5m]) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High rate of rate limit violations"
          description: "{{ $value }} rate limit violations in the last 5 minutes"
```

## Conclusion

The monitoring setup in the boilerplate provides a solid foundation for monitoring your application. You can extend it with custom metrics and dashboards to suit your specific needs. 