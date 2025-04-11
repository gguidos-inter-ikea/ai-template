#!/usr/bin/env python
"""
Error monitoring script that scans error logs and sends alerts.

This module reads the errors.log file, counts errors in a time window,
and sends alerts when the count exceeds a threshold.

Usage:
    python error_monitor.py
"""

import os
import json
import logging
from datetime import datetime, timedelta
import sys
from pathlib import Path
import asyncio
from typing import Dict, List, Any
import argparse
from collections import defaultdict, Counter
import traceback

# Add the project root to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.base.config.config import settings
from src.base.utils.email_utils import send_error_alert
from src.base.logging.security_monitor_logger import (
    log_email_attempt,
    log_email_success,
    log_email_failure,
    log_email_config,
    log_email_details
)

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("error_monitor")

class ErrorMonitor:
    """Monitor for detecting and alerting on application errors."""
    
    def __init__(
            self,
            error_log_path: str = "/app/logs/errors.log",
            error_threshold: int = 5,
            time_window_minutes: int = 30,
            cooldown_minutes: int = 60
        ):
        """Initialize the error monitor."""
        self.error_log_path = error_log_path
        self.error_threshold = error_threshold
        self.time_window = timedelta(minutes=time_window_minutes)
        self.cooldown = timedelta(minutes=cooldown_minutes)
        self.last_alert_time = datetime.min  # Set to minimum time to allow first alert immediately
        
        # Initialize tracking data
        self.error_count = 0
        self.module_error_counts = {}
        self.recent_errors = []
        self.alerts_sent_today = 0
        self.max_alerts_per_day = 5
        self.daily_alert_reset = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Track file position to only process new entries
        self.last_file_position = 0
        self.last_file_size = 0
        self.processed_error_ids = set()  # To track processed errors by unique ID
        self.first_run = True  # Flag for first run
        
        # Flag to control the monitoring loop
        self.is_running = False
        
        # Initialize background task
        self.monitor_task = None
        
        # Initialize email settings
        self._initialize_email_settings()
        
        logger.info(f"Error monitor initialized with log path: {error_log_path}")
        logger.info(f"Error threshold: {error_threshold}")
        logger.info(f"Time window: {time_window_minutes} minutes")
        logger.info(f"Alert cooldown: {cooldown_minutes} minutes")
        logger.info(f"Maximum alerts per day: {self.max_alerts_per_day}")
    
    def _initialize_email_settings(self) -> None:
        """Initialize email settings with validation."""
        try:
            self.email_alerts_enabled = settings.email_alerts_enabled
            self.smtp_server = settings.email_smtp_server
            self.smtp_port = settings.email_smtp_port
            self.email_sender = settings.email_sender
            self.email_password = settings.email_password
            self.email_recipients = settings.email_recipients
            self.use_tls = settings.email_use_tls
            
            # Validate settings
            if not all([
                self.email_alerts_enabled,
                self.smtp_server,
                self.email_sender,
                self.email_password,
                self.email_recipients
            ]):
                logger.warning("Email alerts disabled due to missing configuration")
                self.email_alerts_enabled = False
            else:
                logger.info("Email settings initialized successfully")
                
                # Log email configuration (for consistency with security monitor)
                log_email_config(
                    smtp_server=self.smtp_server,
                    smtp_port=self.smtp_port,
                    sender=self.email_sender,
                    recipients=self.email_recipients,
                    use_tls=self.use_tls
                )
            
        except Exception as e:
            logger.error(f"Error initializing email settings: {str(e)}")
            self.email_alerts_enabled = False
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp from log entry."""
        try:
            # Try format with comma in milliseconds
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
        except ValueError:
            try:
                # Try ISO format
                return datetime.fromisoformat(timestamp_str.replace('Z', ''))
            except ValueError:
                # Use a more lenient approach for other formats
                return datetime.fromisoformat(
                    timestamp_str.replace(' ', 'T').replace('Z', '').replace(',', '.')
                )
    
    def scan_error_logs(self) -> List[Dict[str, Any]]:
        """Scan error logs for recent errors, but only process new entries since last scan."""
        if not os.path.exists(self.error_log_path):
            logger.warning(f"Error log file not found: {self.error_log_path}")
            return []
        
        # Get current file size
        current_file_size = os.path.getsize(self.error_log_path)
        
        # If file hasn't changed or got smaller (log rotation), just return empty
        if current_file_size == self.last_file_size:
            logger.debug(f"File size unchanged ({current_file_size} bytes). No new errors.")
            return []
        
        if current_file_size < self.last_file_size:
            logger.info(f"File size decreased from {self.last_file_size} to {current_file_size} bytes. Log rotation detected.")
            # Reset position since file was likely rotated
            self.last_file_position = 0
            self.processed_error_ids.clear()
        
        # Get cutoff time based on time window
        cutoff_time = datetime.now() - self.time_window
        new_errors = []
        
        try:
            with open(self.error_log_path, 'r') as f:
                # Seek to the last position if we have one
                if self.last_file_position > 0:
                    f.seek(self.last_file_position)
                
                # Read all new lines
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        error = json.loads(line)
                        
                        # Verify this is an error entry
                        if error.get('level') != 'ERROR':
                            continue
                        
                        # Create a unique ID for this error to avoid duplicates
                        error_id = self._create_error_id(error)
                        
                        # Skip if we've already processed this error
                        if error_id in self.processed_error_ids:
                            continue
                        
                        # Add to processed IDs to avoid future duplicates
                        self.processed_error_ids.add(error_id)
                        
                        # Get the timestamp if available
                        timestamp_str = error.get('timestamp')
                        if timestamp_str:
                            try:
                                timestamp = self.parse_timestamp(timestamp_str)
                                # Only include errors within the time window
                                if timestamp >= cutoff_time:
                                    new_errors.append(error)
                                    logger.debug(f"Found new error: {error.get('message')}")
                            except Exception as e:
                                logger.warning(f"Failed to parse timestamp: {timestamp_str}, error: {str(e)}")
                                # Include the error if we can't parse the timestamp to be safe
                                new_errors.append(error)
                                logger.debug(f"Found new error (no timestamp): {error.get('message')}")
                        else:
                            # Include the error if there's no timestamp to be safe
                            new_errors.append(error)
                            logger.debug(f"Found new error (no timestamp): {error.get('message')}")
                    
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse log line as JSON: {line[:100]}...")
                
                # Save our position for next time
                self.last_file_position = f.tell()
                
            # Update file size
            self.last_file_size = current_file_size
            
            if new_errors:
                logger.info(f"Found {len(new_errors)} new errors in the log file")
            else:
                logger.debug("No new errors found in log file")
                
        except Exception as e:
            logger.error(f"Error scanning error logs: {str(e)}")
        
        # Limit the number of processed error IDs to prevent memory growth
        if len(self.processed_error_ids) > 1000:
            logger.debug(f"Pruning processed error ID cache from {len(self.processed_error_ids)} items")
            # Keep only the most recent 500 error IDs
            self.processed_error_ids = set(list(self.processed_error_ids)[-500:])
            logger.debug(f"Processed error ID cache pruned to {len(self.processed_error_ids)} items")
        
        return new_errors
    
    def _create_error_id(self, error: Dict[str, Any]) -> str:
        """Create a unique ID for an error to prevent duplicate processing."""
        # Use a combination of timestamp, message, and module if available
        id_parts = []
        
        if 'timestamp' in error:
            id_parts.append(str(error['timestamp']))
        if 'message' in error:
            id_parts.append(str(error['message']))
        if 'module' in error:
            id_parts.append(str(error['module']))
        if 'line' in error:
            id_parts.append(str(error['line']))
        
        # If we don't have enough parts, use the whole entry
        if len(id_parts) < 2:
            return str(hash(json.dumps(error, sort_keys=True)))
            
        return str(hash('|'.join(id_parts)))
    
    def prepare_alert_data(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare alert data from the list of errors."""
        # Count errors by module
        module_counts = defaultdict(int)
        error_types = []
        error_messages = []
        
        for error in errors:
            # Get module name from the error
            module = error.get('module', 'unknown')
            module_counts[module] += 1
            
            # Get the error type and message
            error_type = error.get('exception', 'Unknown error')
            error_message = error.get('message', 'No message')
            
            if isinstance(error_type, str):
                error_types.append(error_type.split(':')[0] if ':' in error_type else error_type)
            else:
                error_types.append(str(error_type))
                
            error_messages.append(error_message)
        
        # Get the top errors by frequency
        error_type_counts = Counter(error_types)
        error_message_counts = Counter(error_messages)
        top_error_types = error_type_counts.most_common(5)
        top_error_messages = error_message_counts.most_common(5)
        
        # Find a stack trace to include as an example
        example_stack_trace = None
        for error in errors:
            if 'traceback' in error:
                example_stack_trace = error['traceback']
                break
                
        if not example_stack_trace:
            example_stack_trace = "Exception: No stack trace available"
        
        top_error_message = top_error_messages[0][0] if top_error_messages else "Unknown error"
        top_error_type = top_error_types[0][0] if top_error_types else "Unknown type"
        
        return {
            'count': len(errors),
            'module_counts': dict(module_counts),
            'top_errors': top_error_messages,
            'top_types': top_error_types,
            'stack_trace': example_stack_trace,
            'top_error_message': top_error_message,
            'top_error_type': top_error_type
        }
    
    async def check_and_alert(self) -> None:
        """Check for errors and send alerts if needed."""
        try:
            # Reset daily alert counter if needed
            now = datetime.now()
            if now >= self.daily_alert_reset:
                self.alerts_sent_today = 0
                self.daily_alert_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                logger.info(f"Reset daily alert counter. Next reset at {self.daily_alert_reset}")
                
            # Scan for errors in the time window
            errors = self.scan_error_logs()
            error_count = len(errors)
            
            # Log status
            logger.info(f"Found {error_count} errors in the last {self.time_window.total_seconds() / 60} minutes")
            logger.info(f"Error threshold configured: {self.error_threshold}")
            logger.info(f"Error log path: {self.error_log_path}")
            logger.info(f"Alerts sent today: {self.alerts_sent_today}/{self.max_alerts_per_day}")
            
            # Special handling for first run - we want to alert if threshold exceeded, but don't
            # want to consider existing errors as "new" for future runs
            if self.first_run:
                logger.info("First run detected - initializing monitor state")
                self.first_run = False
                # If no errors on first run, we'll just return
                if error_count == 0:
                    logger.info("No errors found on first run. Monitor initialized.")
                    return
                
            # Check if we need to send an alert
            if error_count >= self.error_threshold:
                # Check if we're still in the cooldown period
                cooldown_expired = now - self.last_alert_time > self.cooldown
                
                # Check if we've reached the daily alert limit
                daily_limit_reached = self.alerts_sent_today >= self.max_alerts_per_day
                
                if daily_limit_reached:
                    logger.warning(f"Daily alert limit reached ({self.max_alerts_per_day}). Skipping alert.")
                    return
                    
                if cooldown_expired:
                    time_since_last = now - self.last_alert_time
                    logger.info(f"Cooldown period expired. Time since last alert: {time_since_last.total_seconds() / 60:.1f} minutes")
                    logger.info(f"Error threshold exceeded: {error_count}/{self.error_threshold}. Sending alert.")
                    
                    try:
                        # Prepare alert data
                        alert_data = self.prepare_alert_data(errors)
                        top_error = alert_data.get('top_error_message')
                        top_type = alert_data.get('top_error_type')
                        stack_trace = alert_data.get('stack_trace')
                        
                        # Log alert information
                        logger.warning("=" * 80)
                        logger.warning("ERROR ALERT TRIGGERED")
                        logger.warning(f"Error Type: {top_type}")
                        logger.warning(f"Error Message: {top_error}")
                        logger.warning(f"Total Errors: {error_count}")
                        logger.warning("=" * 80)
                        
                        # Send error alert with consistent formatting 
                        await self._send_error_alert({
                            "error_type": top_type,
                            "error_message": top_error,
                            "stack_trace": stack_trace,
                            "error_context": f"Multiple errors detected in the application logs.",
                            "service_name": "API Service",
                            "environment": settings.environment,
                            "error_count_hour": error_count,
                            "similar_errors": sum(alert_data['module_counts'].values()),
                            "total_errors": error_count,
                            "severity_level": "high" if error_count > 20 else "medium" if error_count > 10 else "low",
                            "affected_services": ", ".join(alert_data['module_counts'].keys()),
                            "recommended_action": "Investigate the error logs and fix the underlying issue.",
                            "additional_info": alert_data
                        })
                    except Exception as e:
                        logger.error(f"Failed to send error alert: {str(e)}")
                        logger.error(f"Error type: {type(e).__name__}")
                        logger.error(traceback.format_exc())
                else:
                    time_since_last = now - self.last_alert_time
                    cooldown_remaining = self.cooldown - time_since_last
                    logger.info(f"Error threshold exceeded but in cooldown period. Time since last alert: {time_since_last.total_seconds() / 60:.1f} minutes")
                    logger.info(f"Cooldown remaining: {cooldown_remaining.total_seconds() / 60:.1f} minutes. Skipping alert.")
            else:
                logger.info("Error threshold not exceeded. No alert needed.")
        except Exception as e:
            logger.error(f"Error in check_and_alert: {str(e)}")
            logger.error(traceback.format_exc())
            
    async def _send_error_alert(self, error_data: Dict[str, Any]) -> None:
        """Send an error alert email using the dedicated error alert function."""
        try:
            logger.info("Preparing to send error alert email")
            
            # Check email configuration
            if not self.email_alerts_enabled:
                logger.warning("Email alerts are disabled in configuration")
                return
                
            if not self.email_recipients:
                logger.warning("No email recipients configured")
                return
            
            # Log email configuration
            log_email_config(
                smtp_server=self.smtp_server,
                smtp_port=self.smtp_port,
                sender=self.email_sender,
                recipients=self.email_recipients,
                use_tls=self.use_tls
            )
            
            # Log error details
            logger.info(f"Error Type: {error_data.get('error_type')}")
            logger.info(f"Recipients: {self.email_recipients}")
            
            # Send email with retry logic
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempting to send error alert email (attempt {attempt + 1}/{max_retries})")
                    
                    # Log attempt with the specialized logger
                    for recipient in self.email_recipients:
                        log_email_attempt(
                            recipient=recipient,
                            alert_type=f"error_{error_data.get('error_type', 'unknown').lower().replace(' ', '_')}",
                            event_data=error_data.get('additional_info', {})
                        )
                    
                    success = await send_error_alert(
                        smtp_server=self.smtp_server,
                        smtp_port=self.smtp_port,
                        sender_email=self.email_sender,
                        receiver_emails=self.email_recipients,
                        password=self.email_password,
                        use_tls=self.use_tls,
                        error_type=error_data.get('error_type'),
                        error_message=error_data.get('error_message'),
                        stack_trace=error_data.get('stack_trace', ''),
                        error_context=error_data.get('error_context', ''),
                        service_name=error_data.get('service_name'),
                        environment=error_data.get('environment'),
                        error_count_hour=error_data.get('error_count_hour', 1),
                        similar_errors=error_data.get('similar_errors', 0),
                        total_errors=error_data.get('total_errors', 1),
                        severity_level=error_data.get('severity_level', 'Medium'),
                        affected_services=error_data.get('affected_services', 'API'),
                        recommended_action=error_data.get('recommended_action', 'Investigate the logs'),
                        additional_info=error_data.get('additional_info')
                    )
                    
                    if success:
                        logger.info("Error alert email sent successfully")
                        
                        # Log success with the specialized logger
                        for recipient in self.email_recipients:
                            log_email_success(
                                recipient=recipient,
                                alert_type=f"error_{error_data.get('error_type', 'unknown').lower().replace(' ', '_')}"
                            )
                        
                        self.last_alert_time = datetime.now()
                        self.alerts_sent_today += 1
                        logger.info(f"Error alert processed successfully. Alerts sent today: {self.alerts_sent_today}/{self.max_alerts_per_day}")
                        return
                    else:
                        logger.warning(f"Failed to send error alert email on attempt {attempt + 1}")
                        
                        # Log failure with the specialized logger
                        for recipient in self.email_recipients:
                            log_email_failure(
                                recipient=recipient,
                                alert_type=f"error_{error_data.get('error_type', 'unknown').lower().replace(' ', '_')}",
                                error="Unknown error",
                                attempt=attempt + 1,
                                max_attempts=max_retries
                            )
                except Exception as e:
                    logger.error(f"Error sending error alert email on attempt {attempt + 1}: {str(e)}")
                    logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                    
                    # Log failure with the specialized logger
                    for recipient in self.email_recipients:
                        log_email_failure(
                            recipient=recipient,
                            alert_type=f"error_{error_data.get('error_type', 'unknown').lower().replace(' ', '_')}",
                            error=str(e),
                            attempt=attempt + 1,
                            max_attempts=max_retries
                        )
                    
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                
        except Exception as e:
            logger.error(f"Error in _send_error_alert: {str(e)}")
            logger.error(traceback.format_exc())
            
    def _format_dict(self, d):
        """Format a dictionary for email display."""
        return "\n".join([f"- {k}: {v}" for k, v in d.items()])
        
    def _format_list(self, items):
        """Format a list of tuples for email display."""
        return "\n".join([f"- {item[0]}: {item[1]}" for item in items])
    
    async def _run_monitor(self) -> None:
        """Run the error monitor continuously."""
        logger.info("Starting error monitor loop...")
        
        while self.is_running:
            try:
                await self.check_and_alert()
            except Exception as e:
                logger.error(f"Error in monitor cycle: {str(e)}")
                
            # Wait before next check
            await asyncio.sleep(60)  # Check every minute
    
    async def start(self) -> None:
        """Start the error monitor."""
        try:
            logger.info("Starting error monitor...")
            if self.is_running:
                logger.info("Error monitor is already running.")
                return
                
            self.is_running = True
            
            # Start the monitoring task
            self.monitor_task = asyncio.create_task(self._run_monitor())
            
            logger.info("Error monitor started successfully.")
        except Exception as e:
            logger.error(f"Error starting error monitor: {str(e)}")
            self.is_running = False
            raise

    async def stop(self) -> None:
        """Stop the error monitor gracefully."""
        try:
            logger.info("Stopping error monitor...")
            
            if not self.is_running:
                logger.info("Error monitor is not running.")
                return
                
            self.is_running = False
            
            # Cancel the monitoring task if it exists
            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass
                self.monitor_task = None
                
            logger.info("Error monitor stopped successfully.")
        except Exception as e:
            logger.error(f"Error stopping error monitor: {str(e)}")
            raise

# Create a global instance with default configuration
monitor = ErrorMonitor()

async def main():
    """Run the error monitor."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Monitor error logs and send alerts")
    parser.add_argument("--log-path", help="Path to error log file", default="/app/logs/errors.log")
    parser.add_argument("--threshold", type=int, help="Error threshold", default=5)
    parser.add_argument("--window", type=int, help="Time window in minutes", default=30)
    parser.add_argument("--cooldown", type=int, help="Alert cooldown in minutes", default=60)
    args = parser.parse_args()
    
    # Create and run the monitor
    custom_monitor = ErrorMonitor(
        error_log_path=args.log_path,
        error_threshold=args.threshold,
        time_window_minutes=args.window,
        cooldown_minutes=args.cooldown
    )
    
    try:
        # Start the monitor
        await custom_monitor.start()
        
        # Keep the script running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Monitor interrupted by user.")
    finally:
        # Stop the monitor
        await custom_monitor.stop()

if __name__ == "__main__":
    asyncio.run(main()) 