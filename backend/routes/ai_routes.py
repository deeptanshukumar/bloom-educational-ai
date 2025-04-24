from flask import Blueprint, request, jsonify
from services.groq_service import GroqService
from services.speech_service import SpeechService
from flask_jwt_extended import jwt_required
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
from requests.exceptions import RequestException

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
            raise BadRequest('Prompt is required')

        prompt = data['prompt']
        if not prompt or not prompt.strip():
            raise BadRequest('Prompt cannot be empty')

        language = data.get('language', 'English')

        # Process with Groq
        result = groq_service.complete_prompt(prompt)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'error': result['error']}), 500

        # Extract the actual response text from Groq's response
        response_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        if not response_text:
            return jsonify({'error': 'No response generated'}), 500

        # Translate if needed (if not English)
        if language.lower() != 'english':
            translated = groq_service.translate_content(response_text, language)
            if translated and 'choices' in translated:
                response_text = translated['choices'][0]['message']['content']

        return jsonify({
            'response': response_text,
            'status': 'success'
        })

    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except (RequestException, RuntimeError) as e:
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

    except (RequestException, RuntimeError) as e:
        print(f"Error in analyze with context: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/process-audio', methods=['POST'])
@jwt_required()
def process_audio():
    """Process audio input and return transcription"""
    try:
        if 'audio' not in request.files:
            raise BadRequest('No audio file provided')

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

    except (BadRequest, RuntimeError) as e:
        print(f"Error processing audio: {str(e)}")
        return jsonify({'error': str(e)}), 400 if isinstance(e, BadRequest) else 500

@ai_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze an image using Groq's vision model"""
    try:
        if 'image' in request.files:
            # Handle file upload
            image = request.files['image']
            if not image.filename:
                raise BadRequest('No image file provided')
            
            # Save the file temporarily
            filename = secure_filename(image.filename)
            temp_path = os.path.join('/tmp', filename)
            image.save(temp_path)
            
            try:
                # Get the query from form data or use default
                query = request.form.get('query', "What's in this image?")
                result = groq_service.analyze_local_image(temp_path, query)
                return jsonify(result)
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        elif 'image_url' in request.json:
            # Handle image URL
            image_url = request.json['image_url']
            query = request.json.get('query', "What's in this image?")
            result = groq_service.analyze_image(image_url, query, is_url=True)
            return jsonify(result)
            
        else:
            raise BadRequest('No image or image URL provided')
            
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except (RequestException, RuntimeError, OSError) as e:
        print(f"Error processing image: {str(e)}")
        return jsonify({'error': str(e)}), 500