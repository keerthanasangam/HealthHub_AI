import sys
import os

# =====================================================
# Add Project Root to Python Path
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

print(">>> Running backend/app.py <<<")

# =====================================================
# Imports
# =====================================================

from flask import Flask, render_template
from dotenv import load_dotenv
from database.mongodb import users
from routes.auth import auth
from routes.patient import patient_bp
from routes.bmi import bmi_bp
from routes.water import water_bp
from routes.medicine import medicine_bp
from routes.appointments import appointments_bp
from routes.chatbot import chatbot
from routes.doctor import doctor_bp

# =====================================================
# Load Environment Variables
# =====================================================

load_dotenv(os.path.join(BASE_DIR, "backend", ".env"))

# =====================================================
# Create Flask App
# =====================================================

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)

# =====================================================
# Flask Secret Key
# =====================================================

app.secret_key = os.getenv("SECRET_KEY", "healthhub-ai-super-secret-key-2026")

# =====================================================
# Register Blueprints
# =====================================================

app.register_blueprint(auth)
app.register_blueprint(patient_bp)
app.register_blueprint(bmi_bp)
app.register_blueprint(water_bp)
app.register_blueprint(medicine_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(chatbot)
app.register_blueprint(doctor_bp)


# =====================================================
# Routes
# =====================================================

@app.route("/")
def home():
    print("[OK] Home Route Executed")
    return render_template("index.html")


@app.route("/test-db")
def test_db():

    total_users = users.count_documents({})

    return f"""
    <h2>✅ MongoDB Connected Successfully</h2>
    <h3>Total Users : {total_users}</h3>
    """

# =====================================================
# Run Application
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)