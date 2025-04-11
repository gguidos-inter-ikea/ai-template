"""Slack utilities for sending security alerts."""

import json
import logging
import requests
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

slack_alerts_available = True

def send_slack_alert(
    webhook_url: str,
    alert_type: str,
    description: str,
    suspicious_ips: List[str],
    attempt_count: int,
    additional_info: Dict[str, Any]
) -> bool:
    """Send a security alert to Slack."""
    try:
        # Create Slack message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Security Alert: {alert_type}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:* {description}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Suspicious IPs:*\n{', '.join(suspicious_ips) if suspicious_ips else 'None'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Attempt Count:*\n{attempt_count}"
                    }
                ]
            }
        ]

        # Add additional info
        if additional_info:
            fields = []
            for key, value in additional_info.items():
                fields.append({
                    "type": "mrkdwn",
                    "text": f"*{key}:*\n{value}"
                })
            blocks.append({
                "type": "section",
                "fields": fields
            })

        # Send to Slack
        response = requests.post(
            webhook_url,
            json={"blocks": blocks},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        logger.info("Security alert sent to Slack")
        return True

    except Exception as e:
        logger.error(f"Failed to send Slack alert: {str(e)}")
        return False 