from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.modules.auth.router import router as auth_router
from app.modules.welcome.router import router as welcome_router

app = FastAPI(title="FastAuth")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(welcome_router)
app.include_router(auth_router)
