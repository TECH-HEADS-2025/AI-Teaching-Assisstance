import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("❌ ERROR: OpenAI API Key is missing! Check your .env file.")

class AIService:
    @staticmethod
    def generate_chat_response(prompt, context=None):
        """
        Generate a response using OpenAI's chat API
        """
        try:
            messages = context if context else []
            messages.append({"role": "user", "content": prompt})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            print("✅ OpenAI API Response:", response)  # Debugging log

            return {
                "status": "success",
                "response": response["choices"][0]["message"]["content"]
            }

        except Exception as e:
            print("❌ OpenAI API Error:", str(e))  # Debugging log
            return {
                "status": "error",
                "response": "AI Service error: " + str(e)
            }
