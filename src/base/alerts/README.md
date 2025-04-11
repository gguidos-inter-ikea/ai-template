# Alert System

This directory contains modules for sending alerts about security events and other important system notifications to various destinations.

## Microsoft Teams Integration

The `teams_alerts.py` module provides functionality to send formatted alert messages to Microsoft Teams channels using webhooks.

### Features

- **Formatted Message Cards**: Sends visually appealing and structured message cards to Teams
- **Rich Content**: Includes titles, descriptions, facts lists, and formatted details
- **Color Coding**: Uses color coding to indicate severity (red for critical, amber for warnings)
- **Security-Focused**: Specialized functions for security alerts with context-specific formatting

### Setup Instructions

To set up Microsoft Teams alerts:

1. **Create an Incoming Webhook in Teams**:
   - Open the Teams channel where you want to receive alerts
   - Click the "..." menu next to the channel name
   - Select "Connectors"
   - Find "Incoming Webhook" and click "Configure"
   - Provide a name and icon for your webhook
   - Click "Create" to generate a webhook URL
   - Copy the webhook URL for use in your application

2. **Configure Your Application**:
   - Add the Teams webhook configuration to your `.env` file:
     ```ini
     # Alert configurations
     ALERTS_ENABLED=true
     
     # Microsoft Teams webhook configuration
     TEAMS_ALERTS_ENABLED=true
     TEAMS_WEBHOOK_URL=https://your-tenant.webhook.office.com/webhookb2/your-webhook-id
     TEAMS_ALERT_THRESHOLD=10
     TEAMS_SUSPICIOUS_IP_THRESHOLD=3
     ALERT_COOLDOWN_MINUTES=30
     ```

3. **Test Your Configuration**:
   - Use the security monitoring script with the force-alert option:
     ```bash
     python -m src.base.scripts.security_monitor --alert --force-alert
     ```
   - Verify that the alert appears in your Teams channel

### Programmatic Usage

You can also send Teams alerts from your code:

```python
from src.base.alerts.teams_alerts import send_teams_alert, send_security_alert
import asyncio

async def send_test_alert():
    # Generic alert
    await send_teams_alert(
        webhook_url="your-webhook-url",
        title="System Alert",
        message="This is a test alert from the API",
        facts=[
            {"name": "Server", "value": "api-server-01"},
            {"name": "Time", "value": "2023-07-01 12:34:56"}
        ],
        color="#0078D7"  # Blue for informational alerts
    )
    
    # Security-specific alert
    await send_security_alert(
        webhook_url="your-webhook-url",
        alert_type="Test Alert",
        description="This is a test security alert",
        suspicious_ips=["192.168.1.100", "10.0.0.5"],
        attempt_count=15
    )

# Run the async function
asyncio.run(send_test_alert())
```

### Message Card Format

Teams messages are sent as adaptive cards with the following structure:

```json
{
  "@type": "MessageCard",
  "@context": "http://schema.org/extensions",
  "themeColor": "#FF0000",
  "summary": "Security Alert",
  "sections": [
    {
      "activityTitle": "Security Alert: Suspicious Activity",
      "activitySubtitle": "Alert generated at 2023-07-01T12:34:56.789012",
      "text": "Detected 5 suspicious IPs with unauthorized access attempts",
      "facts": [
        {
          "name": "Unauthorized Attempts",
          "value": "25"
        },
        {
          "name": "Suspicious IPs",
          "value": "192.168.1.100, 10.0.0.5"
        }
      ]
    },
    {
      "title": "Additional Details",
      "text": "{ \"reasons\": { \"invalid_token\": 15, \"missing_auth_header\": 10 } }"
    }
  ]
}
```

## Extending the Alert System

To add support for additional alert destinations:

1. Create a new module in the `alerts` directory (e.g., `slack_alerts.py`, `email_alerts.py`)
2. Implement the alert sending functions
3. Update the configuration in `config.py` to include settings for your new alert destination
4. Modify the security monitoring script to use your new alert functions

## Security Considerations

- **Protect Webhook URLs**: Treat webhook URLs as secrets and never commit them to your repository
- **Rate Limiting**: Be mindful of rate limits imposed by the alerting services
- **Alert Fatigue**: Use thresholds and cooldown periods to prevent alert fatigue 