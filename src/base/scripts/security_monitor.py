#!/usr/bin/env python
"""
Security monitoring system using Watchdog for real-time log monitoring.

This module monitors security and rate limit log files in real-time,
processes events as they occur, and sends alerts when suspicious activity
is detected.

Usage:
    python security_monitor.py [--log-path PATH] [--alert]
"""

import os
import json
import argparse
import logging
from collections import defaultdict
from datetime import datetime, timedelta
import sys
from pathlib import Path
import asyncio
import traceback
from typing import Dict, Any, Set

# Add the project root to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.base.config.config import settings
from src.base.config.alert_config import AlertConfig
from src.base.utils.email_utils import send_email_alert, send_error_alert
from src.base.logging.security_monitor_logger import (
    log_email_attempt,
    log_email_success,
    log_email_failure,
    log_email_config,
    log_email_details
)

# Get the security_monitor logger
logger = logging.getLogger("security_monitor")

class SecurityMonitor:
    """
    Monitors and analyzes security events in real-time.
    Processes events and sends alerts when suspicious activity is detected.
    """

    # Class-level counters that persist across instances
    _error_count = 0
    _ip_failure_counts = defaultdict(int)
    _rate_limit_violations = defaultdict(int)  # Track violations per endpoint
    _endpoint_attempts = defaultdict(int)  # Track attempts per endpoint
    _historical_events = []  # Store recent events for pattern analysis
    
    def __init__(
            self,
            alert_config: AlertConfig = None,
            security_log_path: str = None,
            rate_limit_log_path: str = None,
            error_log_path: str = None
        ):
        """Initialize the security monitor with configurable paths."""
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize alert configuration
        self.alert_config = alert_config or AlertConfig(
            enabled_logs=settings.monitoring.observable_log_types,
            cooldown_minutes=settings.security.alert_cooldown_minutes
        )
        
        # Initialize log paths with fallbacks
        self.log_paths = {
            'security': security_log_path or "/app/logs/security.log",
            'rate_limit': rate_limit_log_path or "/app/logs/rate_limiter.log",
            'error': error_log_path or "/app/logs/errors.log"
        }
        
        # Ensure log directories exist for enabled logs
        for log_type in self.alert_config.enabled_logs:
            if log_type in self.log_paths:
                os.makedirs(os.path.dirname(self.log_paths[log_type]), exist_ok=True)
        
        # Initialize error tracking with defaults
        self.error_threshold = self.alert_config.unauthorized_access_threshold
        self.alert_cooldown = timedelta(minutes=self.alert_config.cooldown_minutes)
        self.last_alert_time = datetime.min
        
        # Initialize email settings
        self._initialize_email_settings()
        
        # Initialize monitoring state
        self.is_running = False
        
        # Load historical events from enabled log files
        self._load_historical_events()
        
        # Clean up old events periodically
        self._cleanup_old_events()
        
        self.logger.info("Security monitor initialized with configuration:")
        for log_type in self.alert_config.enabled_logs:
            if log_type in self.log_paths:
                self.logger.info(f"  {log_type.title()} log path: %s", self.log_paths[log_type])
        self.logger.info("  Unauthorized access threshold: %d", self.alert_config.unauthorized_access_threshold)
        self.logger.info("  Rate limit threshold: %d", self.alert_config.rate_limit_threshold)
        self.logger.info("  Alert cooldown: %s", self.alert_cooldown)
        self.logger.info("  Time window: %d minutes", self.alert_config.time_window_minutes)
    
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
                self.logger.warning("Email alerts disabled due to missing configuration")
                self.email_alerts_enabled = False
            else:
                self.logger.info("Email settings initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing email settings: {str(e)}")
            self.email_alerts_enabled = False
    
    def _cleanup_old_events(self) -> None:
        """Remove events older than the time window."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=self.alert_config.time_window_minutes)
        
        cleaned_events = []
        for event in self._historical_events:
            try:
                if 'timestamp' in event:
                    # Handle different timestamp formats using our helper method
                    try:
                        event_time = self._get_timestamp_naive(event['timestamp'])
                        # If we were able to parse the timestamp, check it against cutoff time
                        if event_time > cutoff_time:
                            cleaned_events.append(event)
                    except Exception as e:
                        # If there's an error processing the timestamp, log and keep the event
                        self.logger.warning(f"Error processing event timestamp in cleanup: {str(e)}")
                        cleaned_events.append(event)
                        continue
                else:
                    # No timestamp, keep it
                    cleaned_events.append(event)
            except Exception as e:
                # If there's any error processing an event, log and keep it
                self.logger.warning(f"Error processing event in cleanup: {str(e)}")
                cleaned_events.append(event)
                
        self._historical_events = cleaned_events

    def _analyze_attack_pattern(self, event: Dict[str, Any]) -> str:
        """Analyze the pattern of attacks based on recent events."""
        self._cleanup_old_events()
        
        endpoint = event.get('path', 'unknown')
        events_same_endpoint = sum(
            1 for e in self._historical_events
            if e.get('path') == endpoint
        )
        
        if events_same_endpoint > 10:
            return f"Persistent attacks on endpoint {endpoint}"
        elif events_same_endpoint > 5:
            return f"Multiple attempts targeting {endpoint}"
        else:
            return "Single unauthorized access attempt"

    def _load_historical_events(self) -> None:
        """Load recent events from log files for historical analysis."""
        try:
            # Calculate cutoff time based on time window from config
            cutoff_time = datetime.now() - timedelta(minutes=self.alert_config.time_window_minutes)
            self._historical_events = []  # Reset historical events
            
            for log_type in self.alert_config.enabled_logs:
                if log_type not in self.log_paths:
                    continue
                    
                log_path = self.log_paths[log_type]
                if not os.path.exists(log_path):
                    self.logger.warning(f"{log_type.title()} log file not found: {log_path}")
                    continue
                
                self.logger.info(f"Loading historical events from {log_path}")
                
                with open(log_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:  # Skip empty lines
                            continue
                            
                        try:
                            # Try to parse the line as JSON first
                            log_entry = json.loads(line)
                            
                            # Check if this is a security log entry
                            if log_type == 'security' and log_entry.get('event_type') == 'unauthorized_access':
                                # Add log_type if not already present
                                if 'log_type' not in log_entry:
                                    log_entry['log_type'] = 'security'
                                
                                # Parse timestamp
                                timestamp_str = log_entry.get('timestamp')
                                if timestamp_str:
                                    # Handle different timestamp formats
                                    try:
                                        # Get a timezone naive datetime for comparison
                                        event_time = self._get_timestamp_naive(timestamp_str)
                                                
                                        if event_time > cutoff_time:
                                            self._historical_events.append(log_entry)
                                            
                                            # Update counters
                                            client_ip = log_entry.get('client_ip', 'unknown')
                                            endpoint = log_entry.get('path', 'unknown')
                                            SecurityMonitor._ip_failure_counts[client_ip] += 1
                                            SecurityMonitor._error_count += 1
                                            SecurityMonitor._endpoint_attempts[endpoint] += 1
                                    except ValueError as e:
                                        self.logger.warning(f"Could not parse timestamp: {timestamp_str}, error: {str(e)}")
                                    
                            elif log_type == 'rate_limit' and 'rate_limit_exceeded' in str(log_entry):
                                # For rate limit logs
                                if 'log_type' not in log_entry:
                                    log_entry['log_type'] = 'rate_limit'
                                
                                # Parse timestamp
                                timestamp_str = log_entry.get('timestamp')
                                if timestamp_str:
                                    try:
                                        # Get a timezone naive datetime for comparison
                                        event_time = self._get_timestamp_naive(timestamp_str)
                                                
                                        if event_time > cutoff_time:
                                            self._historical_events.append(log_entry)
                                            endpoint = log_entry.get('path', 'unknown')
                                            SecurityMonitor._rate_limit_violations[endpoint] += 1
                                    except ValueError as e:
                                        self.logger.warning(f"Could not parse timestamp: {timestamp_str}, error: {str(e)}")
                            
                            elif log_type == 'error' and log_entry.get('level') == 'ERROR':
                                # Process error logs in JSON format
                                log_entry['log_type'] = 'error'
                                
                                # Parse timestamp
                                timestamp_str = log_entry.get('timestamp')
                                if timestamp_str:
                                    try:
                                        # Get a timezone naive datetime for comparison
                                        event_time = self._get_timestamp_naive(timestamp_str)
                                        
                                        if event_time > cutoff_time:
                                            self._historical_events.append(log_entry)
                                            
                                            # Update error counters
                                            error_module = log_entry.get('module', 'unknown')
                                            if not hasattr(SecurityMonitor, '_module_error_counts'):
                                                SecurityMonitor._module_error_counts = defaultdict(int)
                                                
                                            SecurityMonitor._module_error_counts[error_module] += 1
                                            SecurityMonitor._error_count += 1
                                            self.logger.info(f"Loaded error event from module {error_module}, total error count: {SecurityMonitor._error_count}")
                                    except ValueError as e:
                                        self.logger.warning(f"Could not parse timestamp: {timestamp_str}, error: {str(e)}")
                                
                        except json.JSONDecodeError:
                            # Fall back to older log format parsing for backward compatibility
                            try:
                                # Process different log types with non-JSON format
                                if log_type == 'security' and 'WARNING' in line and 'unauthorized_access' in line:
                                    json_str = line[line.find('{'):line.rfind('}')+1]
                                    event = json.loads(json_str)
                                    event['log_type'] = 'security'
                                    
                                    # Handle different timestamp formats
                                    try:
                                        # First try ISO format
                                        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', ''))
                                    except ValueError:
                                        try:
                                            # Try format with comma in milliseconds
                                            event_time = datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                                        except ValueError:
                                            try:
                                                # Try format with space instead of T
                                                timestamp = event['timestamp'].replace(' ', 'T')
                                                event_time = datetime.fromisoformat(timestamp.replace('Z', ''))
                                            except ValueError:
                                                # If all else fails, use current time
                                                self.logger.warning(f"Could not parse timestamp: {event['timestamp']}")
                                                event_time = datetime.utcnow()
                                    
                                    if event_time > cutoff_time:
                                        self._historical_events.append(event)
                                        
                                        # Update counters
                                        client_ip = event.get('client_ip', 'unknown')
                                        endpoint = event.get('path', 'unknown')
                                        SecurityMonitor._ip_failure_counts[client_ip] += 1
                                        SecurityMonitor._error_count += 1
                                        SecurityMonitor._endpoint_attempts[endpoint] += 1
                                        
                                elif log_type == 'rate_limit' and 'WARNING' in line and 'rate_limit_exceeded' in line:
                                    json_str = line[line.find('{'):line.rfind('}')+1]
                                    event = json.loads(json_str)
                                    event['log_type'] = 'rate_limit'
                                    
                                    # Handle different timestamp formats
                                    try:
                                        # First try ISO format
                                        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', ''))
                                    except ValueError:
                                        try:
                                            # Try format with comma in milliseconds
                                            event_time = datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                                        except ValueError:
                                            try:
                                                # Try format with space instead of T
                                                timestamp = event['timestamp'].replace(' ', 'T')
                                                event_time = datetime.fromisoformat(timestamp.replace('Z', ''))
                                            except ValueError:
                                                # If all else fails, use current time
                                                self.logger.warning(f"Could not parse timestamp: {event['timestamp']}")
                                                event_time = datetime.utcnow()
                                    
                                    if event_time > cutoff_time:
                                        self._historical_events.append(event)
                                        endpoint = event.get('path', 'unknown')
                                        SecurityMonitor._rate_limit_violations[endpoint] += 1
                                        
                                elif log_type == 'error' and 'ERROR' in line:
                                    # Process error logs if needed
                                    pass
                                    
                            except (json.JSONDecodeError, KeyError) as e:
                                self.logger.debug(f"Skipping malformed log line: {e}")
                                continue

            self.logger.info(f"Loaded {len(self._historical_events)} historical events")
            
        except Exception as e:
            self.logger.error(f"Error loading historical events: {str(e)}")

    def _prepare_error_alert_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for error alert email."""
        try:
            # Extract basic error information
            error_type = event.get('message', '').split(':')[0] if ':' in event.get('message', '') else 'System Error'
            error_message = event.get('message', 'Unknown error')
            error_context = f"Module: {event.get('module', 'unknown')}\nFunction: {event.get('function', 'unknown')}\nPath: {event.get('path', 'unknown')}\nLine: {event.get('line', 'unknown')}"
            
            # Get stack trace if available
            stack_trace = event.get('exception', '')
            
            # Count recent errors within the time window
            error_window_minutes = settings.error_window_minutes
            current_time = datetime.utcnow()
            error_cutoff_time = current_time - timedelta(minutes=error_window_minutes)
            
            recent_errors = [
                e for e in self._historical_events
                if e.get('log_type') == 'error' and
                self._get_timestamp_naive(e.get('timestamp')).replace(tzinfo=None) > error_cutoff_time
            ]
            
            error_count_hour = len(recent_errors)
            
            # Count similar errors (same type/module)
            similar_errors = 0
            for err in recent_errors:
                err_msg = err.get('message', '')
                if error_type in err_msg or (event.get('module') and event.get('module') == err.get('module')):
                    similar_errors += 1
            
            # Calculate total errors
            total_errors = 0
            if hasattr(SecurityMonitor, '_module_error_counts'):
                for _, count in SecurityMonitor._module_error_counts.items():
                    total_errors += count
            
            # Determine severity based on error count and frequency
            severity_level = "Low"
            if error_count_hour >= settings.error_threshold * 2:
                severity_level = "High"
            elif error_count_hour >= settings.error_threshold:
                severity_level = "Medium"
            
            # Determine affected services
            affected_services = "API"
            if event.get('module'):
                affected_services = f"{event.get('module')} module"
            
            # Recommend action based on severity
            recommended_action = "Monitor the situation"
            if severity_level == "High":
                recommended_action = "Immediate investigation required. Consider system restart or rollback."
            elif severity_level == "Medium":
                recommended_action = "Investigate the logs and fix the underlying issue."
            
            # Get the environment
            environment = os.environ.get("ENVIRONMENT", "Production")
            
            # Prepare service name
            service_name = "API Service"
            if event.get('module'):
                service_name = f"{event.get('module')} Service"
            
            return {
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace,
                "error_context": error_context,
                "service_name": service_name,
                "environment": environment,
                "error_count_hour": error_count_hour,
                "similar_errors": similar_errors,
                "total_errors": total_errors,
                "severity_level": severity_level,
                "affected_services": affected_services,
                "recommended_action": recommended_action,
                "additional_info": event
            }
        except Exception as e:
            logger.error(f"Error preparing error alert data: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "error_type": "Unknown Error",
                "error_message": str(e),
                "service_name": "Security Monitor",
                "environment": "Production",
                "additional_info": event
            }

    def _get_timestamp_naive(self, timestamp_str: str) -> datetime:
        """
        Parse a timestamp string to a naive datetime object for comparison.
        Handles multiple timestamp formats:
        - ISO format with T (2023-03-17T10:15:23.456)
        - ISO format with space (2023-03-17 10:15:23.456)
        - Format with comma for milliseconds (2023-03-17 10:15:23,456)
        
        Args:
            timestamp_str: Timestamp string to parse
            
        Returns:
            Naive datetime object
            
        Raises:
            ValueError: If timestamp cannot be parsed
        """
        if not timestamp_str:
            raise ValueError("Empty timestamp string")
            
        # Try each format in sequence
        for formatter in [
            # Try format with comma in milliseconds first
            lambda ts: datetime.strptime(ts, '%Y-%m-%d %H:%M:%S,%f'),
            # Try ISO format with Z
            lambda ts: datetime.fromisoformat(ts.replace('Z', '')),
            # Try format with space instead of T
            lambda ts: datetime.fromisoformat(ts.replace(' ', 'T').replace('Z', '')),
            # Try standard ISO format
            lambda ts: datetime.fromisoformat(ts),
        ]:
            try:
                event_time = formatter(timestamp_str)
                # Make sure it's naive for comparison
                if event_time.tzinfo is not None:
                    event_time = event_time.replace(tzinfo=None)
                return event_time
            except (ValueError, TypeError):
                continue
                
        # If all formatters fail, log and raise exception
        self.logger.error(f"Could not parse timestamp with any formatter: {timestamp_str}")
        raise ValueError(f"Could not parse timestamp: {timestamp_str}")

    async def process_security_event(self, event: Dict[str, Any]) -> None:
        """Process a security event and update counters."""
        try:
            event_type = event.get("event_type", "unknown")
            client_ip = event.get("client_ip", "unknown")
            endpoint = event.get("path", "unknown")
            log_type = event.get("log_type", "security")  # Default to security log
            
            self.logger.info(f"Processing {log_type} event: {event_type} from IP {client_ip}")
            
            if log_type not in self.alert_config.enabled_logs:
                self.logger.debug(f"Skipping event from disabled log type: {log_type}")
                return
            
            # Ensure timestamp is in proper format
            if "timestamp" in event:
                try:
                    # First try ISO format
                    event_time = datetime.fromisoformat(event['timestamp'].replace('Z', ''))
                except ValueError:
                    try:
                        # Try format with comma in milliseconds
                        event_time = datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                        # Convert to ISO format for consistency
                        event['timestamp'] = event_time.isoformat()
                    except ValueError:
                        try:
                            # Try format with space instead of T
                            timestamp = event['timestamp'].replace(' ', 'T')
                            event_time = datetime.fromisoformat(timestamp.replace('Z', ''))
                            # Convert to ISO format for consistency
                            event['timestamp'] = event_time.isoformat()
                        except ValueError:
                            # If all else fails, use current time
                            self.logger.warning(f"Could not parse timestamp: {event['timestamp']}")
                            event_time = datetime.utcnow()
                            event['timestamp'] = event_time.isoformat()
            else:
                # Add timestamp if not present
                event_time = datetime.utcnow()
                event['timestamp'] = event_time.isoformat()
            
            # Store event for historical analysis
            self._historical_events.append(event)
            self._cleanup_old_events()
            
            # Special processing for error log types
            if log_type == 'error':
                # Track error patterns by module and path
                error_module = event.get('module', 'unknown')
                error_path = event.get('path', 'unknown')
                error_message = event.get('message', '')
                
                # Update error counters
                if not hasattr(SecurityMonitor, '_module_error_counts'):
                    SecurityMonitor._module_error_counts = defaultdict(int)
                if not hasattr(SecurityMonitor, '_path_error_counts'):
                    SecurityMonitor._path_error_counts = defaultdict(int)
                
                SecurityMonitor._module_error_counts[error_module] += 1
                SecurityMonitor._path_error_counts[error_path] += 1
                SecurityMonitor._error_count += 1
                
                # Log the error pattern detection
                self.logger.info(f"Error pattern detected in module {error_module}: {error_message[:100]}...")
                
                # Check if we should send error alerts
                should_alert = self._should_send_alert(event)
                
                if should_alert:
                    self.logger.info(f"Alert condition met for error in module {error_module}. Sending error alert...")
                    
                    # Prepare error alert data
                    error_data = self._prepare_error_alert_data(event)
                    
                    # Send error alert with the dedicated function
                    await self._send_error_alert(error_data)
                else:
                    self.logger.info(f"No alert triggered for error in module {error_module}")
                
                return
            
            # Process regular security events (not errors)
            # Update class-level counters based on event type
            if event_type == "unauthorized_access" and 'security' in self.alert_config.enabled_logs:
                SecurityMonitor._ip_failure_counts[client_ip] += 1
                SecurityMonitor._error_count += 1
                SecurityMonitor._endpoint_attempts[endpoint] += 1
                
                # Log the updated counts
                self.logger.info(f"Updated counters for {client_ip}: {SecurityMonitor._ip_failure_counts[client_ip]} failures")
                
            elif event_type == "rate_limit_violation" and 'rate_limit' in self.alert_config.enabled_logs:
                SecurityMonitor._rate_limit_violations[endpoint] += 1
                
                # Log the updated rate limit violations
                self.logger.info(f"Updated rate limit violations for {endpoint}: {SecurityMonitor._rate_limit_violations[endpoint]}")
            
            # Check if we should send alerts
            should_alert = self._should_send_alert(event)
            
            if should_alert:
                self.logger.info(f"Alert condition met for {event_type} from {client_ip}. Sending email alert...")
                
                # Prepare alert data with additional context
                alert_data = self._prepare_alert_data(event)
                
                # Send the alert
                await self.send_alerts(alert_data)
            else:
                self.logger.info(f"No alert triggered for {event_type} from {client_ip}")
                
        except Exception as e:
            self.logger.error(f"Error processing security event: {str(e)}")
            self.logger.error("Event data: %s", json.dumps(event, indent=2, default=str))

    async def _send_error_alert(self, error_data: Dict[str, Any]) -> None:
        """Send an error alert email using the dedicated error alert function."""
        try:
            self.logger.info("Preparing to send error alert email")
            
            # Check email configuration
            if not self.email_alerts_enabled:
                self.logger.warning("Email alerts are disabled in configuration")
                return
                
            if not self.email_recipients:
                self.logger.warning("No email recipients configured")
                return
            
            # Log detailed configuration for troubleshooting using specialized logger
            log_email_config(
                smtp_server=self.smtp_server,
                smtp_port=self.smtp_port,
                sender=self.email_sender,
                recipients=self.email_recipients,
                use_tls=self.use_tls
            )
            
            # Log error details
            self.logger.info(f"ERROR ALERT: Type={error_data.get('error_type')}, Service={error_data.get('service_name')}")
            
            # Send email with retry logic
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"Attempting to send error alert email (attempt {attempt + 1}/{max_retries})")
                    
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
                        additional_info=error_data.get('additional_info'),
                        use_tls=self.use_tls
                    )
                    
                    if success:
                        self.logger.info("ERROR ALERT EMAIL SENT SUCCESSFULLY")
                        
                        # Log success with the specialized logger
                        for recipient in self.email_recipients:
                            log_email_success(
                                recipient=recipient,
                                alert_type=f"error_{error_data.get('error_type', 'unknown').lower().replace(' ', '_')}"
                            )
                        
                        self.last_alert_time = datetime.now()
                        self.logger.info(f"Setting last_alert_time to {self.last_alert_time}")
                        return
                    else:
                        self.logger.warning(f"ERROR ALERT EMAIL SEND FAILURE: Failed to send on attempt {attempt + 1}")
                        
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
                    self.logger.error(f"Error sending error alert email on attempt {attempt + 1}: {str(e)}")
                    self.logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                    
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
                        self.logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                
        except Exception as e:
            self.logger.error(f"Error in _send_error_alert: {str(e)}")
            self.logger.error(traceback.format_exc())

    def _prepare_alert_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive alert data including historical analysis."""
        self._cleanup_old_events()
        
        # Start with the original event
        alert_data = dict(event)
        
        # Add current time
        alert_data["alert_time"] = datetime.utcnow().isoformat()
        
        # Count total attempts in the time window
        total_attempts = len(self._historical_events)
        
        # Get endpoint statistics
        endpoint_stats = dict(self._endpoint_attempts)
        
        # Analyze attack pattern
        attack_pattern = self._analyze_attack_pattern(event)
        
        # Get the current endpoint's attempt count
        current_endpoint = event.get('path', 'unknown')
        endpoint_attempt_count = self._endpoint_attempts.get(current_endpoint, 0)
        
        # Get IP failure count
        client_ip = event.get('client_ip', 'unknown')
        ip_failure_count = SecurityMonitor._ip_failure_counts.get(client_ip, 0)
        
        # Get rate limit violations for the endpoint
        rate_limit_violations = SecurityMonitor._rate_limit_violations.get(current_endpoint, 0)
        
        # Add statistics
        alert_data["total_unauthorized_attempts"] = total_attempts
        alert_data["total_rate_limit_violations"] = sum(SecurityMonitor._rate_limit_violations.values())
        alert_data["endpoint_attempts"] = endpoint_stats
        alert_data["time_window_minutes"] = self.alert_config.time_window_minutes
        alert_data["attack_pattern"] = attack_pattern
        alert_data["ip_failure_count"] = ip_failure_count
        alert_data["current_endpoint_attempts"] = endpoint_attempt_count
        alert_data["endpoint_rate_limit_violations"] = rate_limit_violations
        alert_data["attempt_count"] = ip_failure_count  # Add attempt_count explicitly
        
        # Add error statistics if this is an error alert
        if event.get("log_type") == "error":
            if hasattr(SecurityMonitor, '_module_error_counts'):
                alert_data["module_error_counts"] = dict(SecurityMonitor._module_error_counts)
            if hasattr(SecurityMonitor, '_path_error_counts'):
                alert_data["path_error_counts"] = dict(SecurityMonitor._path_error_counts)
            
            # Count recent errors within the time window
            error_window_minutes = settings.error_window_minutes
            current_time = datetime.utcnow()
            error_cutoff_time = current_time - timedelta(minutes=error_window_minutes)
            
            recent_errors = [
                e for e in self._historical_events
                if e.get('log_type') == 'error' and
                self._get_timestamp_naive(e.get('timestamp')).replace(tzinfo=None) > error_cutoff_time
            ]
            
            alert_data["recent_error_count"] = len(recent_errors)
            alert_data["error_window_minutes"] = error_window_minutes
            
            # Include most common error types
            error_types = {}
            for err in recent_errors:
                error_msg = err.get('message', '')
                error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg[:50]
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            alert_data["error_types"] = error_types
        
        return alert_data

    def _should_send_alert(self, event: Dict[str, Any]) -> bool:
        """Determine if an alert should be sent based on the event and cooldown."""
        try:
            # Check if we're in cooldown period
            if datetime.now() - self.last_alert_time < self.alert_cooldown:
                self.logger.debug("Still in cooldown period, not sending alert")
                return False
            
            # Check event type and thresholds
            event_type = event.get("event_type", "unknown")
            client_ip = event.get("client_ip", "unknown")
            endpoint = event.get("path", "unknown")
            log_type = event.get("log_type", "security")
            
            if log_type not in self.alert_config.enabled_logs:
                self.logger.debug(f"Log type {log_type} not enabled for alerts")
                return False
            
            # Log more debug information to help track the issue
            self.logger.info(f"Checking alert conditions for {event_type} from {client_ip}")
            self.logger.info(f"IP failure count: {SecurityMonitor._ip_failure_counts[client_ip]}, threshold: {self.alert_config.unauthorized_access_threshold}")
            self.logger.info(f"Rate limit violations for {endpoint}: {SecurityMonitor._rate_limit_violations[endpoint]}, threshold: {self.alert_config.rate_limit_threshold}")
            
            # Check specific conditions based on event type
            if event_type == "unauthorized_access" and 'security' in self.alert_config.enabled_logs:
                ip_count = SecurityMonitor._ip_failure_counts[client_ip]
                if ip_count >= self.alert_config.unauthorized_access_threshold:
                    self.logger.info(f"Alert condition met: IP {client_ip} has {ip_count} failures")
                    return True
                
            elif event_type == "rate_limit_violation" and 'rate_limit' in self.alert_config.enabled_logs:
                violations = SecurityMonitor._rate_limit_violations[endpoint]
                if violations >= self.alert_config.rate_limit_threshold:
                    self.logger.info(f"Alert condition met: Endpoint {endpoint} has {violations} rate limit violations")
                    return True
            
            # Check for error threshold if error logs are enabled
            elif log_type == 'error' and 'error' in self.alert_config.enabled_logs:
                error_threshold = settings.error_threshold
                error_window_minutes = settings.error_window_minutes
                
                # Calculate time window for errors
                current_time = datetime.utcnow()
                error_cutoff_time = current_time - timedelta(minutes=error_window_minutes)
                
                # Count recent errors within the time window
                recent_error_count = sum(
                    1 for event in self._historical_events
                    if event.get('log_type') == 'error' and
                    self._get_timestamp_naive(event.get('timestamp', '')) > error_cutoff_time
                )
                
                self.logger.info(f"Recent error count: {recent_error_count}, threshold: {error_threshold}")
                
                if recent_error_count >= error_threshold:
                    self.logger.info(f"Alert condition met: {recent_error_count} errors in the last {error_window_minutes} minutes")
                    return True
                    
                # Check for specific module error patterns
                if hasattr(SecurityMonitor, '_module_error_counts'):
                    for module, count in SecurityMonitor._module_error_counts.items():
                        if count >= error_threshold:
                            self.logger.info(f"Alert condition met: Module {module} has {count} errors")
                            return True
            
            # If we have a missing_auth_header reason, let's trigger an alert regardless of count
            # This handles our specific case for unauthorized access
            if event.get("reason") == "missing_auth_header" and 'security' in self.alert_config.enabled_logs:
                self.logger.info(f"Alert condition met: missing_auth_header from IP {client_ip}")
                return True
                
            self.logger.debug("No alert conditions met")
            return False
        except Exception as e:
            self.logger.error(f"Error checking alert conditions: {str(e)}")
            return False
    
    async def send_alerts(self, event_data: Dict[str, Any]) -> None:
        """Send alerts for security events."""
        try:
            self.logger.info("Preparing to send security alert email")
            
            # Generate alert description
            description = f"Security event detected: {event_data['event_type']} from IP {event_data['client_ip']}"
            if event_data.get('reason'):
                description += f"\nReason: {event_data['reason']}"
            
            # Make sure we have the attempt_count in the event data
            if 'attempt_count' not in event_data:
                client_ip = event_data.get('client_ip', 'unknown')
                event_data['attempt_count'] = SecurityMonitor._ip_failure_counts.get(client_ip, 1)
            
            self.logger.info(f"Email alert description: {description}")
            self.logger.info(f"Email recipients: {self.email_recipients}")
            
            # Check email configuration
            if not self.email_alerts_enabled:
                self.logger.warning("Email alerts are disabled in configuration")
                return
                
            if not self.email_recipients:
                self.logger.warning("No email recipients configured")
                return
            
            # Log detailed configuration for troubleshooting using specialized logger
            log_email_config(
                smtp_server=self.smtp_server,
                smtp_port=self.smtp_port,
                sender=self.email_sender,
                recipients=self.email_recipients,
                use_tls=self.use_tls
            )
            
            # Log email content details
            log_email_details(
                alert_type=event_data['event_type'],
                suspicious_ips=[event_data['client_ip']],
                attempt_count=event_data['attempt_count'],
                additional_info=event_data
            )
            
            # Send email with retry logic
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"Attempting to send email (attempt {attempt + 1}/{max_retries})")
                    
                    # Log attempt with the specialized logger
                    for recipient in self.email_recipients:
                        log_email_attempt(
                            recipient=recipient,
                            alert_type=event_data['event_type'],
                            event_data=event_data
                        )
                    
                    success = await send_email_alert(
                        smtp_server=self.smtp_server,
                        smtp_port=self.smtp_port,
                        sender_email=self.email_sender,
                        receiver_emails=self.email_recipients,
                        password=self.email_password,
                        alert_type=event_data['event_type'],
                        description=description,
                        suspicious_ips=[event_data['client_ip']],
                        attempt_count=event_data['attempt_count'],
                        additional_info=event_data,
                        use_tls=self.use_tls
                    )
                    
                    if success:
                        self.logger.info("EMAIL SENT SUCCESSFULLY: Security alert email sent to all recipients")
                        
                        # Log success with the specialized logger
                        for recipient in self.email_recipients:
                            log_email_success(
                                recipient=recipient,
                                alert_type=event_data['event_type']
                            )
                        
                        self.last_alert_time = datetime.now()
                        self.logger.info(f"Setting last_alert_time to {self.last_alert_time}")
                        return
                    else:
                        self.logger.warning(f"EMAIL SEND FAILURE: Failed to send email on attempt {attempt + 1}")
                        
                        # Log failure with the specialized logger
                        for recipient in self.email_recipients:
                            log_email_failure(
                                recipient=recipient,
                                alert_type=event_data['event_type'],
                                error="Unknown error",
                                attempt=attempt + 1,
                                max_attempts=max_retries
                            )
                except Exception as e:
                    self.logger.error(f"EMAIL ERROR: Error sending email on attempt {attempt + 1}: {str(e)}")
                    self.logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                    
                    # Log failure with the specialized logger
                    for recipient in self.email_recipients:
                        log_email_failure(
                            recipient=recipient,
                            alert_type=event_data['event_type'],
                            error=str(e),
                            attempt=attempt + 1,
                            max_attempts=max_retries
                        )
                    
                    if attempt < max_retries - 1:
                        self.logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                
        except Exception as e:
            self.logger.error(f"Error in send_alerts: {str(e)}")
            self.logger.error(f"Event data: {json.dumps(event_data, default=str)}")

    async def start(self) -> None:
        """Start the security monitor."""
        try:
            self.logger.info("Starting security monitor...")
            self.is_running = True
            self.logger.info("Security monitor started successfully")
        except Exception as e:
            self.logger.error(f"Error starting security monitor: {str(e)}")
            self.is_running = False
            raise

    async def stop(self) -> None:
        """Stop the security monitor gracefully."""
        try:
            self.logger.info("Stopping security monitor...")
            self.is_running = False
            self.logger.info("Security monitor stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping security monitor: {str(e)}")
            raise

# Create a global instance with default configuration
monitor = SecurityMonitor()

async def main_async():
    """Async main entry point for the script."""
    try:
        # Keep the monitor running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Security monitoring system")
    parser.add_argument("--security-log", help="Path to security log file")
    parser.add_argument("--rate-limit-log", help="Path to rate limit log file")
    parser.add_argument("--error-log", help="Path to error log file")
    parser.add_argument("--enabled-logs", help="Comma-separated list of logs to enable (e.g., security,rate_limit,error)", default="security,rate_limit")
    parser.add_argument("--unauthorized-threshold", type=int, help="Threshold for unauthorized access alerts", default=3)
    parser.add_argument("--rate-limit-threshold", type=int, help="Threshold for rate limit violation alerts", default=5)
    parser.add_argument("--cooldown", type=int, help="Alert cooldown period in minutes", default=5)
    parser.add_argument("--time-window", type=int, help="Time window for tracking events in minutes", default=60)
    
    args = parser.parse_args()
    
    # Create alert configuration from command line arguments
    alert_config = AlertConfig(
        enabled_logs=set(args.enabled_logs.split(',')),
        unauthorized_access_threshold=args.unauthorized_threshold,
        rate_limit_threshold=args.rate_limit_threshold,
        cooldown_minutes=args.cooldown,
        time_window_minutes=args.time_window
    )
    
    # Create monitor with command line arguments
    monitor = SecurityMonitor(
        alert_config=alert_config,
        security_log_path=args.security_log,
        rate_limit_log_path=args.rate_limit_log,
        error_log_path=args.error_log
    )
    
    # Run the monitor
    asyncio.run(main_async())