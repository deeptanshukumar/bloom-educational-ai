from flask import Blueprint, request, jsonify
from services.groq_service import GroqService
from services.image_service import ImageService
from services.speech_service import SpeechService
import os

tutor_bp = Blueprint('tutor', __name__)

# Initialize services
groq_service = GroqService()
image_service = ImageService()
speech_service = SpeechService()

@tutor_bp.route('/process-text', methods=['POST'])
def process_text_problem():
    """Process a text-based problem submission"""
    data = request.json
    
    if not data or 'problem' not in data:
        return jsonify({'error': 'Problem text is required'}), 400
    
    problem_text = data['problem']
    subject = data.get('subject', 'mathematics')
    language = data.get('language', 'english')
    
    # Process with Groq
    result = groq_service.process_math_problem(problem_text, subject)
    
    # Translate if needed (if not English)
    if language.lower() != 'english':
        translated = groq_service.translate_content(
            result.get('choices', [{}])[0].get('message', {}).get('content', ''),
            language
        )
        result['translated'] = translated
    
    return jsonify(result)

@tutor_bp.route('/process-image', methods=['POST'])
def process_image_problem():
    """Process an image of a problem (e.g., handwritten math)"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    subject = request.form.get('subject', 'mathematics')
    language = request.form.get('language', 'english')
    
    # Process image to extract text/math
    extracted_text = image_service.extract_text_from_image(image_file)
    
    if not extracted_text:
        return jsonify({'error': 'Could not extract text from image'}), 400
    
    # Process with Groq
    result = groq_service.process_math_problem(extracted_text, subject)
    
    # Translate if needed
    if language.lower() != 'english':
        translated = groq_service.translate_content(
            result.get('choices', [{}])[0].get('message', {}).get('content', ''),
            language
        )
        result['translated'] = translated
    
    return jsonify(result)

@tutor_bp.route('/process-speech', methods=['POST'])
def process_speech_problem():
    """Process a spoken problem (audio file)"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio provided'}), 400
    
    audio_file = request.files['audio']
    subject = request.form.get('subject', 'mathematics')
    language = request.form.get('language', 'english')
    
    # Convert speech to text
    transcribed_text = speech_service.transcribe_audio(audio_file, language)
    
    if not transcribed_text:
        return jsonify({'error': 'Could not transcribe audio'}), 400
    
    # Process with Groq
    result = groq_service.process_math_problem(transcribed_text, subject)
    
    return jsonify(result)

@tutor_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Return list of supported languages"""
    languages = [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "zh", "name": "Chinese"},
        {"code": "hi", "name": "Hindi"},
        {"code": "ar", "name": "Arabic"},
        {"code": "ru", "name": "Russian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "ja", "name": "Japanese"}
    ]
    return jsonify(languages)