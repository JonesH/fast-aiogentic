"""Configuration settings for fast-aiogentic bot."""

import functools

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Bot configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram Bot
    telegram_bot_token: str

    # OpenRouter (for fast-agent LLM)
    openrouter_api_key: str

    # Model settings
    default_model: str = "openrouter.x-ai/grok-3-mini"

    # Webhook configuration
    webhook_enabled: bool = False
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8000
    webhook_url: str = "https://jonaheidsick.de/fast-aiogentic/webhook"
    webhook_path: str = "/webhook"
    webhook_secret: str = ""

    # Health endpoint (for Docker/Traefik)
    health_path: str = "/health"


@functools.cache
def get_settings() -> Settings:
    """Lazy-load settings to avoid import-time env var validation."""
    return Settings()
