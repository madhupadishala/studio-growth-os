"""
Studio Growth OS - Core Configuration
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Studio Growth OS"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://studio:studio_dev_password@localhost:5432/studio_growth_os"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str = "dev-secret-change-in-production"
    JWT_SECRET: str = "dev-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Meta/WhatsApp
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_WEBHOOK_URL: str = ""

    # YouTube
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_API_KEY: str = ""
    YOUTUBE_REDIRECT_URI: str = ""

    # Google Business Profile
    GBP_CLIENT_ID: str = ""
    GBP_CLIENT_SECRET: str = ""
    GBP_REDIRECT_URI: str = ""

    # Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # AI
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 500

    # Media Storage (Cloudflare R2 / S3)
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = ""
    R2_PUBLIC_URL: str = ""

    # Email (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@studiox.in"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()