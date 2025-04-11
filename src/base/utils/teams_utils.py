"""Microsoft Teams utilities for sending security alerts."""

import json
import logging
import requests
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

def send_teams_alert(
    webhook_url: str,
    alert_type: str,
    description: str,
    suspicious_ips: List[str],
    attempt_count: int,
    additional_info: Dict[str, Any]
) -> bool:
    """Send a security alert to Microsoft Teams."""
    try:
        # Create Teams message card
        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": f"Security Alert: {alert_type}",
            "sections": [{
                "activityTitle": f"Security Alert: {alert_type}",
                "activitySubtitle": description,
                "facts": [
                    {
                        "name": "Suspicious IPs",
                        "value": ', '.join(suspicious_ips) if suspicious_ips else 'None'
                    },
                    {
                        "name": "Attempt Count",
                        "value": str(attempt_count)
                    }
                ],
                "markdown": True
            }]
        }

        # Add additional info
        if additional_info:
            facts = []
            for key, value in additional_info.items():
                facts.append({
                    "name": key,
                    "value": str(value)
                })
            card["sections"].append({
                "title": "Additional Information",
                "facts": facts,
                "markdown": True
            })

        # Send to Teams
        response = requests.post(
            webhook_url,
            json=card,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        logger.info("Security alert sent to Teams")
        return True

    except Exception as e:
        logger.error(f"Failed to send Teams alert: {str(e)}")
        return False 