"""Email utilities for sending security alerts."""

import ssl
import logging
import smtplib
import asyncio
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime
from pathlib import Path

# Use the security_monitor logger
logger = logging.getLogger("security_monitor")

# Flag to indicate if email alerts are available
email_alerts_available = True

async def test_email_connection(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    password: str,
    use_tls: bool = True
) -> Tuple[bool, str]:
    """
    Test the email connection settings.
    
    Args:
        smtp_server: SMTP server address
        smtp_port: SMTP server port
        sender_email: Email address to send from
        password: Email password or app-specific password
        use_tls: Whether to use TLS for the connection
        
    Returns:
        Tuple[bool, str]: (Success status, Error message if any)
    """
    try:
        logger.info(f"Testing email connection to {smtp_server}:{smtp_port}")
        logger.info(f"Sender email: {sender_email}")
        logger.info(f"Using TLS: {use_tls}")
        
        context = ssl.create_default_context()
        
        if use_tls:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                logger.debug("Establishing connection...")
                server.starttls(context=context)
                logger.debug("Starting TLS...")
                server.login(sender_email, password)
                logger.info("Login successful!")
        else:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=10) as server:
                logger.debug("Establishing SSL connection...")
                server.login(sender_email, password)
                logger.info("Login successful!")
                
        return True, "Connection test successful"
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Authentication failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPConnectError as e:
        error_msg = f"Connection failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except ssl.SSLError as e:
        error_msg = f"SSL/TLS error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

