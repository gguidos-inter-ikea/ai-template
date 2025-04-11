"""
Microsoft Teams alert integration module.

This module provides functionality to send security alerts to Microsoft Teams
channels via webhooks.
"""
import aiohttp
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

async def send_teams_alert(
    webhook_url: str,
    title: str,
    message: str,
    facts: Optional[List[Dict[str, str]]] = None,
    color: str = "#FF0000",  # Red color by default for alerts
    details: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send an alert to Microsoft Teams via webhook.
    
    Args:
        webhook_url: The Teams webhook URL
        title: Title of the alert
        message: Main message text
        facts: List of facts to display in name/value format
        color: Color of the message card (hex color code)
        details: Additional details to include in the card
        
    Returns:
        bool: True if the alert was sent successfully, False otherwise
    """
    if not webhook_url:
        logger.error("No Teams webhook URL provided")
        return False
        
    # Build Teams card payload
    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": color,
        "summary": title,
        "sections": [
            {
                "activityTitle": title,
                "activitySubtitle": f"Alert generated at {datetime.utcnow().isoformat()}",
                "text": message
            }
        ]
    }
    
    # Add facts if provided
    if facts:
        card["sections"][0]["facts"] = facts
        
    # Add additional sections for details if provided
    if details:
        card["sections"].append({
            "title": "Additional Details",
            "text": json.dumps(details, indent=2)
        })
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=card,
                raise_for_status=True
            ) as response:
                status = response.status
                if status == 200:
                    logger.info(f"Successfully sent Teams alert: {title}")
                    return True
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to send Teams alert. Status: {status}, Response: {response_text}")
                    return False
    except Exception as e:
        logger.error(f"Error sending Teams alert: {str(e)}")
        return False

async def send_security_alert(
    webhook_url: str,
    alert_type: str,
    description: str,
    suspicious_ips: List[str],
    attempt_count: int,
    additional_info: Dict[str, Any]
) -> bool:
    """
    Send a security alert to Microsoft Teams.
    
    Args:
        webhook_url: Teams webhook URL
        alert_type: Type of alert (e.g. "unauthorized_access")
        description: Alert description
        suspicious_ips: List of suspicious IP addresses
        attempt_count: Number of suspicious attempts
        additional_info: Additional information to include
        
    Returns:
        bool: True if alert was sent successfully
    """
    try:
        # Create Teams message card
        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0075FF",
            "summary": f"Security Alert: {alert_type}",
            "sections": [
                {
                    "activityTitle": f"🚨 Security Alert: {alert_type}",
                    "activitySubtitle": f"Alert generated at {datetime.utcnow().isoformat()}",
                    "facts": [
                        {
                            "name": "Description",
                            "value": description
                        },
                        {
                            "name": "Suspicious IPs",
                            "value": ", ".join(suspicious_ips) if suspicious_ips else "None"
                        },
                        {
                            "name": "Attempt Count",
                            "value": str(attempt_count)
                        }
                    ],
                    "markdown": True
                }
            ]
        }
        
        # Add additional info section if provided
        if additional_info:
            card["sections"].append({
                "title": "Additional Information",
                "facts": [
                    {
                        "name": k,
                        "value": str(v)
                    }
                    for k, v in additional_info.items()
                ]
            })

        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=card,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info("Security alert sent successfully to Teams")
                    return True
                else:
                    logger.error(f"Failed to send Teams alert. Status: {response.status}")
                    return False

    except Exception as e:
        logger.error(f"Failed to send Teams alert: {str(e)}")
        return False 