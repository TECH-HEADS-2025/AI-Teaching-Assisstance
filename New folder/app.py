import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from ai_service import AIService  # Importing the AI service

# Load environment variables
load_dotenv()

# Debugging log to check if API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERROR: OpenAI API key not found. Check your .env file!")
else:
    print("🔑 OpenAI Key Loaded Successfully")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route("/")
def home():
    return "BODH AI Backend is Running!"

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handles chatbot requests from the frontend.
    """
    try:
        data = request.json
        user_message = data.get("message", "").strip()
        chat_context = data.get("context", [])

        print(f"📩 User Message: {user_message}")  # Debugging log

        if not user_message:
            return jsonify({"status": "error", "response": "No message provided"}), 400

        # Call AIService to get response
        response = AIService.generate_chat_response(user_message, chat_context)

        print("🛠 AI Response:", response)  # Debugging log

        if response["status"] == "success":
            return jsonify({"status": "success", "response": response["response"]})
        else:
            return jsonify({"status": "error", "response": response["response"]}), 500

    except Exception as e:
        print("🚨 Error in chat endpoint:", str(e))
        return jsonify({"status": "error", "response": "Server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
