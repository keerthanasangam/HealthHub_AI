from flask import render_template, request, jsonify, session
from datetime import datetime
from services.ai_service import AIService
from database.mongodb import triage_sessions, health_metrics


class ChatbotController:

    @staticmethod
    def render_chat():
        user = session.get("user")
        # Fetch latest BMI or water metrics if available
        user_metrics = {}
        if user and user.get("id"):
            metric_doc = health_metrics.find_one({"user_id": user["id"]})
            if metric_doc:
                user_metrics = metric_doc

        return render_template(
            "patient/chatbot.html",
            user=user,
            metrics=user_metrics
        )

    @staticmethod
    def chat_api():
        try:
            data = request.get_json() or {}
            message = data.get("message", "").strip()
            agent_type = data.get("agent", "triage").lower()  # triage | report | wellness
            user = session.get("user")

            if not message:
                return jsonify({"success": False, "error": "Message is required"}), 400

            if agent_type == "triage":
                result = AIService.triage_symptoms(message)

                # Persist triage summary in MongoDB if user is signed in
                if user and user.get("id"):
                    triage_sessions.insert_one({
                        "user_id": user["id"],
                        "user_name": user.get("name"),
                        "symptoms": message,
                        "urgency": result.get("urgency"),
                        "recommended_specialist": result.get("recommended_specialist"),
                        "badge": result.get("badge"),
                        "created_at": datetime.utcnow()
                    })

                return jsonify({"success": True, "data": result})

            elif agent_type == "report":
                result = AIService.explain_report(message)
                return jsonify({"success": True, "data": result})

            elif agent_type == "wellness":
                bmi = data.get("bmi")
                cups = data.get("water_cups")
                result = AIService.wellness_advice(bmi=bmi, water_cups=cups, query=message)
                return jsonify({"success": True, "data": result})

            else:
                # Default to triage
                result = AIService.triage_symptoms(message)
                return jsonify({"success": True, "data": result})

        except Exception as e:
            print(f"Error in chat_api: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
