from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Index,
    UniqueConstraint,
    CheckConstraint,
)
from app.database import Base


class AppointmentStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    status = Column(
        String,
        nullable=False,
        default=AppointmentStatus.ACTIVE.value,
    )

    __table_args__ = (
        # Índice parcial SOLO para turnos activos (optimizado para SQLite)
        Index(
            "ix_appointments_active_user_time",
            "user_name",
            "appointment_time",
            sqlite_where=(status == AppointmentStatus.ACTIVE.value),
        ),
        Index(
            "ix_appointments_status_time",
            "status",
            "appointment_time",
        ),
        UniqueConstraint(
            "user_name",
            "appointment_time",
            "status",
            name="uq_active_appointment_per_user",
        ),
        CheckConstraint(
            "status IN ('active', 'cancelled')",
            name="ck_appointments_status_valid",
        ),
    )
