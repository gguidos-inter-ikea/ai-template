import datetime
import logging
from pydantic import Dict, Any
from src.base.config.alert_config import AlertConfig

logger = logging.name(__name__)

def _get_timestamp_naive(timestamp_str: str) -> datetime:
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
        logger.error(f"Could not parse timestamp with any formatter: {timestamp_str}")
        raise ValueError(f"Could not parse timestamp: {timestamp_str}")

def _should_send_alert(event: Dict[str, Any], last_alert_time, alert_cooldown) -> bool:
        """Determine if an alert should be sent based on the event and cooldown."""
        try:
            # Check if we're in cooldown period
            if datetime.utcnow() - last_alert_time < alert_cooldown:
                logger.debug("Still in cooldown period, not sending alert")
                return False
            
            # Check event type and thresholds
            event_type = event.get("event_type", "unknown")
            client_ip = event.get("client_ip", "unknown")
            endpoint = event.get("path", "unknown")
            log_type = event.get("log_type", "security")
            
            if log_type not in AlertConfig.enabled_logs:
                logger.debug(f"Log type {log_type} not enabled for alerts")
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