from flask import render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
from bson.objectid import ObjectId
from database.mongodb import appointments, users, triage_sessions


class AppointmentController:

    @staticmethod
    def render_patient_appointments():
        user = session.get("user")
        user_id = user["id"] if user else None

        # Fetch doctors
        doctor_list = list(users.find({"role": "doctor"}, {"password": 0}))
        if not doctor_list:
            # Fallback mock doctors for seamless demo
            doctor_list = [
                {"_id": "doc1", "name": "Dr. Sarah Jenkins", "specialization": "Cardiologist", "experience": "12 Years"},
                {"_id": "doc2", "name": "Dr. Rajesh Sharma", "specialization": "General Physician", "experience": "15 Years"},
                {"_id": "doc3", "name": "Dr. Emily Chen", "specialization": "Dermatologist", "experience": "9 Years"}
            ]

        user_appointments = []
        if user_id:
            user_appointments = list(appointments.find({"patient_id": user_id}).sort("date", 1))

        return render_template(
            "patient/appointments.html",
            user=user,
            doctors=doctor_list,
            appointments=user_appointments
        )

    @staticmethod
    def book_appointment():
        user = session.get("user")
        if not user or not user.get("id"):
            flash("Please sign in to schedule an appointment.", "error")
            return redirect(url_for("auth.login"))

        doctor_id = request.form.get("doctor_id")
        doctor_name = request.form.get("doctor_name", "Specialist")
        date_str = request.form.get("date")
        time_str = request.form.get("time")
        symptoms = request.form.get("symptoms", "").strip()

        if not date_str or not time_str:
            flash("Date and time slot are required.", "error")
            return redirect(url_for("appointments.appointments_page"))

        # Look for recent triage session to attach
        recent_triage = triage_sessions.find_one({"user_id": user["id"]}, sort=[("created_at", -1)])
        triage_urgency = recent_triage.get("urgency") if recent_triage else "green"

        appointments.insert_one({
            "patient_id": user["id"],
            "patient_name": user.get("name"),
            "patient_email": user.get("email"),
            "doctor_id": doctor_id,
            "doctor_name": doctor_name,
            "date": date_str,
            "time": time_str,
            "symptoms": symptoms,
            "triage_urgency": triage_urgency,
            "status": "Confirmed",
            "created_at": datetime.utcnow()
        })

        flash(f"Appointment with {doctor_name} on {date_str} at {time_str} confirmed!", "success")
        return redirect(url_for("appointments.appointments_page"))
