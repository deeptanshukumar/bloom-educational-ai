from flask import Blueprint, request, jsonify
from services.groq_service import GroqService
from services.speech_service import SpeechService
from flask_jwt_extended import jwt_required
import os

ai_bp = Blueprint('ai', __name__)
groq_service = GroqService()
speech_service = SpeechService()

@ai_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    """Process an AI request and return the response"""
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400

        prompt = data['prompt']
        language = data.get('language', 'English')

        # Process with Groq
        result = groq_service.complete_prompt(prompt)
        
        if 'error' in result:
            return jsonify(result), 500

        # Extract the actual response text from Groq's response
        response_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        if not response_text:
            return jsonify({'error': 'No response generated'}), 500

        # Translate if needed (if not English)
        if language.lower() != 'english':
            translated = groq_service.translate_content(response_text, language)
            response_text = translated.get('choices', [{}])[0].get('message', {}).get('content', response_text)

        return jsonify({'response': response_text})

    except Exception as e:
        print(f"Error in AI analyze endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analyze-with-context', methods=['POST'])
@jwt_required()
def analyze_with_context():
    """Process an AI request with file context"""
    try:
        data = request.json
        if not data or 'content' not in data:
            return jsonify({'error': 'File content is required'}), 400

        content = data['content']
        file_type = data.get('fileType', '')
        language = data.get('language', 'English')

        # Create prompt with context
        prompt = f"""
        Analyze the following content from a {file_type} file:

        {content}

        Please provide:
        1. Summary of the content
        2. Key points or findings
        3. Any relevant insights or suggestions
        """

        # Process with Groq
        result = groq_service.complete_prompt(prompt)
        
        if 'error' in result:
            return jsonify(result), 500

        response_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        if not response_text:
            return jsonify({'error': 'No response generated'}), 500

        # Translate if needed
        if language.lower() != 'english':
            translated = groq_service.translate_content(response_text, language)
            response_text = translated.get('choices', [{}])[0].get('message', {}).get('content', response_text)

        return jsonify({'response': response_text})

    except Exception as e:
        print(f"Error in analyze with context: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/process-audio', methods=['POST'])
@jwt_required()
def process_audio():
    """Process audio input and return transcription"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        language = request.form.get('language', 'en')

        # Transcribe audio
        transcription = speech_service.transcribe_audio(audio_file, language)
        
        if not transcription:
            return jsonify({'error': 'Could not transcribe audio'}), 500

        return jsonify({
            'transcription': transcription,
            'status': 'success'
        })

    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return jsonify({'error': str(e)}), 500