"""
Slack alert integration module.

This module provides functionality to send security alerts to Slack
channels via webhooks.
"""
import aiohttp
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

async def send_slack_alert(
    webhook_url: str,
    title: str,
    message: str,
    fields: Optional[List[Dict[str, str]]] = None,
    color: str = "#ff0000",  # Red color by default for alerts
    footer: Optional[str] = None
) -> bool:
    """
    Send an alert to Slack via webhook.
    
    Args:
        webhook_url: The Slack webhook URL
        title: Title of the alert
        message: Main message text
        fields: List of fields to display in name/value format
        color: Color of the message attachment (hex color code)
        footer: Footer text for the message
        
    Returns:
        bool: True if the alert was sent successfully, False otherwise
    """
    if not webhook_url:
        logger.error("No Slack webhook URL provided")
        return False
        
    # Build Slack message payload
    attachment = {
        "fallback": title,
        "color": color,
        "title": title,
        "text": message,
        "ts": int(datetime.utcnow().timestamp())
    }
    
    # Add fields if provided
    if fields:
        attachment["fields"] = fields
        
    # Add footer if provided
    if footer:
        attachment["footer"] = footer
    
    payload = {
        "attachments": [attachment]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=payload,
                raise_for_status=True
            ) as response:
                status = response.status
                if status == 200:
                    logger.info(f"Successfully sent Slack alert: {title}")
                    return True
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to send Slack alert. Status: {status}, Response: {response_text}")
                    return False
    except Exception as e:
        logger.error(f"Error sending Slack alert: {str(e)}")
        return False

async def send_security_slack_alert(
    webhook_url: str,
    alert_type: str,
    description: str,
    suspicious_ips: List[str],
    attempt_count: int,
    additional_info: Dict[str, Any]
) -> bool:
    """
    Send a security alert to Slack.
    
    Args:
        webhook_url: Slack webhook URL
        alert_type: Type of alert (e.g. "unauthorized_access")
        description: Alert description
        suspicious_ips: List of suspicious IP addresses
        attempt_count: Number of suspicious attempts
        additional_info: Additional information to include
        
    Returns:
        bool: True if alert was sent successfully
    """
    try:
        # Create Slack message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 Security Alert: {alert_type}",
                    "emoji": True
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
                        "text": f"*Time:*\n{datetime.utcnow().isoformat()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Attempt Count:*\n{attempt_count}"
                    }
                ]
            }
        ]

        # Add suspicious IPs section
        if suspicious_ips:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Suspicious IPs:*\n{', '.join(suspicious_ips)}"
                }
            })

        # Add additional info section
        if additional_info:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Additional Information:*\n" + "\n".join(
                        f"• *{k}:* {v}" for k, v in additional_info.items()
                    )
                }
            })

        # Create message payload
        payload = {
            "blocks": blocks,
            "text": f"Security Alert: {alert_type}"  # Fallback text
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info("Security alert sent successfully to Slack")
                    return True
                else:
                    logger.error(f"Failed to send Slack alert. Status: {response.status}")
                    return False

    except Exception as e:
        logger.error(f"Failed to send Slack alert: {str(e)}")
        return False 