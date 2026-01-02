from pydantic import BaseSettings, Field, validator, AnyHttpUrl
from typing import Dict


class BaseConfig(BaseSettings):
    """
    Configuración base compartida entre entornos.
    Carga variables desde .env automáticamente.
    """

    # Clave secreta de la aplicación. NO usar valor por defecto en producción.
    SECRET_KEY: str = Field(..., env="SECRET_KEY")

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Cabeceras de seguridad
    SECURITY_HEADERS: Dict[str, str] = {
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("SECRET_KEY")
    def secret_key_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("SECRET_KEY must be set and non-empty")
        return v


class DevelopmentConfig(BaseConfig):
    """
    Configuración para desarrollo.
    Usa SQLite por defecto si DATABASE_URL no está definida.
    """

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = Field(
        default="sqlite:///dev.db", env="DATABASE_URL"
    )


class ProductionConfig(BaseConfig):
    """
    Configuración para producción.
    Lanza error si DATABASE_URL no está definida para evitar fallos silenciosos.
    """

    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = Field(..., env="DATABASE_URL")

    @validator("SQLALCHEMY_DATABASE_URI")
    def validate_db_uri(cls, v):
        if not v or v.strip() == "":
            raise ValueError("DATABASE_URL must be set in Production environment")
        return v
