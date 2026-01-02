import os
from flask import Flask

from app.config import DevelopmentConfig, ProductionConfig
from app.database import Base, engine
from app.routes import routes
from app.error_handlers import (
    register_error_handlers,
    register_web_error_handlers,
)


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)

    # Selección de configuración según entorno
    env = os.getenv("FLASK_ENV", "development")

    app.config.from_object(
        ProductionConfig if env == "production" else DevelopmentConfig
    )

    # Fail fast: nunca arrancar sin SECRET_KEY
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY no configurada")

    # Registro de handlers de errores
    register_error_handlers(app)
    register_web_error_handlers(app)

    # Registro de blueprints
    app.register_blueprint(routes)

    # Headers de seguridad
    @app.after_request
    def add_security_headers(response):
        headers = app.config.get("SECURITY_HEADERS", {})
        for key, value in headers.items():
            response.headers.setdefault(key, value)
        return response

    # Lazy DB init (solo desarrollo)
    if env == "development":
        with app.app_context():
            Base.metadata.create_all(bind=engine)

    return app


# Entrypoint para Gunicorn / uWSGI
app = create_app()

if __name__ == "__main__":
    # Solo desarrollo
    app.run()
