from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """
    Expose Prometheus metrics with the correct content type.
    
    This endpoint manually sets the content type to 'text/plain; version=0.0.4',
    which is what Prometheus expects when scraping metrics.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    ) 