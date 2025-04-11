# Security Monitoring System

A comprehensive security monitoring system that provides real-time monitoring, logging, and alerting for security events and system errors.

## Features

### Log Monitoring
- **Real-time Log Monitoring**: Uses Watchdog to monitor security and rate limit logs in real-time
- **Rotating Log Files**: Automatic log rotation with configurable size limits and backup counts
- **Structured Logging**: JSON-formatted log entries for easy parsing and analysis
- **Multiple Log Types**:
  - Security logs for unauthorized access attempts
  - Rate limit violation logs
  - Error logs for system issues

### Security Event Detection
- **Unauthorized Access Tracking**: 
  - Monitors and logs all unauthorized access attempts
  - Tracks suspicious IPs and their attempt counts
  - Configurable thresholds for triggering alerts
- **Rate Limit Violations**: 
  - Monitors rate limit violations by IP and endpoint
  - Tracks patterns of abuse
  - Configurable thresholds for different endpoints

### Error Monitoring
- **Error Tracking**:
  - Monitors different types of system errors
  - Aggregates errors by type within configurable time windows
  - Tracks error frequency and patterns
- **Error Types**:
  - JSON decode errors in log processing
  - Security log processing errors
  - Rate limit log processing errors
  - File access errors
  - General system errors

### Alert System
- **Multi-Channel Alerts**:
  - Email alerts with detailed HTML formatting
  - Microsoft Teams alerts with rich message cards
  - Slack alerts with formatted messages
- **Configurable Thresholds**:
  - Customizable thresholds for different alert types
  - Separate thresholds for unauthorized access and rate limiting
  - Error-specific thresholds
- **Alert Cooldown**:
  - Prevents alert fatigue
  - Configurable cooldown periods
  - Per-channel cooldown settings

### Statistics and Reporting
- **Security Statistics**:
  - Unauthorized access attempts
  - Rate limit violations
  - Suspicious IP tracking
  - Error frequency and patterns
- **Time-based Analysis**:
  - Configurable time windows for analysis
  - Historical trend tracking
  - Pattern detection

## Configuration

### Environment Variables
```ini
# Alert settings
ALERTS_ENABLED=true
ALERT_COOLDOWN_MINUTES=30

# Email alerts
EMAIL_ALERTS_ENABLED=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SENDER=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=["security@yourcompany.com"]
EMAIL_USE_TLS=true
EMAIL_ALERT_THRESHOLD=1
EMAIL_SUSPICIOUS_IP_THRESHOLD=1

# Teams alerts
TEAMS_ALERTS_ENABLED=false
TEAMS_WEBHOOK_URL=your_teams_webhook_url
TEAMS_ALERT_THRESHOLD=10
TEAMS_SUSPICIOUS_IP_THRESHOLD=3

# Slack alerts
SLACK_ALERTS_ENABLED=false
SLACK_WEBHOOK_URL=your_slack_webhook_url
SLACK_ALERT_THRESHOLD=10
SLACK_SUSPICIOUS_IP_THRESHOLD=3

# Log settings
SECURITY_LOG_PATH=logs/security.log
RATE_LIMIT_LOG_PATH=logs/rate_limiter.log
```

### Log Rotation Settings
- Maximum file size: 10MB
- Number of backup files: 5
- Rotation naming: `security.log.1`, `security.log.2`, etc.
- Encoding: UTF-8

### Error Monitoring Settings
- Error aggregation window: 5 minutes
- Maximum errors before alert: 3
- Auto-cleanup of old error counts

## Usage

### Starting the Monitor
```bash
# Start the security monitor
python -m src.base.scripts.security_monitor

# Start with specific log path
python -m src.base.scripts.security_monitor --log-path /custom/path/security.log

# Force immediate alerts (for testing)
python -m src.base.scripts.security_monitor --force-alert
```

### Log Format

#### Security Log Entry
```json
{
  "event_type": "unauthorized_access",
  "client_ip": "192.168.1.100",
  "reason": "missing_auth_header",
  "timestamp": "2024-03-15T19:52:08.123456"
}
```

#### Rate Limit Log Entry
```json
{
  "event_type": "rate_limit_violation",
  "client_ip": "192.168.1.100",
  "endpoint": "/api/v1/users",
  "timestamp": "2024-03-15T19:52:08.123456"
}
```

#### Error Log Entry
```json
{
  "event_type": "error",
  "error_type": "json_decode_error",
  "error_message": "Invalid JSON format",
  "source": "security_log",
  "timestamp": "2024-03-15T19:52:08.123456"
}
```

## Alert Examples

### Email Alert
- HTML-formatted email with detailed information
- Color-coded severity indicators
- Comprehensive statistics and details
- Responsive design for mobile viewing

### Teams Alert
- Rich message card format
- Color-coded by severity
- Organized sections for different types of information
- Quick statistics and detailed data

### Slack Alert
- Formatted message with sections
- Color-coded by severity
- Bulleted lists for multiple items
- Collapsible detailed information

## Best Practices

1. **Log Management**:
   - Regularly archive old log files
   - Monitor disk space usage
   - Implement log rotation policies

2. **Alert Configuration**:
   - Set appropriate thresholds based on traffic
   - Configure cooldown periods to prevent alert fatigue
   - Use different thresholds for different environments

3. **Error Handling**:
   - Monitor error patterns
   - Investigate recurring errors
   - Update thresholds based on patterns

4. **Security**:
   - Protect log files with appropriate permissions
   - Secure alert webhook URLs
   - Use environment variables for sensitive data

5. **Monitoring**:
   - Regularly check alert effectiveness
   - Review and adjust thresholds
   - Monitor system performance

## Integration

The security monitor integrates with:
- FastAPI application logs
- Rate limiting middleware
- Authentication middleware
- System health monitoring
- Prometheus metrics (optional)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 