# ai_service.py
import os
import openai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

class AIService:
    @staticmethod
    def generate_chat_response(prompt, context=None):
        """
        Generate a response using OpenAI's chat API
        """
        try:
            messages = []
            if context:
                # Add previous conversation context if available
                for message in context:
                    messages.append(message)
            
            # Add the current prompt
            messages.append({"role": "user", "content": prompt})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "status": "success",
                "response": response.choices[0].message.content,
                "full_response": response
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def generate_content(prompt, content_type="text"):
        """
        Generate content based on the prompt and content type
        content_type options: "text", "quiz", "explanation", "summary"
        """
        try:
            system_message = "You are an educational assistant."
            
            if content_type == "quiz":
                system_message = "Create a quiz with 5 multiple-choice questions based on the following topic:"
            elif content_type == "explanation":
                system_message = "Provide a detailed explanation of the following concept for students:"
            elif content_type == "summary":
                system_message = "Create a concise summary of the following educational content:"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return {
                "status": "success",
                "content": response.choices[0].message.content
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }