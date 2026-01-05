import os
import logging
from flask import Flask

from app.config import DevelopmentConfig, ProductionConfig
from app.database import Base, engine
from app.routes import routes
from app.error_handlers import (
    register_error_handlers,
    register_web_error_handlers,
)


def create_app() -> Flask:
    """Flask application factory."""
    app = Flask(__name__)

    logging.basicConfig(level=logging.INFO)

    env = os.getenv("APP_ENV", "development")
    logging.info(f"Starting application in {env} mode")

    # Cargar configuración desde Pydantic
    config = (
        ProductionConfig()
        if env == "production"
        else DevelopmentConfig()
    )

    app.config.from_mapping(config.model_dump())

    # Fail fast (nunca arrancar sin SECRET_KEY)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY no configurada")

    app.secret_key = app.config["SECRET_KEY"]

    # Error handlers
    register_error_handlers(app)
    register_web_error_handlers(app)

    # Blueprints
    app.register_blueprint(routes)

    # Security headers
    @app.after_request
    def add_security_headers(response):
        for k, v in app.config.get("SECURITY_HEADERS", {}).items():
            response.headers.setdefault(k, v)
        return response

    # Inicializar DB solo en desarrollo
    if env == "development":
        with app.app_context():
            Base.metadata.create_all(bind=engine)

    return app


# Entry point
app = create_app()

if __name__ == "__main__":
    app.run()
