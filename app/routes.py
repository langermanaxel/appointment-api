from datetime import datetime

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

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


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

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


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
    min_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M")

    if request.method == "POST":
        try:
            data = AppointmentCreate(
                user_name=request.form["user_name"],
                appointment_time=datetime.fromisoformat(
                    request.form["appointment_time"]
                ),
            )

            with get_db() as db:
                create_appointment(db, data)

            flash("Turno creado correctamente", "success")
            return redirect(url_for("routes.show_appointments"))

        except ValidationError as e:
            flash(e.errors()[0]["msg"], "danger")

        except ValueError as e:
            flash(str(e), "danger")

        except Exception:
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

    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for("routes.show_appointments"))
