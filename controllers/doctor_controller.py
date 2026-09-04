from flask import render_template, request, jsonify, session, redirect, url_for
from database.mongodb import appointments, users, triage_sessions
from services.ai_service import AIService


class DoctorController:

    @staticmethod
    def render_dashboard():
        user = session.get("user")
        if not user or user.get("role") != "doctor":
            return redirect(url_for("auth.login"))

        doc_id = user.get("id")

        # Fetch appointments booked for this doctor (or all confirmed if demo)
        doc_appts = list(appointments.find({"status": "Confirmed"}).sort("date", 1))

        if not doc_appts:
            doc_appts = [
                {
                    "_id": "demo_p1",
                    "patient_name": "Keerthana S.",
                    "date": "Tomorrow",
                    "time": "10:30 AM",
                    "symptoms": "Throbbing migraine and neck tension for 3 days",
                    "triage_urgency": "yellow",
                    "status": "Confirmed"
                },
                {
                    "_id": "demo_p2",
                    "patient_name": "Arun Kumar",
                    "date": "Friday",
                    "time": "02:00 PM",
                    "symptoms": "Follow-up blood pressure check and fasting lipid panel",
                    "triage_urgency": "green",
                    "status": "Confirmed"
                }
            ]

        total_patients = len(doc_appts)

        return render_template(
            "doctor/dashboard.html",
            user=user,
            appointments=doc_appts,
            total_patients=total_patients
        )

    @staticmethod
    def generate_soap():
        data = request.get_json() or {}
        patient_name = data.get("patient_name", "Patient")
        symptoms = data.get("symptoms", "General checkup")
        history = data.get("history", "None reported")
        vitals = data.get("vitals", "BP: 120/80 mmHg, HR: 72 bpm")

        soap_result = AIService.draft_soap_note(patient_name, symptoms, history, vitals)
        return jsonify({"success": True, "data": soap_result})
