from src.base.interfaces.internal.health import router as health_check_router
from src.base.interfaces.internal.rate_limited_endpoints import router as rate_limited_router
from src.base.interfaces.internal.metrics import router as metrics_router
from prometheus_fastapi_instrumentator import Instrumentator

def setup_internal_routes(app, instrumentator: Instrumentator):
    # Include the metrics endpoint with the correct content type
    app.include_router(metrics_router, prefix="/internal", tags=["Internal"])
    
    # Include the health and readiness endpoints with a prefix
    app.include_router(health_check_router, prefix="/internal", tags=["Internal"])
    # Include rate-limited example endpoints
    app.include_router(rate_limited_router, prefix="/internal/rate-limit-examples", tags=["Rate Limiting"])
