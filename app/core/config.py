from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAuth"
    database_url: str = "sqlite+aiosqlite:///./fastauth.db"
    secret_key: str = "changeme"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
