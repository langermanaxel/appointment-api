class AppointmentError(Exception):
    """Excepción base para el dominio de gestión de turnos."""
    pass


class AppointmentAlreadyExists(AppointmentError):
    """Se intenta crear un turno que ya existe para ese usuario y horario."""
    pass


class AppointmentNotFound(AppointmentError):
    """No se encontró el turno solicitado."""
    pass


class AppointmentAlreadyCancelled(AppointmentError):
    """Se intenta cancelar un turno que ya fue cancelado."""
    pass
