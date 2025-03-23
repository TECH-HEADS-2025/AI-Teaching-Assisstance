# routes/ai_routes.py
from flask import Blueprint, request, jsonify
from services.ai_service import AIService

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    prompt = data['prompt']
    context = data.get('context', None)
    
    response = AIService.generate_chat_response(prompt, context)
    
    if response['status'] == 'error':
        return jsonify({"error": response['error']}), 500
    
    return jsonify({"response": response['response']})

@ai_bp.route('/generate', methods=['POST'])
def generate_content():
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    prompt = data['prompt']
    content_type = data.get('content_type', 'text')
    
    response = AIService.generate_content(prompt, content_type)
    
    if response['status'] == 'error':
        return jsonify({"error": response['error']}), 500
    
    return jsonify({"content": response['content']})