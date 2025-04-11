#!/usr/bin/env python
"""
Test script to verify the configuration system.
This will load the configuration and print out values to confirm they're loaded correctly.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set a profile for testing
print("Setting profile to 'dev'")
os.environ["SPRING_PROFILES_ACTIVE"] = "dev"

# Import the settings after setting the profile
from src.base.config.config import settings, PropertyManager, active_profile

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50)

def main():
    """Main test function"""
    print_section("Configuration Test")
    
    # Print the active profile
    print(f"Active Profile: {active_profile}")
    
    # Print some key settings to verify they're loaded correctly
    print("\nGeneral settings:")
    print(f"  Application Name: {settings.application_name}")
    print(f"  Environment: {settings.environment}")
    print(f"  Log Level: {settings.log_level}")
    print(f"  Allowed Admin IPs: {settings.allowed_admin_ips}")
    
    print("\nDatabase settings:")
    print(f"  MongoDB URI: {settings.mongodb_uri}")
    print(f"  MongoDB Database: {settings.mongodb_dbname}")
    
    print("\nRedis settings:")
    print(f"  Redis Host: {settings.redis_host}")
    print(f"  Redis Port: {settings.redis_port}")
    print(f"  Redis URL: {settings.redis_url}")
    
    print("\nSecurity settings:")
    print(f"  JWT Secret Key: {'*' * 8}...{'*' * 8}") # Don't print actual secrets
    print(f"  Alerts Enabled: {settings.alerts_enabled}")
    print(f"  Email Alerts Enabled: {settings.email_alerts_enabled}")
    
    print("\nEmail configuration:")
    print(f"  SMTP Server: {settings.email_smtp_server}")
    print(f"  Email Sender: {settings.email_sender}")
    print(f"  Email Recipients: {settings.email_recipient1}, {settings.email_recipient2}")
    
    # Test immutability
    print_section("Testing Immutability")
    try:
        print("Attempting to modify a setting...")
        settings.application_name = "Modified App Name"
        print("ERROR: Was able to modify a setting!")
    except Exception as e:
        print(f"Correctly prevented modification: {type(e).__name__}: {e}")
    
if __name__ == "__main__":
    main() 