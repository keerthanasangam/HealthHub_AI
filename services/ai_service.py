import os
import re
from datetime import datetime

# Try importing google-generativeai
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False


class AIService:
    _model = None

    @classmethod
    def _init_gemini(cls):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key or api_key == "your_api_key" or not GENAI_AVAILABLE:
            return None

        if cls._model is None:
            try:
                genai.configure(api_key=api_key)
                cls._model = genai.GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                print(f"[WARN] Gemini init error: {e}")
                cls._model = None
        return cls._model

    # =========================================================================
    # AGENT 1: Dr. Triage (Symptom Assessment & Urgency Classifier)
    # =========================================================================
    @classmethod
    def triage_symptoms(cls, user_message, chat_history=None):
        """
        Analyzes symptoms, assigns urgency (green/yellow/red), suggests specialist,
        and generates an empathetic medical assessment.
        """
        model = cls._init_gemini()
        emergency_keywords = [
            "chest pain", "heart attack", "can't breathe", "cannot breathe", "shortness of breath",
            "stroke", "paralysis", "coughing blood", "unconscious", "passed out", "seizure",
            "overdose", "severe burn", "suicide", "bleeding heavily", "anaphylaxis"
        ]

        lower_msg = user_message.lower()
        is_red_alert = any(keyword in lower_msg for keyword in emergency_keywords)

        if is_red_alert:
            return {
                "urgency": "red",
                "badge": "EMERGENCY - URGENT CARE REQUIRED",
                "recommended_specialist": "Emergency Medicine / ER",
                "reply": (
                    "⚠️ **CRITICAL ALERT: Please Seek Immediate Emergency Care!**\n\n"
                    "The symptoms you described could indicate a life-threatening medical emergency. "
                    "**Do not wait or drive yourself:**\n"
                    "1. Call emergency services immediately (911 in the US, 112 in India/Europe, or your local emergency line).\n"
                    "2. Stay calm, rest in a seated or comfortable position, and notify someone nearby.\n"
                    "3. If experiencing chest pain or difficulty breathing, loosen tight clothing.\n\n"
                    "*HealthHub AI provides informational assistance only and cannot replace immediate emergency services.*"
                ),
                "summary": f"Emergency triage triggered by symptoms: '{user_message}'."
            }

        # Try Gemini API if available
        if model:
            system_prompt = (
                "You are Dr. Triage, an empathetic, highly knowledgeable AI clinical triage agent for HealthHub AI. "
                "Analyze the user's symptoms and respond warmly, professionally, and clearly. "
                "Structure your response with:\n"
                "1. **Clinical Assessment**: Likely possibilities (remind them this is not an official diagnosis).\n"
                "2. **Urgency Level**: Indicate Green (Mild/Self-Care) or Yellow (Consultation Advised).\n"
                "3. **Recommended Specialist**: (e.g. General Physician, Dermatologist, ENT, Orthopedic).\n"
                "4. **Home Care & Comfort Measures**: Safe self-care recommendations.\n"
                "5. **Red Flag Warnings**: Symptoms that mean they should seek urgent medical care.\n"
                "Keep the tone reassuring, concise, and easy to understand."
            )
            try:
                response = model.generate_content([system_prompt, user_message])
                urgency = "yellow" if any(w in lower_msg for w in ["fever", "pain", "swelling", "infection", "vomit", "dizzy", "headache"]) else "green"
                specialist = cls._deduce_specialist(lower_msg)
                return {
                    "urgency": urgency,
                    "badge": "CONSULTATION ADVISED" if urgency == "yellow" else "MILD / HOME CARE",
                    "recommended_specialist": specialist,
                    "reply": response.text,
                    "summary": f"Symptom assessment for: {user_message[:60]}..."
                }
            except Exception as e:
                print(f"Gemini triage fallback due to: {e}")

        # Intelligent Built-in Fallback Knowledge Engine
        return cls._mock_triage_engine(user_message)

    # =========================================================================
    # AGENT 2: MediLens (Report & Lab Explainer Agent)
    # =========================================================================
    @classmethod
    def explain_report(cls, report_text):
        """
        Translates complex medical reports and lab markers into plain English.
        """
        model = cls._init_gemini()

        if model:
            system_prompt = (
                "You are MediLens, an expert medical laboratory communicator for HealthHub AI. "
                "A patient has provided lab results or medical report notes. "
                "Explain each metric clearly and reassuringly:\n"
                "- Name of marker and its role in the body\n"
                "- What the patient's value indicates (Normal, Low, High)\n"
                "- Plain-English health takeaway\n"
                "- 3 smart, constructive questions the patient can ask their doctor\n"
                "Keep the tone empathetic and never panic the user."
            )
            try:
                response = model.generate_content([system_prompt, report_text])
                return {
                    "reply": response.text,
                    "timestamp": datetime.utcnow().strftime("%b %d, %Y %I:%M %p")
                }
            except Exception as e:
                print(f"Gemini report explanation fallback: {e}")

        return cls._mock_report_engine(report_text)

    # =========================================================================
    # AGENT 3: NutriHydra (Personalized Wellness & Hydration Coach)
    # =========================================================================
    @classmethod
    def wellness_advice(cls, bmi=None, water_cups=None, query=None):
        """
        Generates tailored hydration and nutrition guidance based on metrics.
        """
        model = cls._init_gemini()
        context = f"Patient context - BMI: {bmi or 'Not specified'}, Today's water intake: {water_cups or 0}/8 cups."
        prompt = f"{context} Question/Topic: {query or 'Provide customized hydration and wellness tips for my profile.'}"

        if model:
            system_prompt = (
                "You are NutriHydra, a certified wellness and hydration AI coach at HealthHub AI. "
                "Provide uplifting, science-backed lifestyle, hydration, and nutrition tips. "
                "Be encouraging, concise, with actionable bullet points and practical habits."
            )
            try:
                response = model.generate_content([system_prompt, prompt])
                return {"reply": response.text}
            except Exception as e:
                print(f"Gemini wellness fallback: {e}")

        return cls._mock_wellness_engine(bmi, water_cups, query)

    # =========================================================================
    # AGENT 4: DocScribe (Clinical SOAP Note Drafter for Doctors)
    # =========================================================================
    @classmethod
    def draft_soap_note(cls, patient_name, symptoms, history="None reported", vitals="Normal"):
        """
        Generates structured Subjective, Objective, Assessment, Plan notes for doctors.
        """
        model = cls._init_gemini()
        prompt = f"Patient: {patient_name}\nReported Symptoms: {symptoms}\nHistory: {history}\nVitals: {vitals}"

        if model:
            system_prompt = (
                "You are DocScribe, a clinical transcription and medical note assistant. "
                "Format a preliminary SOAP note for a healthcare provider to review, edit, and sign."
            )
            try:
                response = model.generate_content([system_prompt, prompt])
                return {"soap": response.text}
            except Exception as e:
                print(f"Gemini SOAP note fallback: {e}")

        return {
            "soap": (
                f"### Clinical SOAP Draft — {patient_name}\n"
                f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}\n\n"
                f"**Subjective (S):** Patient reports: {symptoms}. Medical History: {history}.\n\n"
                f"**Objective (O):** Vitals recorded: {vitals}. Physical exam pending consultation.\n\n"
                f"**Assessment (A):** Symptoms consistent with preliminary clinical review. Differential diagnoses pending.\n\n"
                f"**Plan (P):** 1. Conduct focused examination. 2. Order relevant confirmatory labs. 3. Formulate prescription and follow-up in 7 days."
            )
        }

    # =========================================================================
    # Private Helper & Fallback Engines
    # =========================================================================
    @staticmethod
    def _deduce_specialist(text):
        if any(w in text for w in ["skin", "rash", "acne", "itch", "mole"]):
            return "Dermatologist"
        if any(w in text for w in ["heart", "palpitation", "blood pressure", "cholesterol"]):
            return "Cardiologist"
        if any(w in text for w in ["bone", "joint", "knee", "back pain", "sprain"]):
            return "Orthopedic Specialist"
        if any(w in text for w in ["throat", "ear", "nose", "sinus", "cough", "cold"]):
            return "ENT / General Physician"
        if any(w in text for w in ["stomach", "acidity", "digestion", "nausea", "abdomen"]):
            return "Gastroenterologist"
        if any(w in text for w in ["eye", "vision", "blur"]):
            return "Ophthalmologist"
        if any(w in text for w in ["anxiety", "stress", "depression", "sleep", "insomnia"]):
            return "Psychiatrist / Wellness Counselor"
        return "General Physician"

    @classmethod
    def _mock_triage_engine(cls, msg):
        lower = msg.lower()
        specialist = cls._deduce_specialist(lower)
        urgency = "yellow" if any(w in lower for w in ["fever", "pain", "dizzy", "headache", "vomit", "infection"]) else "green"

        if urgency == "yellow":
            badge = "CONSULTATION ADVISED (YELLOW)"
            reply = (
                f"### 🩺 Dr. Triage Clinical Assessment\n\n"
                f"Thank you for sharing your symptoms. Based on your description (*\"{msg}\"*), here is a structured evaluation:\n\n"
                f"#### 1. Potential Considerations\n"
                f"Your symptoms could be linked to seasonal viral factors, inflammation, or mild stress-related physiological responses. A formal physical checkup will provide definitive answers.\n\n"
                f"#### 2. Recommended Healthcare Specialist\n"
                f"👉 **{specialist}**\n\n"
                f"#### 3. Recommended Home Care\n"
                f"- **Hydration**: Drink at least 2.5–3 liters of water or electrolyte liquids today.\n"
                f"- **Rest**: Avoid strenuous exertion and aim for 7–8 hours of quality sleep.\n"
                f"- **Monitoring**: Note any temperature changes or shifts in symptom intensity.\n\n"
                f"#### 4. When to Seek Urgent Care\n"
                f"If you develop high unyielding fever, difficulty breathing, or severe sudden pain, please proceed to immediate medical care.\n\n"
                f"*HealthHub AI provides guidance to help you prepare for your doctor visit.*"
            )
        else:
            badge = "MILD / HOME CARE (GREEN)"
            reply = (
                f"### 🌿 Dr. Triage Health Assessment\n\n"
                f"Your symptoms appear mild and manageable with proper rest and supportive care:\n\n"
                f"#### 1. Observations\n"
                f"No critical red flags are detected in your description. Your body is likely responding to daily fatigue, mild dehydration, or light strain.\n\n"
                f"#### 2. Suggested Next Steps\n"
                f"- Continue drinking water regularly throughout the day.\n"
                f"- Eat fresh, nutrient-dense meals with plenty of fruit and vegetables.\n"
                f"- If symptoms persist beyond 48–72 hours, schedule an appointment with a **{specialist}**.\n\n"
                f"Stay well, and feel free to ask more questions!"
            )

        return {
            "urgency": urgency,
            "badge": badge,
            "recommended_specialist": specialist,
            "reply": reply,
            "summary": f"Triage review for: {msg[:60]}"
        }

    @classmethod
    def _mock_report_engine(cls, text):
        return {
            "reply": (
                "### 🔬 MediLens Lab Report Breakdown\n\n"
                "Here is an accessible explanation of key markers commonly found in health reports:\n\n"
                "| Marker | Standard Range | Clinical Significance |\n"
                "| :--- | :--- | :--- |\n"
                "| **Fasting Blood Glucose** | 70 – 99 mg/dL | Indicates healthy blood sugar regulation |\n"
                "| **Hemoglobin (Hb)** | 12.0 – 16.5 g/dL | Oxygen-carrying protein in red blood cells |\n"
                "| **Total Cholesterol** | < 200 mg/dL | Overall circulating lipid level |\n"
                "| **Blood Pressure** | ~120/80 mmHg | Systolic / diastolic cardiovascular pressure |\n\n"
                "#### 💡 Key Takeaway\n"
                "If your readings fall within standard ranges, your baseline metabolic indicators look stable! For any highlighted or borderline values, lifestyle adaptations (such as balanced fiber intake and consistent cardio) can yield significant improvements.\n\n"
                "#### 📋 Questions to Ask Your Physician\n"
                "1. *Are my current readings consistent with my age and lifestyle profile?*\n"
                "2. *Do any of these borderline values require a follow-up test in 3–6 months?*\n"
                "3. *What specific dietary or activity adjustments would optimize these numbers?*"
            ),
            "timestamp": datetime.utcnow().strftime("%b %d, %Y %I:%M %p")
        }

    @classmethod
    def _mock_wellness_engine(cls, bmi=None, water_cups=None, query=None):
        bmi_val = float(bmi) if bmi else 22.5
        cups = int(water_cups) if water_cups else 4
        percent = min(100, int((cups / 8) * 100))

        status = "Normal / Balanced"
        if bmi_val < 18.5:
            status = "Underweight"
        elif bmi_val >= 25.0 and bmi_val < 30.0:
            status = "Overweight"
        elif bmi_val >= 30.0:
            status = "Obese"

        return {
            "reply": (
                f"### 💧 NutriHydra Personalized Wellness Plan\n\n"
                f"**Current Status:**\n"
                f"- **BMI:** `{bmi_val}` (*{status}*)\n"
                f"- **Hydration Progress:** `{cups}/8` cups ({percent}% of daily target)\n\n"
                f"#### 🎯 Daily Health Recommendations\n"
                f"1. **Hydration Goal**: Drink {max(1, 8 - cups)} more glass(es) before evening to hit your optimal 2.0L baseline. Staying hydrated directly assists cognitive sharpness and kidney filtration.\n"
                f"2. **Nutritional Balance**: Emphasize lean proteins, whole grains, and leafy greens. Pair water intake with hydrating foods like cucumbers, oranges, and watermelon.\n"
                f"3. **Physical Activity**: Aim for a 25–30 minute brisk walk or light aerobic session to sustain cardiovascular endurance.\n\n"
                f"*Consistency is the foundation of long-term vitality!*"
            )
        }
