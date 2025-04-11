#!/usr/bin/env python
"""
Test script to run the error monitor once and check for errors.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.base.scripts.error_monitor import ErrorMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_error_monitor")

async def main():
    """Run the error monitor once."""
    logger.info("Testing error monitor...")
    
    # Create monitor with a low threshold to trigger alert
    monitor = ErrorMonitor(
        error_threshold=1,  # Just 1 error will trigger an alert
        time_window_minutes=60,  # Look at errors from the last hour
        cooldown_minutes=0  # No cooldown for testing
    )
    
    # Scan for errors and alert if needed
    await monitor.check_and_alert()
    
    logger.info("Test completed")

if __name__ == "__main__":
    asyncio.run(main()) 