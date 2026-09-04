from flask import Blueprint
from controllers.patient_controller import PatientController
from middleware.auth_middleware import login_required

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")


@patient_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return PatientController.render_dashboard()
