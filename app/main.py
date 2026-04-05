import time

from fastapi import FastAPI, Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.core.logging import get_logger, setup_logging
from app.modules.auth.router import router as auth_router
from app.modules.welcome.router import router as welcome_router

setup_logging()
logger = get_logger("app")

app = FastAPI(title="FastAuth")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "http_request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration,
            "ip": request.client.host,
        },
    )
    return response


app.include_router(welcome_router)
app.include_router(auth_router)
