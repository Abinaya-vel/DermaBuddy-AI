import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

from chatbot_configuration import SYSTEM_PROMPT


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


# ==================================================
# GEMINI CLIENT
# ==================================================

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not configured.")


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==================================================
# CHAT API
# ==================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "reply": "Please send a valid message."
            }), 400


        user_message = data.get("message", "").strip()


        if not user_message:
            return jsonify({
                "reply": "Please type a skincare question first. 🌸"
            }), 400


        # ------------------------------------------
        # Check API configuration
        # ------------------------------------------

        if client is None:

            return jsonify({
                "reply": (
                    "Gemini API is not configured. "
                    "Please add GEMINI_API_KEY to your .env file."
                )
            }), 500


        # ------------------------------------------
        # Build prompt
        # ------------------------------------------

        full_prompt = f"""
{SYSTEM_PROMPT}

USER QUESTION:
{user_message}

IMPORTANT:
Answer the user's question as DermaBuddy AI.
Give clear, friendly and practical skincare information.
Do not claim to diagnose medical conditions.
"""


        # ------------------------------------------
        # Gemini API call
        # ------------------------------------------

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
        )


        # ------------------------------------------
        # Get response text
        # ------------------------------------------

        if response and response.text:

            bot_reply = response.text.strip()

        else:

            bot_reply = (
                "Sorry, I couldn't generate a response right now. "
                "Please try again. 🌸"
            )


        return jsonify({
            "reply": bot_reply
        })


    except Exception as error:

        print("ERROR:", str(error))

        return jsonify({
            "reply": (
                "Sorry, something went wrong while processing "
                "your request. Please try again."
            )
        }), 500


# ==================================================
# HEALTH CHECK
# ==================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "online",
        "chatbot": "DermaBuddy AI"
    })


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )