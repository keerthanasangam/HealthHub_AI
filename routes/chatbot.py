from flask import Blueprint
from controllers.chatbot_controller import ChatbotController
from middleware.auth_middleware import login_required

chatbot = Blueprint(
    "chatbot",
    __name__
)


@chatbot.route("/patient/chatbot", methods=["GET"])
def chatbot_page():
    return ChatbotController.render_chat()


@chatbot.route("/api/chat", methods=["POST"])
def api_chat():
    return ChatbotController.chat_api()
