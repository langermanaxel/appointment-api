from flask import jsonify, render_template, current_app

from app.exceptions import (
    AppointmentAlreadyExists,
    AppointmentNotFound,
    AppointmentAlreadyCancelled,
)


def _error_message(error: Exception, public_message: str) -> str | None:
    """
    Devuelve un mensaje seguro para el cliente.
    En desarrollo muestra el error real, en producción devuelve None.
    """
    return str(error) if current_app.debug else None


def handle_page_not_found(error):
    return render_template("404.html"), 404


def _json_error(public_message: str, status_code: int, error_detail: str | None = None):
    """
    Handler genérico de errores JSON.
    Estandariza el formato: code, message, details.
    """
    payload = {
        "code": status_code,
        "message": public_message,
        "details": error_detail,
    }
    return jsonify(payload), status_code


def handle_appointment_already_exists(error):
    return _json_error(
        public_message="An appointment already exists for the selected time",
        status_code=409,
        error_detail=_error_message(error, "An appointment already exists for the selected time")
    )


def handle_appointment_already_cancelled(error):
    return _json_error(
        public_message="The appointment has already been cancelled",
        status_code=400,
        error_detail=_error_message(error, "The appointment has already been cancelled")
    )


def handle_appointment_not_found(error):
    return _json_error(
        public_message="Appointment not found",
        status_code=404,
        error_detail=_error_message(error, "Appointment not found")
    )


def handle_internal_error(error):
    # Log completo siempre
    current_app.logger.exception(error)

    return _json_error(
        public_message="Internal Server Error",
        status_code=500,
        error_detail=_error_message(error, "Internal Server Error")
    )


def register_error_handlers(app):
    """
    Registro de handlers para la API versionada: /api/v1/errors
    """
    app.register_error_handler(AppointmentAlreadyExists, handle_appointment_already_exists)
    app.register_error_handler(AppointmentAlreadyCancelled, handle_appointment_already_cancelled)
    app.register_error_handler(AppointmentNotFound, handle_appointment_not_found)

    # Fallback global (siempre al final)
    app.register_error_handler(Exception, handle_internal_error)


def register_web_error_handlers(app):
    """
    Handlers para errores de páginas web (HTML).
    """
    app.register_error_handler(404, handle_page_not_found)
