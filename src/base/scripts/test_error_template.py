#!/usr/bin/env python
"""
Test script to verify error alert template.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.base.config.config import settings, get_email_recipients
from src.base.utils.email_utils import send_error_alert, _read_template

async def test_error_template():
    """Test the error alert template by sending a test email with all variables filled in."""
    print("Testing error alert template...")
    
    if not settings.email_alerts_enabled:
        print("Email alerts are disabled in settings. Enabling for test...")
    
    # Read the template to verify it exists
    template = _read_template("error_alert.html")
    print(f"Template loaded successfully, length: {len(template)} characters")
    
    # Test variables that should be replaced
    test_data = {
        "error_type": "Test Error",
        "service_name": "Test Service",
        "environment": "Development",
        "error_message": "This is a test error message",
        "error_context": "Testing template variable replacement",
        "stack_trace": "Exception: Test Error\n  at testFunction()\n  at main()",
        "error_count_hour": "42",
        "similar_errors": "15",
        "total_errors": "100",
        "severity_level": "medium",
        "affected_services": "API, Database",
        "recommended_action": "This is a test, no action needed"
    }
    
    # Show template variables that will be replaced
    print("\nTemplate variables to replace:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    try:
        success = await send_error_alert(
            smtp_server=settings.email_smtp_server,
            smtp_port=settings.email_smtp_port,
            sender_email=settings.email_sender,
            receiver_emails=get_email_recipients(),
            password=settings.email_password,
            use_tls=settings.email_use_tls,
            **test_data
        )
        
        if success:
            print("\nTest email sent successfully!")
        else:
            print("\nFailed to send test email.")
            
        return success
    except Exception as e:
        print(f"Error sending test email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    await test_error_template()

if __name__ == "__main__":
    asyncio.run(main()) 