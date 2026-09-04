from flask import Blueprint
from controllers.doctor_controller import DoctorController
from middleware.auth_middleware import doctor_required

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


@doctor_bp.route("/dashboard", methods=["GET"])
@doctor_required
def dashboard():
    return DoctorController.render_dashboard()


@doctor_bp.route("/soap-generate", methods=["POST"])
@doctor_required
def soap_generate():
    return DoctorController.generate_soap()
