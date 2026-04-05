from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAuth"
    database_url: str = "sqlite+aiosqlite:///./fastauth.db"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "changeme"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
