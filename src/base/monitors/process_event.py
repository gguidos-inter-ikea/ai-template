from typing import Dict, Any
from collections import defaultdict
from src.base.scripts.security_monitor import SecurityMonitor
from src.base.config.alert_config import alert_config
from src.base.monitors.utils import (
    _cleanup_old_events,
    _should_send_alert,
)
import datetime
import logging

logger= logging.name(__name__)

async def process_event(event: Dict[str, Any]) -> None:
        """Process a security event and update counters."""

        historical_events = []
        
        try:
            event_type = event.get("event_type", "unknown")
            client_ip = event.get("client_ip", "unknown")
            endpoint = event.get("path", "unknown")
            log_type = event.get("log_type", "security")  # Default to security log
            
            logger.info(f"Processing {log_type} event: {event_type} from IP {client_ip}")
            
            if log_type not in alert_config.enabled_logs:
                logger.debug(f"Skipping event from disabled log type: {log_type}")
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
                            logger.warning(f"Could not parse timestamp: {event['timestamp']}")
                            event_time = datetime.utcnow()
                            event['timestamp'] = event_time.isoformat()
            else:
                # Add timestamp if not present
                event_time = datetime.utcnow()
                event['timestamp'] = event_time.isoformat()
            
            # Store event for historical analysis
            historical_events.append(event)
            _cleanup_old_events()
            
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
                logger.info(f"Error pattern detected in module {error_module}: {error_message[:100]}...")
                
                # Check if we should send error alerts
                should_alert = _should_send_alert(event)
                
                if should_alert:
                    logger.info(f"Alert condition met for error in module {error_module}. Sending error alert...")
                    
                    # Prepare error alert data
                    error_data = self._prepare_error_alert_data(event)
                    
                    # Send error alert with the dedicated function
                    await self._send_error_alert(error_data)
                else:
                    self.logger.info(f"No alert triggered for error in module {error_module}")
                
                return
            
            # Process regular security events (not errors)
            # Update class-level counters based on event type
            if event_type == "unauthorized_access" and 'security' in alert_config.enabled_logs:
                SecurityMonitor._ip_failure_counts[client_ip] += 1
                SecurityMonitor._error_count += 1
                SecurityMonitor._endpoint_attempts[endpoint] += 1
                
                # Log the updated counts
                logger.info(f"Updated counters for {client_ip}: {SecurityMonitor._ip_failure_counts[client_ip]} failures")
                
            elif event_type == "rate_limit_violation" and 'rate_limit' in self.alert_config.enabled_logs:
                SecurityMonitor._rate_limit_violations[endpoint] += 1
                
                # Log the updated rate limit violations
                logger.info(f"Updated rate limit violations for {endpoint}: {SecurityMonitor._rate_limit_violations[endpoint]}")
            
            # Check if we should send alerts
            should_alert = _should_send_alert(event)
            
            if should_alert:
                logger.info(f"Alert condition met for {event_type} from {client_ip}. Sending email alert...")
                
                # Prepare alert data with additional context
                alert_data = self._prepare_alert_data(event)
                
                # Send the alert
                await self.send_alerts(alert_data)
            else:
                self.logger.info(f"No alert triggered for {event_type} from {client_ip}")
                
        except Exception as e:
            self.logger.error(f"Error processing security event: {str(e)}")
            self.logger.error("Event data: %s", json.dumps(event, indent=2, default=str))