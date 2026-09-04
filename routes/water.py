from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
from database.mongodb import health_metrics

water_bp = Blueprint("water", __name__, url_prefix="/patient")


@water_bp.route("/water", methods=["GET"])
def water_tracker():
    user = session.get("user")
    cups = 4
    streak = 3

    if user and user.get("id"):
        doc = health_metrics.find_one({"user_id": user["id"]})
        if doc:
            cups = doc.get("water_cups", 4)
            streak = doc.get("water_streak", 3)

    return render_template(
        "patient/water_tracker.html",
        user=user,
        cups=cups,
        streak=streak
    )


@water_bp.route("/water/update", methods=["POST"])
def update_water():
    user = session.get("user")
    data = request.get_json() or {}
    cups = max(0, min(12, int(data.get("cups", 0))))

    if user and user.get("id"):
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        # If cups reached 8, update or reward streak
        streak_inc = 1 if cups >= 8 else 0

        health_metrics.update_one(
            {"user_id": user["id"]},
            {
                "$set": {
                    "water_cups": cups,
                    "water_ml": cups * 250,
                    "last_water_date": today_str,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    return jsonify({
        "success": True,
        "cups": cups,
        "ml": cups * 250,
        "percentage": min(100, int((cups / 8) * 100))
    })
