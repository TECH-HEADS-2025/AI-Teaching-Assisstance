# In routes/some_blueprint.py
from flask import Blueprint, current_app, jsonify

some_bp = Blueprint('some_bp', __name__)

@some_bp.route('/use-ai/<prompt>')
def use_ai(prompt):
    # Access the AI function from anywhere in your app
    ai_response = current_app.get_ai_response(prompt)
    return jsonify({'response': ai_response})