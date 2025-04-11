#!/usr/bin/env python
"""
Diagnostic script for email issues.
Provides detailed information about email configuration and attempts
to send a test email.
"""
import asyncio
import os
import sys
import traceback
import socket
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.base.config.config import settings, get_email_recipients

async def diagnose_smtp_connection():
    """Test direct SMTP connectivity without using the email module."""
    print("\n=== TESTING DIRECT SMTP CONNECTIVITY ===")
    smtp_server = settings.email_smtp_server
    smtp_port = settings.email_smtp_port
    
    print(f"Attempting to connect to {smtp_server}:{smtp_port}...")
    
    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        
        # Connect to the server
        result = sock.connect_ex((smtp_server, smtp_port))
        
        if result == 0:
            print(f"✅ Successfully connected to {smtp_server}:{smtp_port}")
        else:
            print(f"❌ Failed to connect to {smtp_server}:{smtp_port},"\
                  f"error code: {result}")
            
        # Clean up
        sock.close()
        
    except Exception as e:
        print(f"❌ Error testing SMTP connection: {str(e)}")
        traceback.print_exc()

async def diagnose_email_config():
    """Diagnose email configuration issues."""
    print("\n=== EMAIL CONFIGURATION DIAGNOSIS ===")
    
    # Check email settings
    print("\nCurrent Email Settings:")
    print(f"  Enabled: {settings.email_alerts_enabled}")
    print(f"  SMTP Server: {settings.email_smtp_server}")
    print(f"  SMTP Port: {settings.email_smtp_port}")
    print(f"  Sender Email: {settings.email_sender}")
    
    # Check password (mask it for security)
    if settings.email_password:
        masked_password = \
            settings.email_password[:2] + "*" * (len(settings.email_password) - 4) +\
            settings.email_password[-2:]
        print(f"  Password: {masked_password}")
    else:
        print("  Password: Not configured")
    
    # Check recipients
    recipients = get_email_recipients()
    print(f"  Recipients: {recipients if recipients else 'None'}")
    print(f"  Use TLS: {settings.email_use_tls}")
    print(f"  Alert Threshold: {settings.email_alert_threshold}")
    print(f"  Suspicious IP Threshold: {settings.email_suspicious_ip_threshold}")
    
    # Validate configuration
    issues = []
    
    if not settings.email_alerts_enabled:
        issues.append("Email alerts are disabled (email_alerts_enabled=False)")
        
    if not settings.email_smtp_server:
        issues.append("SMTP server not configured")
        
    if not settings.email_sender:
        issues.append("Sender email not configured")
        
    if not settings.email_password:
        issues.append("Email password not configured")
        
    if not recipients:
        issues.append("No recipients configured")
    
    # Print validation results
    if issues:
        print("\nConfiguration Issues:")
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("\n✅ Basic configuration looks valid")
    
    # Test SMTP connectivity
    await diagnose_smtp_connection()
    
    # Import email module only if needed to avoid import errors
    if not issues:
        try:
            # Try to import the email module
            print("\nTesting email module import...")
            from src.base.alerts.email_alerts import send_security_email_alert
            print("✅ Email module imported successfully")
            
            # Test sending email
            print("\nAttempting to send test email...")
            try:
                success = await send_security_email_alert(
                    smtp_server=settings.email_smtp_server,
                    smtp_port=settings.email_smtp_port,
                    sender_email=settings.email_sender,
                    receiver_emails=recipients,
                    password=settings.email_password,
                    alert_type="Email Diagnosis",
                    description="This is a test email for diagnosing email issues.",
                    suspicious_ips=["127.0.0.1"],
                    attempt_count=1,
                    additional_info={"test": True, "env": settings.environment},
                    use_tls=settings.email_use_tls
                )
                
                if success:
                    print("✅ Test email sent successfully!")
                else:
                    print("❌ Failed to send test email")
            except Exception as e:
                print(f"❌ Error sending test email: {str(e)}")
                print("\nDetailed error information:")
                traceback.print_exc()
        except Exception as e:
            print(f"❌ Error importing email module: {str(e)}")
            print("\nDetailed error information:")
            traceback.print_exc()

async def main():
    """Run all diagnostics."""
    print("=== EMAIL DIAGNOSIS TOOL ===")
    print(f"Running on Python {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    try:
        await diagnose_email_config()
    except Exception as e:
        print(f"Error during diagnosis: {str(e)}")
        traceback.print_exc()
    
    print("\nDiagnosis complete.")

if __name__ == "__main__":
    asyncio.run(main()) 