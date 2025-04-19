from flask import Blueprint, request, jsonify
from services.screen_service import ScreenService
from services.groq_service import GroqService

screen_bp = Blueprint('screen', __name__)

# Initialize services
screen_service = ScreenService()
groq_service = GroqService()

@screen_bp.route('/status', methods=['GET'])
def screen_service_status():
    """Check if screen monitoring service is connected and running"""
    is_connected = screen_service.is_connected
    return jsonify({
        'status': 'connected' if is_connected else 'disconnected',
        'message': 'Screen monitoring service is active' if is_connected 
                   else 'Not connected to Terminator server'
    })

@screen_bp.route('/capture', methods=['GET'])
def capture_current_screen():
    """Capture current screen content for analysis"""
    if not screen_service.is_connected:
        return jsonify({'error': 'Screen service not connected'}), 503
    
    screen_content = screen_service.capture_screen_content()
    
    return jsonify(screen_content)

@screen_bp.route('/analyze', methods=['POST'])
def analyze_screen_content():
    """Analyze captured screen content using Groq for educational insights"""
    if not screen_service.is_connected:
        return jsonify({'error': 'Screen service not connected'}), 503
    
    data = request.json
    content = data.get('content', '')
    subject = data.get('subject', 'general')
    
    if not content:
        # If no content provided, capture from screen
        screen_data = screen_service.capture_screen_content()
        content = screen_data.get('content', '')
    
    if not content:
        return jsonify({'error': 'No content available for analysis'}), 400
    
    # Analyze content with Groq
    prompt = f"""
    Analyze the following content from a student's screen for the subject {subject}:
    
    {content}
    
    Please provide:
    1. Identification of the topic or problem
    2. Any potential misconceptions or errors
    3. Helpful suggestions or tips
    4. Resources that might be valuable
    """
    
    analysis = groq_service.complete_prompt(prompt)
    
    return jsonify({
        'original_content': content,
        'analysis': analysis
    })

@screen_bp.route('/monitor-app', methods=['POST'])
def monitor_specific_application():
    """Monitor a specific application (e.g., calculator, notepad)"""
    if not screen_service.is_connected:
        return jsonify({'error': 'Screen service not connected'}), 503
    
    data = request.json
    app_name = data.get('application', '')
    
    if not app_name:
        return jsonify({'error': 'Application name is required'}), 400
    
    monitoring_result = screen_service.monitor_math_application(app_name)
    
    return jsonify(monitoring_result)