from datetime import datetime, time, timezone
from pydantic import BaseModel, field_validator


# Reglas de negocio centralizadas
BUSINESS_HOURS_START = time(9, 0)
BUSINESS_HOURS_END = time(18, 0)

# Reglas de validación de usuario
MAX_USERNAME_LENGTH = 100


class AppointmentCreate(BaseModel):
    """
    Modelo de entrada para la creación de turnos.
    - Manejo de fechas en UTC
    - Reglas de negocio centralizadas
    - Validaciones defensivas para robustez y seguridad
    """
    user_name: str
    appointment_time: datetime

    @field_validator("user_name")
    def validate_user_name(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Datos inválidos")

        if len(normalized) > MAX_USERNAME_LENGTH:
            raise ValueError("Datos inválidos")

        if not normalized.replace(" ", "").isalpha():
            raise ValueError("Datos inválidos")

        return normalized

    @field_validator("appointment_time")
    def validate_appointment_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("Datos inválidos")

        now_utc = datetime.now(timezone.utc)
        if value < now_utc:
            raise ValueError("Datos inválidos")

        appointment_clock_time = value.timetz().replace(tzinfo=None)

        if not (
            BUSINESS_HOURS_START
            <= appointment_clock_time
            <= BUSINESS_HOURS_END
        ):
            raise ValueError("Datos inválidos")

        return value

