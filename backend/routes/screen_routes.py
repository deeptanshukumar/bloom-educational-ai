from flask import Blueprint, request, jsonify
from services.screen_service import ScreenService, DESKTOP_USE_AVAILABLE
from services.groq_service import GroqService

screen_bp = Blueprint('screen', __name__)

# Initialize services
screen_service = ScreenService()
groq_service = GroqService()

@screen_bp.route('/status', methods=['GET'])
def screen_service_status():
    """Check if screen monitoring service is connected and running"""
    is_connected = screen_service.is_connected
    features_available = DESKTOP_USE_AVAILABLE
    return jsonify({
        'status': 'connected' if is_connected else 'disconnected',
        'features_available': features_available,
        'message': 'Screen monitoring service is active' if is_connected 
                   else 'Limited functionality available - desktop_use features restricted'
    })

@screen_bp.route('/capture', methods=['GET'])
def capture_screen():
    """Capture current screen content"""
    return jsonify(screen_service.capture_screen_content())

@screen_bp.route('/start', methods=['POST'])
def start_monitoring():
    """Start screen monitoring"""
    if not DESKTOP_USE_AVAILABLE:
        return jsonify({
            'status': 'limited',
            'message': 'Started with limited functionality - desktop_use features not available'
        })
    return jsonify(screen_service.start_monitoring())

@screen_bp.route('/stop', methods=['POST'])
def stop_monitoring():
    """Stop screen monitoring"""
    return jsonify(screen_service.stop_monitoring())

@screen_bp.route('/analyze', methods=['POST'])
def analyze_screen_content():
    """Analyze captured screen content using Groq for educational insights"""
    if not screen_service.is_connected and not DESKTOP_USE_AVAILABLE:
        return jsonify({
            'status': 'limited',
            'message': 'Operating with limited functionality'
        })
    
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
        'analysis': analysis,
        'status': 'success' if DESKTOP_USE_AVAILABLE else 'limited'
    })

@screen_bp.route('/monitor-app', methods=['POST'])
def monitor_specific_application():
    """Monitor a specific application (e.g., calculator, notepad)"""
    if not DESKTOP_USE_AVAILABLE:
        return jsonify({
            'error': 'Desktop use functionality not available',
            'status': 'failed'
        }), 503
    
    if not screen_service.is_connected:
        return jsonify({
            'error': 'Screen service not connected',
            'status': 'failed'
        }), 503
    
    data = request.json
    app_name = data.get('application', '')
    
    if not app_name:
        return jsonify({'error': 'Application name is required'}), 400
    
    monitoring_result = screen_service.monitor_math_application(app_name)
    
    return jsonify(monitoring_result)