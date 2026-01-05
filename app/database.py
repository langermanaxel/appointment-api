import os
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

# Logger (configurado a nivel aplicación, no aquí)
logger = logging.getLogger(__name__)

# Base ORM
Base = declarative_base()


# -----------------------------
# Utils
# -----------------------------

def validate_database_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.path)


# -----------------------------
# Engine factory
# -----------------------------

def get_engine(
    database_url: str,
    async_mode: bool = False,
    pool_config: Optional[Dict[str, Any]] = None,
) -> Engine | AsyncEngine:

    if not validate_database_url(database_url):
        raise ValueError("DATABASE_URL inválida")

    engine_kwargs: Dict[str, Any] = {"future": True}

    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        pool_config = pool_config or {}
        engine_kwargs.update({
            "pool_size": pool_config.get("pool_size", 5),
            "max_overflow": pool_config.get("max_overflow", 10),
            "pool_timeout": pool_config.get("pool_timeout", 30),
            "pool_recycle": pool_config.get("pool_recycle", 1800),
        })

    try:
        engine = (
            create_async_engine(database_url, **engine_kwargs)
            if async_mode
            else create_engine(database_url, **engine_kwargs)
        )
        logger.info(f"Engine creado exitosamente para {database_url}")
        return engine
    except SQLAlchemyError:
        logger.exception("Error al crear engine")
        raise


# -----------------------------
# Configuración global
# -----------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///appointments.db")

POOL_CONFIG = {
    "pool_size": int(os.getenv("DB_POOL_SIZE", 5)),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 10)),
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", 30)),
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", 1800)),
}

engine = get_engine(
    DATABASE_URL,
    async_mode=False,
    pool_config=POOL_CONFIG,
)

# Session factory (una sesión por request)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# -----------------------------
# Session context manager
# -----------------------------

@contextmanager
def get_db() -> Session:
    """
    Provee una sesión de base de datos por request.
    Garantiza cierre correcto incluso ante excepciones.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
