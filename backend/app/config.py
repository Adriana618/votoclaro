"""Application settings via pydantic-settings."""

import warnings

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    DATABASE_URL: str = "postgresql://votoclaro:votoclaro@localhost:5432/votoclaro"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production"
    CORS_ORIGINS: str = "http://localhost:3000"
    BASE_URL: str = "https://api.votaclaro.com"
    FRONTEND_URL: str = "https://www.votaclaro.com"

    # Web Push (VAPID) settings
    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""
    VAPID_CLAIMS_EMAIL: str = "mailto:admin@votaclaro.com"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        if "*" in origins:
            warnings.warn(
                "CORS_ORIGINS contains '*'. This is insecure for production.",
                stacklevel=2,
            )
        return origins

    def warn_insecure_defaults(self) -> None:
        """Emit warnings if security-critical settings use defaults."""
        if self.SECRET_KEY == "change-me-in-production":
            warnings.warn(
                "SECRET_KEY is using the default value. "
                "Set a strong random SECRET_KEY via environment variable "
                "before deploying to production.",
                stacklevel=2,
            )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
settings.warn_insecure_defaults()