async def send_email_alert(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    receiver_emails: List[str],
    password: str,
    alert_type: str,
    description: str,
    suspicious_ips: List[str],
    attempt_count: int = 1,
    additional_info: Dict[str, Any] = None,
    use_tls: bool = True
) -> bool:
    """
    Send a security alert email with detailed information.
    
    Args:
        smtp_server: SMTP server address
        smtp_port: SMTP server port
        sender_email: Email address to send from
        receiver_emails: List of email addresses to send to
        password: Email password or app-specific password
        alert_type: Type of security alert
        description: Description of the alert
        suspicious_ips: List of suspicious IP addresses
        attempt_count: Number of attempts
        additional_info: Additional information to include
        use_tls: Whether to use TLS
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        logger.info("Starting email alert sending process...")
        logger.info(f"SMTP Server: {smtp_server}:{smtp_port}")
        logger.info(f"Sender: {sender_email}")
        logger.info(f"Recipients: {receiver_emails}")
        logger.info(f"Alert Type: {alert_type}")
        logger.info(f"Use TLS: {use_tls}")
        
        # Create message container
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Security Alert: {alert_type.replace('_', ' ').title()}"
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_emails)
        
        logger.debug("Created email message container")
        
        # Prepare timestamp and other data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create HTML and text versions of the email
        html = _create_html_email(
            alert_type, 
            description, 
            suspicious_ips, 
            timestamp, 
            attempt_count, 
            additional_info
        )
        
        text = f"""
        SECURITY ALERT: {alert_type.replace('_', ' ').title()}
        
        Time: {timestamp}
        Description: {description}
        Suspicious IPs: {', '.join(suspicious_ips)}
        Attempt Count: {attempt_count}
        
        === SUMMARY ===
        - Total Attempts: {additional_info.get('total_unauthorized_attempts', 1) if additional_info else 1}
        - Total Rate Limit Violations: {additional_info.get('total_rate_limit_violations', 0) if additional_info else 0}
        - Unique IPs Blocked: {len(suspicious_ips)}
        
        === ADDITIONAL INFORMATION ===
        {json.dumps(additional_info, indent=2) if additional_info else 'No additional information'}
        """

        # Attach both versions
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        message.attach(part1)
        message.attach(part2)
        
        logger.debug("Email content prepared and attached to message")

        # Create secure SSL/TLS context
        context = ssl.create_default_context()
        logger.debug("Created SSL/TLS context")

        # Connect to SMTP server and send email
        if use_tls:
            logger.debug(f"Connecting to SMTP server with STARTTLS: {smtp_server}:{smtp_port}")
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                logger.debug("Connection established, starting TLS")
                server.starttls(context=context)
                logger.debug(f"TLS started, attempting login as {sender_email}")
                server.login(sender_email, password)
                logger.debug("Login successful, sending message")
                server.send_message(message)
                logger.debug("Message sent")
        else:
            logger.debug(f"Connecting to SMTP server with SSL: {smtp_server}:{smtp_port}")
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                logger.debug(f"SSL connection established, attempting login as {sender_email}")
                server.login(sender_email, password)
                logger.debug("Login successful, sending message")
                server.send_message(message)
                logger.debug("Message sent")

        logger.info(f"Security alert email sent successfully to {len(receiver_emails)} recipients")
        return True

    except Exception as e:
        logger.error(f"Failed to send security alert email: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        # Log additional details for specific error types
        if isinstance(e, smtplib.SMTPAuthenticationError):
            logger.error("Authentication error: Check your email and password")
        elif isinstance(e, smtplib.SMTPConnectError):
            logger.error("Connection error: Check your SMTP server and port")
        elif isinstance(e, ssl.SSLError):
            logger.error("SSL/TLS error: Check your SSL/TLS settings")
        elif isinstance(e, smtplib.SMTPRecipientsRefused):
            logger.error("Recipients refused: Check recipient email addresses")
        elif isinstance(e, smtplib.SMTPSenderRefused):
            logger.error("Sender refused: Check sender email address")
        return False 

def _create_html_email(
    alert_type: str, 
    description: str, 
    suspicious_ips: List[str], 
    timestamp: str, 
    attempt_count: int, 
    additional_info: Dict[str, Any] = None
) -> str:
    """
    Create HTML content for email alert.
    
    Args:
        alert_type: Type of security alert
        description: Description of the alert
        suspicious_ips: List of suspicious IP addresses
        timestamp: Current timestamp
        attempt_count: Number of attempts
        additional_info: Additional information to include
        
    Returns:
        str: HTML content for email
    """
    logger.debug(f"Creating HTML email content for alert type: {alert_type}")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ padding: 20px; }}
            .header {{ background-color: #f44336; color: white; padding: 10px; }}
            .info-table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            .info-table td, .info-table th {{ border: 1px solid #ddd; padding: 8px; }}
            .info-table th {{ padding-top: 12px; padding-bottom: 12px; text-align: left; background-color: #f2f2f2; }}
            .details {{ background-color: #f9f9f9; padding: 10px; margin-top: 20px; }}
            pre {{ background-color: #f5f5f5; padding: 10px; overflow: auto; }}
            .stats {{ margin-top: 20px; }}
            .stats h3 {{ color: #f44336; }}
            .summary {{ background-color: #fff3e0; padding: 15px; margin: 20px 0; border-left: 4px solid #ff9800; }}
            .summary h3 {{ color: #ff9800; margin-top: 0; }}
            .rate-limits {{ background-color: #e3f2fd; padding: 15px; margin: 20px 0; border-left: 4px solid #2196f3; }}
            .rate-limits h3 {{ color: #2196f3; margin-top: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Security Alert: {alert_type.replace('_', ' ').title()}</h2>
                <p>Alert generated at {timestamp}</p>
            </div>
            
            <div class="summary">
                <h3>Alert Summary</h3>
                <p><strong>Event:</strong> {description}</p>
                <p><strong>Latest Impact:</strong> {attempt_count} new attempt(s) from {len(suspicious_ips)} unique IP(s)</p>
                <p><strong>Historical Impact:</strong> {additional_info.get('total_unauthorized_attempts', 1)} total unauthorized attempts</p>
                <p><strong>Time Window:</strong> Last {additional_info.get('time_window_minutes', 60)} minutes</p>
            </div>

            <div class="rate-limits">
                <h3>Security Analysis</h3>
                <p><strong>Total Rate Limit Violations:</strong> {additional_info.get('total_rate_limit_violations', 0)}</p>
                <p><strong>Most Targeted Endpoints:</strong></p>
                <ul>
                    {(''.join(f'<li><strong>{endpoint}</strong>: {count} attempts</li>' for endpoint, count in (additional_info.get('endpoint_attempts', {}).items() if isinstance(additional_info.get('endpoint_attempts', {}), dict) else [(item, 1) for item in additional_info.get('endpoint_attempts', [])]))) if additional_info and 'endpoint_attempts' in additional_info else '<li>No endpoint statistics available</li>'}
                </ul>
                <p><strong>Attack Pattern:</strong> {additional_info.get('attack_pattern', 'Single unauthorized access attempt')}</p>
            </div>

            <div class="content">
                <table class="info-table">
                    <tbody>
                        <tr>
                            <th>Information</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td>Alert Type</td>
                            <td>{alert_type}</td>
                        </tr>
                        <tr>
                            <td>Attempt Count</td>
                            <td>{attempt_count}</td>
                        </tr>
                        <tr>
                            <td>IP Failure Count</td>
                            <td>{additional_info.get('ip_failure_count', 1) if additional_info else 1}</td>
                        </tr>
                        <tr>
                            <td>Total Unauthorized Attempts</td>
                            <td>{additional_info.get('total_unauthorized_attempts', 1) if additional_info else 1}</td>
                        </tr>
                        <tr>
                            <td>Suspicious IPs</td>
                            <td>{', '.join(suspicious_ips)}</td>
                        </tr>
                        <tr>
                            <td>Path</td>
                            <td>{additional_info.get('path', 'N/A') if additional_info else 'N/A'}</td>
                        </tr>
                        <tr>
                            <td>Method</td>
                            <td>{additional_info.get('method', 'N/A') if additional_info else 'N/A'}</td>
                        </tr>
                        <tr>
                            <td>User Agent</td>
                            <td>{additional_info.get('user_agent', 'N/A') if additional_info else 'N/A'}</td>
                        </tr>
                        <tr>
                            <td>Alert Time</td>
                            <td>{timestamp}</td>
                        </tr>
                    </tbody>
                </table>
    
                <div class="stats">
                    <h3>Security Statistics</h3>
                    <table class="info-table">
                        <tbody>
                            <tr>
                                <th>Category</th>
                                <th>Count</th>
                            </tr>
                            <tr>
                                <td>Total Unauthorized Attempts</td>
                                <td>{additional_info.get('total_unauthorized_attempts', 1) if additional_info else 1}</td>
                            </tr>
                            <tr>
                                <td>Total Rate Limit Violations</td>
                                <td>{additional_info.get('total_rate_limit_violations', 0) if additional_info else 0}</td>
                            </tr>
                            <tr>
                                <td>Unique IPs Blocked</td>
                                <td>{len(suspicious_ips)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
    
                <div class="details">
                    <h3>Additional Details</h3>
                    <pre>{json.dumps(additional_info, indent=2, default=str) if additional_info else 'No additional information'}</pre>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    logger.debug("HTML email content created successfully")
    return html 

def _read_template(template_name: str) -> str:
    """
    Read an HTML template file.
    
    Args:
        template_name: Name of the template file
        
    Returns:
        str: Content of the template file
    """
    try:
        # Try multiple possible locations for the template
        possible_paths = [
            f"src/base/utils/templates/{template_name}",
            f"python-new-bp/src/base/utils/templates/{template_name}",
            f"/app/src/base/utils/templates/{template_name}",
            str(Path(__file__).parent / "templates" / template_name)
        ]
        
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as file:
                        logger.debug(f"Found template file at {path}")
                        return file.read()
            except Exception as e:
                logger.warning(f"Error checking path {path}: {str(e)}")
                
        # Fallback to using a simple template string
        logger.warning(f"Could not find template file: {template_name}, using fallback template")
        if template_name == "error_alert.html":
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .header { background-color: #dc3545; color: white; padding: 15px; border-radius: 5px; }
                    .section { background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px; }
                    pre { background-color: #f1f1f1; padding: 10px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Error Alert: {error_type}</h1>
                    <p>Time: {timestamp}</p>
                </div>
                <div class="section">
                    <h2>Error Details</h2>
                    <p>Service: {service_name}</p>
                    <p>Environment: {environment}</p>
                    <p>Message: {error_message}</p>
                    <p>Context: {error_context}</p>
                </div>
                <div class="section">
                    <h2>Stack Trace</h2>
                    <pre>{stack_trace}</pre>
                </div>
            </body>
            </html>
            """
        else:
            # Generic fallback template
            return "<html><body><h1>{error_type}</h1><p>{error_message}</p></body></html>"
    except Exception as e:
        logger.error(f"Error with template processing: {str(e)}")
        return "<html><body><h1>Error Alert</h1><p>An error occurred, but the template could not be loaded.</p></body></html>"

