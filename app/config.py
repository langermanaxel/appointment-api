from typing import Dict
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")

    DATABASE_URL: str = Field(
        default="sqlite:///appointments.db",
        env="DATABASE_URL",
    )

    APP_ENV: str = Field(
        default="development",
        env="APP_ENV",
    )

    DEBUG: bool = True

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    SECURITY_HEADERS: Dict[str, str] = {
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("SECRET_KEY must be set")
        return v


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True


class ProductionConfig(BaseConfig):
    DEBUG: bool = False
