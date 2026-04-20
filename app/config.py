from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "DevLog API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"

    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_KEY: str = "your-service-role-key"

    GUNICORN_WORKERS: int = 4
    GUNICORN_MAX_REQUESTS: int = 1000
    GUNICORN_MAX_REQUESTS_JITTER: int = 50

    RATE_LIMIT_GENERAL: int = 100
    RATE_LIMIT_ANALYTICS: int = 20
    RATE_LIMIT_WINDOW: int = 60


settings = Settings()