async def send_error_alert(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    receiver_emails: List[str],
    password: str,
    error_type: str,
    error_message: str,
    stack_trace: str = "",
    error_context: str = "",
    service_name: str = "API Service",
    environment: str = "Production",
    error_count_hour: int = 1,
    similar_errors: int = 0,
    total_errors: int = 1,
    severity_level: str = "Medium",
    affected_services: str = "API",
    recommended_action: str = "Investigate the logs for more details",
    additional_info: Dict[str, Any] = None,
    use_tls: bool = True
) -> bool:
    """
    Send an error alert email using the error_alert.html template.
    
    Args:
        smtp_server: SMTP server address
        smtp_port: SMTP server port
        sender_email: Email address to send from
        receiver_emails: List of email addresses to send to
        password: Email password or app-specific password
        error_type: Type of error (e.g., "Database Connection Error")
        error_message: Main error message
        stack_trace: Full stack trace (optional)
        error_context: Context in which the error occurred (optional)
        service_name: Name of the service where the error occurred
        environment: Environment (e.g., "Production", "Development")
        error_count_hour: Number of similar errors in the last hour
        similar_errors: Number of similar errors overall
        total_errors: Total number of errors in the system
        severity_level: Error severity (e.g., "High", "Medium", "Low")
        affected_services: Services affected by the error
        recommended_action: Recommended action to fix the error
        additional_info: Additional information to include
        use_tls: Whether to use TLS
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        logger.info("Starting error alert email sending process...")
        logger.info(f"SMTP Server: {smtp_server}:{smtp_port}")
        logger.info(f"Sender: {sender_email}")
        logger.info(f"Recipients: {receiver_emails}")
        logger.info(f"Error Type: {error_type}")
        
        # Create message container
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Error Alert: {error_type}"
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_emails)
        
        logger.debug("Created email message container for error alert")
        
        # Prepare timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Read the error alert template
        template = _read_template("error_alert.html")
        
        # Ensure all required variables are present and have default values
        template_vars = {
            "timestamp": timestamp,
            "error_type": error_type,
            "service_name": service_name or "API Service",
            "environment": environment or "Production",
            "error_message": error_message or "No error message available",
            "error_context": error_context or "Not available",
            "stack_trace": stack_trace or "Not available",
            "error_count_hour": str(error_count_hour),
            "similar_errors": str(similar_errors),
            "total_errors": str(total_errors),
            "severity_level": severity_level or "Medium",
            "affected_services": affected_services or "API",
            "recommended_action": recommended_action or "Investigate the logs for more details"
        }
        
        # Create HTML content by filling in the template
        html = template
        for key, value in template_vars.items():
            html = html.replace("{" + key + "}", str(value))
        
        # Create plain text version
        text = f"""
        ERROR ALERT: {error_type}
        
        Time: {timestamp}
        Service: {service_name}
        Environment: {environment}
        
        Error Message:
        {error_message}
        
        Stack Trace:
        {stack_trace or "Not available"}
        
        Context:
        {error_context or "Not available"}
        
        === ERROR STATISTICS ===
        - Occurrences (Last Hour): {error_count_hour}
        - Similar Errors: {similar_errors}
        - Total System Errors: {total_errors}
        
        === SYSTEM IMPACT ===
        - Severity Level: {severity_level}
        - Affected Services: {affected_services}
        - Recommended Action: {recommended_action}
        
        === ADDITIONAL INFORMATION ===
        {json.dumps(additional_info, indent=2) if additional_info else 'No additional information'}
        """
        
        # Attach both versions
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        message.attach(part1)
        message.attach(part2)
        
        logger.debug("Error alert email content prepared and attached to message")
        
        # Create secure SSL/TLS context
        context = ssl.create_default_context()
        
        # Connect to SMTP server and send email
        if use_tls:
            logger.debug(f"Connecting to SMTP server with STARTTLS: {smtp_server}:{smtp_port}")
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                logger.debug("Connection established, starting TLS")
                server.starttls(context=context)
                logger.debug(f"TLS started, attempting login as {sender_email}")
                server.login(sender_email, password)
                logger.debug("Login successful, sending error alert message")
                server.send_message(message)
                logger.debug("Error alert message sent")
        else:
            logger.debug(f"Connecting to SMTP server with SSL: {smtp_server}:{smtp_port}")
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                logger.debug(f"SSL connection established, attempting login as {sender_email}")
                server.login(sender_email, password)
                logger.debug("Login successful, sending error alert message")
                server.send_message(message)
                logger.debug("Error alert message sent")
                
        logger.info(f"Error alert email sent successfully to {len(receiver_emails)} recipients")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send error alert email: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        # Log additional details for specific error types
        if isinstance(e, smtplib.SMTPAuthenticationError):
            logger.error("Authentication error: Check your email and password")
        elif isinstance(e, smtplib.SMTPConnectError):
            logger.error("Connection error: Check your SMTP server and port")
        elif isinstance(e, ssl.SSLError):
            logger.error("SSL/TLS error: Check your SSL/TLS settings")
        return False 

def process_rate_limit_template(template_content, progress_percentage):
    """
    Pre-process the rate limit alert template to set the progress bar width correctly.
    
    Args:
        template_content: The HTML template content
        progress_percentage: The progress percentage value
        
    Returns:
        The processed template content with the width set correctly
    """
    # Replace the placeholder with the actual percentage in the style attribute
    return template_content.replace(
        'data-width="{progress_percentage}" style="height: 10px; background: linear-gradient(to right, #f39c12, #e67e22); border-radius: 4px; width: 0;"',
        f'style="height: 10px; background: linear-gradient(to right, #f39c12, #e67e22); border-radius: 4px; width: {progress_percentage}%;"'
    ) 