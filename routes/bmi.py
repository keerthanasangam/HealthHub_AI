from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
from database.mongodb import health_metrics

bmi_bp = Blueprint("bmi", __name__, url_prefix="/patient")


def calculate_bmi_details(weight_kg, height_cm):
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
        color = "#F59E0B"
        badge = "warning"
        advice = "Focus on nutrient-dense, calorie-rich wholesome foods and strength training."
    elif bmi <= 24.9:
        category = "Normal Weight"
        color = "#10B981"
        badge = "success"
        advice = "Great job! Maintain your balanced diet, hydration, and regular exercise."
    elif bmi <= 29.9:
        category = "Overweight"
        color = "#F97316"
        badge = "warning"
        advice = "Incorporate 30 minutes of daily cardio and mindful portion control."
    else:
        category = "Obese"
        color = "#EF4444"
        badge = "danger"
        advice = "Consider consulting with a physician or nutritionist for a structured wellness plan."

    min_ideal = round(18.5 * (height_m ** 2), 1)
    max_ideal = round(24.9 * (height_m ** 2), 1)

    return {
        "bmi": bmi,
        "category": category,
        "color": color,
        "badge": badge,
        "advice": advice,
        "ideal_weight_range": f"{min_ideal} kg - {max_ideal} kg"
    }


@bmi_bp.route("/bmi", methods=["GET", "POST"])
def bmi_calculator():
    user = session.get("user")
    latest_result = None

    if request.method == "POST":
        try:
            # Check if JSON request or Form submit
            if request.is_json:
                data = request.get_json()
                weight = float(data.get("weight"))
                height = float(data.get("height"))
            else:
                weight = float(request.form.get("weight"))
                height = float(request.form.get("height"))

            latest_result = calculate_bmi_details(weight, height)

            # Persist in DB if logged in
            if user and user.get("id"):
                health_metrics.update_one(
                    {"user_id": user["id"]},
                    {
                        "$set": {
                            "bmi": latest_result["bmi"],
                            "bmi_category": latest_result["category"],
                            "weight": weight,
                            "height": height,
                            "updated_at": datetime.utcnow()
                        },
                        "$push": {
                            "bmi_history": {
                                "bmi": latest_result["bmi"],
                                "weight": weight,
                                "date": datetime.utcnow().strftime("%Y-%m-%d")
                            }
                        }
                    },
                    upsert=True
                )

            if request.is_json:
                return jsonify({"success": True, "data": latest_result})

        except (ValueError, TypeError, ZeroDivisionError) as e:
            if request.is_json:
                return jsonify({"success": False, "error": "Invalid weight or height values"}), 400

    # If GET, load existing metric if user logged in
    if user and user.get("id"):
        doc = health_metrics.find_one({"user_id": user["id"]})
        if doc and doc.get("weight") and doc.get("height"):
            latest_result = calculate_bmi_details(doc["weight"], doc["height"])

    return render_template("patient/bmi.html", user=user, result=latest_result)
