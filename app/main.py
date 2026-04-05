from fastapi import FastAPI

from app.modules.auth.router import router as auth_router
from app.modules.welcome.router import router as welcome_router

app = FastAPI(title="FastAuth")

app.include_router(welcome_router)
app.include_router(auth_router)
