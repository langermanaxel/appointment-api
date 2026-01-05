import re
from datetime import datetime, time, timezone, timedelta
from pydantic import BaseModel, field_validator


BUSINESS_HOURS_START = time(9, 0)
BUSINESS_HOURS_END = time(18, 0)

MAX_USERNAME_LENGTH = 100
MIN_ADVANCE_MINUTES = 5

ARGENTINA_TZ = timezone(timedelta(hours=-3))


class AppointmentCreate(BaseModel):
    user_name: str
    appointment_time: datetime

    @field_validator("user_name")
    def validate_user_name(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Datos inválidos")

        if len(normalized) > MAX_USERNAME_LENGTH:
            raise ValueError("Datos inválidos")

        # ✔️ Letras (incluye acentos) + números + espacios
        if not re.fullmatch(r"[A-Za-zÀ-ÿ0-9\s]+", normalized):
            raise ValueError("Datos inválidos")

        return normalized

    @field_validator("appointment_time")
    def validate_appointment_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("Datos inválidos")

        now_utc = datetime.now(timezone.utc)
        min_allowed = now_utc + timedelta(minutes=MIN_ADVANCE_MINUTES)

        if value < min_allowed:
            raise ValueError("Datos inválidos")

        local_dt = value.astimezone(ARGENTINA_TZ)
        local_time = local_dt.time()

        if not (BUSINESS_HOURS_START <= local_time <= BUSINESS_HOURS_END):
            raise ValueError("Datos inválidos")

        return value
