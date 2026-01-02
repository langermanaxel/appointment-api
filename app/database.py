import os
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base para modelos ORM
Base = declarative_base()

def validate_database_url(url: str) -> bool:
    """
    Valida que la URL de la base de datos tenga un esquema válido.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.path:
        logger.error(f"URL de base de datos inválida: {url}")
        return False
    return True

def get_engine(
    database_url: str,
    async_mode: bool = False,
    pool_config: Optional[Dict[str, Any]] = None
) -> "Engine | AsyncEngine":
    """
    Factory para crear un engine SQLAlchemy, soportando
    sync y async, diferentes motores de DB y parámetros de pool dinámicos.
    """
    if not validate_database_url(database_url):
        raise ValueError("DATABASE_URL inválida")

    engine_kwargs: Dict[str, Any] = {"future": True}

    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # Pool dinámico con valores por defecto si no se pasan
        pool_config = pool_config or {}
        engine_kwargs.update({
            "pool_size": pool_config.get("pool_size", 5),
            "max_overflow": pool_config.get("max_overflow", 10),
            "pool_timeout": pool_config.get("pool_timeout", 30),
            "pool_recycle": pool_config.get("pool_recycle", 1800),
        })

    try:
        if async_mode:
            engine = create_async_engine(database_url, **engine_kwargs)
        else:
            engine = create_engine(database_url, **engine_kwargs)
        logger.info(f"Engine creado exitosamente para {database_url}")
        return engine
    except SQLAlchemyError as e:
        logger.exception(f"Error al crear engine: {e}")
        raise

def get_session(engine: "Engine | AsyncEngine") -> Session:
    """
    Devuelve una sesión de SQLAlchemy para operaciones de base de datos.
    """
    try:
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
        return SessionLocal()
    except SQLAlchemyError as e:
        logger.exception(f"Error al crear sesión: {e}")
        raise

# URL de la base de datos (sin exponer credenciales en el código)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///appointments.db")

# Configuración de pool dinámica según entorno
POOL_CONFIG = {
    "pool_size": int(os.getenv("DB_POOL_SIZE", 5)),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 10)),
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", 30)),
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", 1800)),
}

# Crear engine y sesión
engine = get_engine(DATABASE_URL, async_mode=False, pool_config=POOL_CONFIG)
session = get_session(engine)
