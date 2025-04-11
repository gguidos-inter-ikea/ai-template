# Security Logging System

This directory contains the security logging system for tracking and analyzing unauthorized access attempts and other security-related events.

## Overview

The security logging system provides:

1. **Detailed Logging**: Captures detailed information about unauthorized access attempts, including client IP, user agent, request path, and reason for failure.
2. **Structured Logs**: Uses JSON format for logs to make them machine-readable and easily parsable.
3. **Monitoring Tools**: Includes a script to analyze logs for suspicious activity patterns.
4. **Configurable Thresholds**: Allows you to set thresholds for alerting on suspicious activity.
5. **Alert Integration**: Supports sending alerts to Microsoft Teams channels.

## Components

### 1. Security Logger

The `security_logger.py` module provides:

- A dedicated security logger that outputs to both console and file
- Helper functions to log security events with consistent format
- Configuration options for log path, log level, etc.

### 2. JWT Middleware Integration

The JWT verification middleware uses the security logger to track:

- Missing authentication headers
- Invalid authentication headers
- Invalid or expired tokens
- Malformed token payloads
- Token processing errors

### 3. Security Monitoring Script

Located at `src/base/scripts/security_monitor.py`, this script:

- Processes security logs to identify patterns of unauthorized access
- Tracks repeated failures from the same IP address
- Identifies suspicious activity based on configurable thresholds
- Generates reports on unauthorized access attempts
- Can send alerts to Microsoft Teams when thresholds are exceeded

### 4. Teams Alert Integration

The system includes integration with Microsoft Teams for security alerts:

- Send formatted cards with details about unauthorized access attempts
- Configurable thresholds to control when alerts are triggered
- Protection against alert fatigue with cooldown periods
- Visual indicators of severity through card colors

## Configuration

Security logging settings can be configured in your `.env` file:

```ini
# Security logging configuration
SECURITY_LOG_PATH=logs/security.log
SECURITY_LOG_TO_FILE=true
SECURITY_LOG_LEVEL=WARNING

# Security thresholds for monitoring
MAX_AUTH_FAILURES_PER_IP=5
AUTH_FAILURE_WINDOW_SECONDS=300

# Alert configurations
ALERTS_ENABLED=true

# Microsoft Teams webhook configuration
TEAMS_ALERTS_ENABLED=true
TEAMS_WEBHOOK_URL=https://your-tenant.webhook.office.com/webhookb2/your-webhook-id
TEAMS_ALERT_THRESHOLD=10
TEAMS_SUSPICIOUS_IP_THRESHOLD=3
ALERT_COOLDOWN_MINUTES=30
```

## Setting Up Microsoft Teams Alerts

To set up Microsoft Teams alerts for unauthorized access attempts:

1. **Create a Teams Webhook**:
   - Open Microsoft Teams and navigate to the channel where you want to receive alerts
   - Click the "..." menu next to the channel name and select "Connectors"
   - Search for "Incoming Webhook" and click "Configure"
   - Give your webhook a name (e.g., "API Security Alerts") and optionally upload an icon
   - Click "Create" and copy the webhook URL that is generated

2. **Configure the Application**:
   - Add the following to your `.env` file:
     ```
     ALERTS_ENABLED=true
     TEAMS_ALERTS_ENABLED=true
     TEAMS_WEBHOOK_URL=<your-webhook-url>
     ```
   - Adjust the threshold values as needed:
     ```
     TEAMS_ALERT_THRESHOLD=10
     TEAMS_SUSPICIOUS_IP_THRESHOLD=3
     ALERT_COOLDOWN_MINUTES=30
     ```

3. **Test the Configuration**:
   - Run the security monitoring script with the force-alert flag:
     ```bash
     python -m src.base.scripts.security_monitor --alert --force-alert
     ```
   - Check your Teams channel for the test alert

## Usage

### Monitoring Unauthorized Access

You can run the monitoring script manually or set it up as a cron job:

```bash
# Run the monitoring script
python -m src.base.scripts.security_monitor

# Run with a specific log path
python -m src.base.scripts.security_monitor --log-path /path/to/security.log

# Run with alerting enabled
python -m src.base.scripts.security_monitor --alert

# Force an alert (for testing)
python -m src.base.scripts.security_monitor --alert --force-alert
```

### Setting Up Scheduled Monitoring

For production environments, set up a cron job to run the monitoring script regularly:

```bash
# Edit crontab
crontab -e

# Add a job to run every 15 minutes
*/15 * * * * cd /path/to/your/app && python -m src.base.scripts.security_monitor --alert >> /path/to/monitor.log 2>&1
```

### Sample Log Output

Each security log entry contains detailed information in JSON format:

```json
{
  "timestamp": "2023-07-01T12:34:56.789012",
  "event_type": "unauthorized_access",
  "client_ip": "192.168.1.100",
  "path": "/api/v1/protected-resource",
  "method": "GET",
  "reason": "invalid_token",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
  "referer": "https://example.com/login",
  "x_forwarded_for": "203.0.113.195"
}
```

## Best Practices

1. **Regular Monitoring**: Schedule regular monitoring of security logs to identify patterns.
2. **Adjust Thresholds**: Fine-tune the thresholds based on your application's normal traffic patterns.
3. **Log Rotation**: Implement log rotation to prevent log files from growing too large.
4. **Alert Integration**: Connect the monitoring system to your team's alert channels (email, Slack, etc.).
5. **IP Blocking**: Consider implementing automatic IP blocking for sustained suspicious activity.
6. **Alert Fatigue**: Be mindful of alert fatigue - set thresholds appropriately so that your team doesn't start ignoring alerts.
7. **Secure Webhooks**: Treat webhook URLs as secrets and don't commit them to your code repository. 