# app.py
from flask import Flask, render_template
from models import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, User
import requests
import json
import os

app = Flask(__name__)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # Redirect unauthorized users

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
def create_app():
    app = Flask(__name__)
    
    # Configure your app
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teacher_assistant.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.register_blueprint(auth_bp)
    
    # Add AI configuration
    try:
        import config
        app.config['AI_API_KEY'] = config.AI_API_KEY
        app.config['AI_ENDPOINT'] = config.AI_ENDPOINT
    except ImportError:
        # Fallback to environment variables if config.py doesn't exist
        app.config['AI_API_KEY'] = os.getenv('AI_API_KEY')
        app.config['AI_ENDPOINT'] = os.getenv('AI_ENDPOINT', 'https://api.openai.com/v1/chat/completions')
    
    
    # AI response function
    def get_ai_response(prompt):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {app.config["AI_API_KEY"]}'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}]
        }
        
        response = requests.post(
            app.config['AI_ENDPOINT'],
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code}, {response.text}"
    
    # Make the function available to the entire app
    app.get_ai_response = get_ai_response
    
    # Register blueprints
    try:
        from routes.assessment_routes import assessment_bp
        app.register_blueprint(assessment_bp)
    except ImportError as e:
        print(f"Warning: Could not import assessment blueprint: {e}")
    
    # Sample AI route (you can move this to a blueprint later)
    @app.route('/ai/ask/<question>')
    def ask_ai(question):
        response = get_ai_response(question)
        return {'response': response}
    
    return app

# This allows you to run the app with `python app.py`
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)