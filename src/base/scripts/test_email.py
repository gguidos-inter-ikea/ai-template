#!/usr/bin/env python
"""
Test script to verify email sending functionality.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.base.config.config import settings, get_email_recipients
from src.base.alerts.email_alerts import send_security_email_alert

async def test_email_sending():
    """Test sending a security email alert."""
    print("Testing email sending functionality...")
    print(f"SMTP Server: {settings.email_smtp_server}")
    print(f"SMTP Port: {settings.email_smtp_port}")
    print(f"Sender: {settings.email_sender}")
    print(f"Recipients: {get_email_recipients()}")
    
    if not settings.email_alerts_enabled:
        print("Email alerts are disabled in settings. Enabling for test...")
    
    if not settings.email_smtp_server or not settings.email_sender or not settings.email_password:
        print("ERROR: Missing required email configuration.")
        print("Please check email_smtp_server, email_sender, and email_password settings.")
        return False
    
    if not get_email_recipients():
        print("ERROR: No email recipients configured.")
        print("Please add at least one recipient in email_recipient1, email_recipient2, or email_recipient3 settings.")
        return False
    
    try:
        success = await send_security_email_alert(
            smtp_server=settings.email_smtp_server,
            smtp_port=settings.email_smtp_port,
            sender_email=settings.email_sender,
            receiver_emails=get_email_recipients(),
            password=settings.email_password,
            alert_type="Test Alert",
            description="This is a test security alert to verify email functionality.",
            suspicious_ips=["192.168.1.1", "10.0.0.1"],
            attempt_count=5,
            additional_info={"test": True, "environment": settings.environment},
            use_tls=settings.email_use_tls
        )
        
        if success:
            print("Test email sent successfully!")
        else:
            print("Failed to send test email.")
            
        return success
    except Exception as e:
        print(f"Error sending test email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_email_sending()) 