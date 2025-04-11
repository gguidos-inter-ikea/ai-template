#!/usr/bin/env python
"""
Add a test error to the error log file.

This script adds a single error entry to the errors.log file
for testing the error monitoring system.

Usage:
    python add_test_error.py [--message MESSAGE] [--module MODULE]
"""

import json
import logging
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("add_test_error")

def main():
    """Add a test error to the error log file."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Add a test error to the error log file')
    parser.add_argument('--message', type=str, default='Test error message',
                        help='Error message to add')
    parser.add_argument('--module', type=str, default='test',
                        help='Module name for the error')
    parser.add_argument('--log-path', type=str, default='/app/logs/errors.log',
                        help='Path to the error log file')
    args = parser.parse_args()
    
    # Create error entry
    error_entry = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3],
        "level": "ERROR",
        "logger": f"test.{args.module}",
        "message": args.message,
        "module": args.module,
        "function": "test_function",
        "path": f"/app/src/base/{args.module}/{args.module}.py",
        "line": 42,
        "request_id": f"test-{uuid.uuid4().hex[:8]}",
        "exception": f"Exception: {args.message}"
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(args.log_path), exist_ok=True)
    
    # Write to log file
    with open(args.log_path, 'a') as f:
        f.write(json.dumps(error_entry) + '\n')
    
    logger.info(f"Added error entry to {args.log_path}")
    logger.info(f"Message: {args.message}")
    logger.info(f"Module: {args.module}")

if __name__ == "__main__":
    main() 