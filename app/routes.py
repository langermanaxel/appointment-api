from datetime import datetime, timezone, timedelta

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash,
)
from pydantic import ValidationError

from app.database import get_db
from app.schemas import AppointmentCreate
from app.services import (
    list_appointments,
    create_appointment,
    cancel_appointment,
)

routes = Blueprint("routes", __name__)

# -----------------------------
# API REST
# -----------------------------

@routes.route("/appointments", methods=["POST"])
def create():
    try:
        payload = request.get_json()
        data = AppointmentCreate(**payload)

        with get_db() as db:
            appointment = create_appointment(db, data)

        return jsonify({"id": appointment.id}), 201

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    except ValueError:
        return jsonify({"error": "Datos inválidos"}), 400


@routes.route("/appointments", methods=["GET"])
def list_all():
    status = request.args.get("status")
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)

    with get_db() as db:
        appointments, total = list_appointments(
            db,
            status=status,
            page=page,
            page_size=page_size,
        )

    return jsonify({
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [
            {
                "id": appointment.id,
                "user_name": appointment.user_name,
                "appointment_time": appointment.appointment_time.isoformat(),
                "status": appointment.status,
            }
            for appointment in appointments
        ],
    })


@routes.route("/appointments/<int:appointment_id>/cancel", methods=["PATCH"])
def cancel(appointment_id: int):
    try:
        with get_db() as db:
            appointment = cancel_appointment(db, appointment_id)

        return jsonify({
            "message": "Turno cancelado correctamente",
            "id": appointment.id,
        })

    except ValueError:
        return jsonify({"error": "Datos inválidos"}), 400


# -----------------------------
# Vistas HTML
# -----------------------------

@routes.route("/")
def show_appointments():
    with get_db() as db:
        appointments, _ = list_appointments(db)

    return render_template(
        "appointments.html",
        appointments=appointments,
    )


@routes.route("/appointments/new", methods=["GET", "POST"])
def new_appointment():
    # Hora mínima local (Argentina)
    min_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M")

    if request.method == "POST":
        try:
            raw_dt = request.form["appointment_time"]

            # ✅ Parse explícito de datetime-local
            appointment_time_local = datetime.strptime(
                raw_dt, "%Y-%m-%dT%H:%M"
            )

            # Timezone Argentina (UTC-3)
            argentina_tz = timezone(timedelta(hours=-3))
            appointment_time_local = appointment_time_local.replace(
                tzinfo=argentina_tz
            )

            # Convertir a UTC
            appointment_time_utc = appointment_time_local.astimezone(
                timezone.utc
            )

            data = AppointmentCreate(
                user_name=request.form["user_name"],
                appointment_time=appointment_time_utc,
            )

            with get_db() as db:
                create_appointment(db, data)

            flash("Turno creado correctamente", "success")
            return redirect(url_for("routes.show_appointments"))

        except ValidationError as e:
            # Debug real (temporal)
            print("VALIDATION ERROR:", e.errors())
            flash("Datos inválidos", "danger")

        except ValueError as e:
            print("VALUE ERROR:", repr(e))
            flash("Datos inválidos", "danger")

        except Exception as e:
            print("ERROR REAL:", repr(e))
            flash("Ocurrió un error inesperado", "danger")

    return render_template(
        "create_appointment.html",
        min_datetime=min_datetime,
    )



@routes.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
def cancel_appointment_view(appointment_id: int):
    try:
        with get_db() as db:
            cancel_appointment(db, appointment_id)

        flash("Turno cancelado correctamente", "info")

    except ValueError:
        flash("Datos inválidos", "danger")

    return redirect(url_for("routes.show_appointments"))
