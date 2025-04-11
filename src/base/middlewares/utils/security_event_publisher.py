from fastapi import Request
import logging

logger = logging.getLogger(__name__)

class SecurityEventPublisher:
    def __init__(self, producer):
        self.producer = producer

    async def publish_event(self, request: Request, reason: str, additional_info: dict):
        """
        Publish a security event when a 401 Unauthorized response is sent.
        """
        event = {
            "event_type": "security",
            "reason": reason,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host,
            "headers": {k: v for k, v in request.headers.items()},
            "additional_info": additional_info,
        }
        try:
            await self.producer.publish_event(event)
            logger.info(f"Published security event: {event}")
        except Exception as e:
            logger.error(f"Failed to publish security event: {e}")