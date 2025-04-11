"""
Logger for security monitor operations, especially for email sending.
This logger uses the central logging configuration and writes to security_monitor.log file.
It provides specific methods for tracking email-related events.
"""

import logging
import json
from typing import Dict, Any, List, Optional

# Get the logger from the central logging configuration
logger = logging.getLogger("security_monitor")

def log_email_attempt(
    recipient: str,
    alert_type: str,
    event_data: Dict[str, Any]
) -> None:
    """
    Log an email sending attempt.
    
    Args:
        recipient: Email recipient
        alert_type: Type of alert being sent
        event_data: Event data being included in the email
    """
    logger.info(f"EMAIL ATTEMPT: Sending {alert_type} alert to {recipient}")
    logger.debug(f"Email event data: {json.dumps(event_data, default=str)}")

def log_email_success(
    recipient: str,
    alert_type: str
) -> None:
    """
    Log successful email sending.
    
    Args:
        recipient: Email recipient
        alert_type: Type of alert that was sent
    """
    logger.info(f"EMAIL SUCCESS: Sent {alert_type} alert to {recipient}")

def log_email_failure(
    recipient: str,
    alert_type: str,
    error: str,
    attempt: int,
    max_attempts: int
) -> None:
    """
    Log email sending failure.
    
    Args:
        recipient: Email recipient
        alert_type: Type of alert that failed to send
        error: Error message
        attempt: Current attempt number
        max_attempts: Maximum number of attempts
    """
    logger.error(f"EMAIL FAILURE: Failed to send {alert_type} alert to {recipient} (Attempt {attempt}/{max_attempts})")
    logger.error(f"Error: {error}")

def log_email_config(
    smtp_server: str,
    smtp_port: int,
    sender: str,
    recipients: List[str],
    use_tls: bool
) -> None:
    """
    Log email configuration details.
    
    Args:
        smtp_server: SMTP server address
        smtp_port: SMTP server port
        sender: Sender email address
        recipients: List of recipient email addresses
        use_tls: Whether TLS is enabled
    """
    logger.info(f"EMAIL CONFIG: Server={smtp_server}:{smtp_port}, Sender={sender}, Recipients={recipients}, TLS={use_tls}")

def log_email_details(
    alert_type: str,
    suspicious_ips: List[str],
    attempt_count: int,
    additional_info: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log email content details.
    
    Args:
        alert_type: Type of alert
        suspicious_ips: List of suspicious IP addresses
        attempt_count: Number of attempts
        additional_info: Additional information included in the email
    """
    logger.info(f"EMAIL CONTENT: Type={alert_type}, IPs={suspicious_ips}, Attempts={attempt_count}")
    if additional_info:
        logger.debug(f"Additional info: {json.dumps(additional_info, default=str)}") 