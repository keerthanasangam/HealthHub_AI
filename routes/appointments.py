from flask import Blueprint
from controllers.appointment_controller import AppointmentController

appointments_bp = Blueprint("appointments", __name__, url_prefix="/patient")


@appointments_bp.route("/appointments", methods=["GET"])
def appointments_page():
    return AppointmentController.render_patient_appointments()


@appointments_bp.route("/appointments/book", methods=["POST"])
def book():
    return AppointmentController.book_appointment()
