from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
from bson.objectid import ObjectId
from database.mongodb import medicines
from middleware.auth_middleware import login_required

medicine_bp = Blueprint("medicine", __name__, url_prefix="/patient")


@medicine_bp.route("/medicine", methods=["GET"])
def list_medicines():
    user = session.get("user")
    user_id = user["id"] if user else "guest"

    med_list = []
    if user and user.get("id"):
        med_list = list(medicines.find({"user_id": user["id"]}))
    else:
        # Sample starter medicines for demo
        med_list = [
            {
                "_id": "demo1",
                "name": "Vitamin D3",
                "dosage": "1000 IU",
                "timing": "Morning • With Breakfast",
                "frequency": "Once Daily",
                "taken_today": True
            },
            {
                "_id": "demo2",
                "name": "Amoxicillin",
                "dosage": "500 mg",
                "timing": "After Lunch & Dinner",
                "frequency": "Twice Daily",
                "taken_today": False
            },
            {
                "_id": "demo3",
                "name": "Omega-3 Fish Oil",
                "dosage": "1000 mg",
                "timing": "Night • With Dinner",
                "frequency": "Once Daily",
                "taken_today": False
            }
        ]

    taken_count = sum(1 for m in med_list if m.get("taken_today"))
    total_count = len(med_list)

    return render_template(
        "patient/medicine.html",
        user=user,
        medicines=med_list,
        taken_count=taken_count,
        total_count=total_count
    )


@medicine_bp.route("/medicine/add", methods=["POST"])
def add_medicine():
    user = session.get("user")
    name = request.form.get("name", "").strip()
    dosage = request.form.get("dosage", "").strip()
    timing = request.form.get("timing", "").strip()
    frequency = request.form.get("frequency", "Once Daily").strip()

    if not name or not dosage:
        flash("Medicine name and dosage are required", "error")
        return redirect(url_for("medicine.list_medicines"))

    if user and user.get("id"):
        medicines.insert_one({
            "user_id": user["id"],
            "name": name,
            "dosage": dosage,
            "timing": timing or "As directed",
            "frequency": frequency,
            "taken_today": False,
            "created_at": datetime.utcnow()
        })
        flash(f"Medication '{name}' added to your schedule.", "success")
    else:
        flash("Please sign in to save medications permanently.", "info")

    return redirect(url_for("medicine.list_medicines"))


@medicine_bp.route("/medicine/toggle/<med_id>", methods=["POST"])
def toggle_medicine(med_id):
    user = session.get("user")
    if user and user.get("id") and med_id != "demo1" and med_id != "demo2" and med_id != "demo3":
        try:
            med = medicines.find_one({"_id": ObjectId(med_id), "user_id": user["id"]})
            if med:
                new_status = not med.get("taken_today", False)
                medicines.update_one({"_id": ObjectId(med_id)}, {"$set": {"taken_today": new_status}})
                return jsonify({"success": True, "taken": new_status})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    return jsonify({"success": True, "taken": True})


@medicine_bp.route("/medicine/delete/<med_id>", methods=["POST"])
def delete_medicine(med_id):
    user = session.get("user")
    if user and user.get("id"):
        try:
            medicines.delete_one({"_id": ObjectId(med_id), "user_id": user["id"]})
            flash("Medication removed from schedule.", "success")
        except Exception:
            flash("Error deleting medication.", "error")
    return redirect(url_for("medicine.list_medicines"))
