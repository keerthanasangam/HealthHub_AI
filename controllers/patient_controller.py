from flask import render_template, session, redirect, url_for
from database.mongodb import health_metrics, appointments, medicines, triage_sessions


class PatientController:

    @staticmethod
    def render_dashboard():
        user = session.get("user")
        if not user:
            return redirect(url_for("auth.login"))

        user_id = user["id"]

        # Health metrics
        metrics = health_metrics.find_one({"user_id": user_id}) or {}
        water_cups = metrics.get("water_cups", 0)
        water_percent = min(100, int((water_cups / 8) * 100))
        bmi = metrics.get("bmi", "--")
        bmi_cat = metrics.get("bmi_category", "Not calculated")

        # Upcoming appointments
        user_appts = list(appointments.find({"patient_id": user_id, "status": "Confirmed"}).sort("date", 1))
        next_appt = user_appts[0] if user_appts else None

        # Medicines
        user_meds = list(medicines.find({"user_id": user_id}))
        taken_meds = sum(1 for m in user_meds if m.get("taken_today"))
        total_meds = len(user_meds)

        # Recent Triage
        recent_triage = list(triage_sessions.find({"user_id": user_id}).sort("created_at", -1).limit(3))

        return render_template(
            "patient/dashboard.html",
            user=user,
            water_cups=water_cups,
            water_percent=water_percent,
            bmi=bmi,
            bmi_cat=bmi_cat,
            next_appt=next_appt,
            total_appts=len(user_appts),
            taken_meds=taken_meds,
            total_meds=total_meds,
            recent_triage=recent_triage
        )
