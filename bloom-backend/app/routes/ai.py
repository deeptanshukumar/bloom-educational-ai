from flask import Blueprint, request, jsonify, session
from app.services.groq_service import GroqAssistant
from app.utils.auth import login_required

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    # Implementation from app.py chat endpoint
    # ... [existing chat logic] ...