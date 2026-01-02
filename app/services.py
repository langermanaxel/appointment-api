from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Appointment
from app.exceptions import (
    AppointmentAlreadyExists,
    AppointmentNotFound,
    AppointmentAlreadyCancelled,
)


def create_appointment(db: Session, data):
    """
    Crea un turno verificando reglas de negocio:
    - No duplicar turnos activos para el mismo usuario
    - Mismo horario
    """

    # Validación rápida para UX (no reemplaza la constraint)
    existing_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.user_name == data.user_name,
            Appointment.appointment_time == data.appointment_time,
            Appointment.status == "active",
        )
        .first()
    )

    if existing_appointment is not None:
        raise AppointmentAlreadyExists(
            "El usuario ya tiene un turno en ese horario"
        )

    appointment = Appointment(
        user_name=data.user_name,
        appointment_time=data.appointment_time,
    )

    db.add(appointment)

    try:
        db.commit()
    except IntegrityError:
        # 🔒 Colisión concurrente detectada por la DB
        db.rollback()
        raise AppointmentAlreadyExists(
            "El usuario ya tiene un turno en ese horario"
        )

    db.refresh(appointment)
    return appointment


def list_appointments(
    db: Session,
    status: str | None = None,
    page: int = 1,
    page_size: int = 10,
):
    """
    Devuelve una lista paginada de turnos.
    """

    query = db.query(Appointment)

    if status is not None:
        query = query.filter(Appointment.status == status)

    total = query.count()

    appointments = (
        query
        .order_by(Appointment.appointment_time)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return appointments, total



def cancel_appointment(db: Session, appointment_id: int):
    """
    Cancela un turno existente.
    No elimina el registro, solo cambia su estado.
    """

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment is None:
        raise AppointmentNotFound("Turno no encontrado")

    if appointment.status == "cancelled":
        raise AppointmentAlreadyCancelled("El turno ya está cancelado")

    appointment.status = "cancelled"
    db.commit()

    return appointment
