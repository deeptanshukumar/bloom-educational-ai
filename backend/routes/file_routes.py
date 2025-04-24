from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.file_service import file_service
from services.groq_service import GroqService
from services.image_service import ImageService
from werkzeug.exceptions import BadRequest, NotFound
import base64
import magic
import os
import PyPDF2

groq_service = GroqService()
image_service = ImageService()

file_bp = Blueprint('file', __name__)

def get_file_mime_type(file_path):
    """Get the true MIME type of a file using python-magic"""
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

def extract_pdf_text(file_path):
    """Extract text from PDF with page numbers"""
    pdf_content = []
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    pdf_content.append(f"Page {page_num}:\n{text.strip()}")
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")
    return "\n\n".join(pdf_content) if pdf_content else None

def analyze_file_content(file_path, mime_type, context=None):
    """Analyze file content based on its type"""
    try:
        if mime_type.startswith('image/'):
            with open(file_path, 'rb') as f:
                base64_image = base64.b64encode(f.read()).decode('utf-8')
                return groq_service.analyze_image(base64_image)
        
        elif mime_type == 'application/pdf':
            content = extract_pdf_text(file_path)
            if not content:
                raise RuntimeError("No readable text found in PDF")
            return groq_service.analyze_file_content(content, mime_type, context)
        
        elif mime_type.startswith('text/') or mime_type in ['application/json', 'application/xml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return groq_service.analyze_file_content(content, mime_type, context)
        
        else:
            # For other file types, try to read as text first
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return groq_service.analyze_file_content(
                    content,
                    mime_type,
                    "This file type is not directly supported, but I'll try to analyze its text content. " + (context or "")
                )
            except UnicodeDecodeError:
                return {
                    'choices': [{
                        'message': {
                            'content': "This file type cannot be analyzed directly. Please provide specific questions about what you'd like to know about this file."
                        }
                    }]
                }

    except Exception as e:
        raise RuntimeError(f"Failed to analyze file content: {str(e)}")

@file_bp.route('/session/create', methods=['POST'])
@jwt_required()
def create_session():
    """Create a new file upload session"""
    try:
        session_id = file_service.create_session()
        return jsonify({
            'session_id': session_id,
            'message': 'Session created successfully'
        })
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/upload/<session_id>', methods=['POST'])
@jwt_required()
def upload_file(session_id):
    """Upload a file to the session and analyze it with AI"""
    try:
        if 'file' not in request.files:
            raise BadRequest('No file was uploaded')
            
        file = request.files['file']
        if not file.filename:
            raise BadRequest('No file was selected')
        
        context = request.form.get('context', '')
        
        try:
            file_info = file_service.add_file_to_session(session_id, file)
        except (ValueError, IOError) as e:
            return jsonify({
                'error': str(e),
                'code': 'SAVE_ERROR'
            }), 400
        
        try:
            file_path = file_info['path']
            claimed_mime_type = file.content_type
            actual_mime_type = get_file_mime_type(file_path)
            
            response_data = {
                'file_id': file_info['id'],
                'original_name': file_info['original_name'],
                'type': actual_mime_type,
                'analysis': None,
                'error': None
            }
            
            try:
                result = analyze_file_content(file_path, actual_mime_type, context)
                if result and 'choices' in result:
                    response_data['analysis'] = result['choices'][0]['message']['content']
                else:
                    response_data['error'] = 'Failed to get AI response'
            except Exception as e:
                response_data['error'] = f'Analysis failed: {str(e)}'
            
            if response_data['error']:
                print(f"Error processing file {file.filename}: {response_data['error']}")
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({
                'file_id': file_info['id'],
                'original_name': file_info['original_name'],
                'type': claimed_mime_type,
                'error': str(e)
            }), 400
            
    except BadRequest as e:
        return jsonify({
            'error': str(e),
            'code': 'INVALID_REQUEST'
        }), 400
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'PROCESSING_ERROR'
        }), 500

@file_bp.route('/session/<session_id>/files', methods=['GET'])
@jwt_required()
def get_session_files(session_id):
    """Get list of files in a session"""
    try:
        files = file_service.get_session_files(session_id)
        return jsonify({'files': files})
    except (ValueError, IOError) as e:
        return jsonify({'error': str(e)}), 404
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/session/<session_id>/file/<file_id>', methods=['DELETE'])
@jwt_required()
def remove_file(session_id, file_id):
    """Remove a file from the session"""
    try:
        if file_service.remove_file_from_session(session_id, file_id):
            return jsonify({'message': 'File removed successfully'})
        raise NotFound('File not found')
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except (ValueError, IOError, RuntimeError) as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/session/<session_id>', methods=['DELETE'])
@jwt_required()
def end_session(session_id):
    """End a file upload session and cleanup"""
    try:
        if file_service.cleanup_session(session_id):
            return jsonify({'message': 'Session ended successfully'})
        raise NotFound('Session not found')
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except (ValueError, RuntimeError) as e:
        return jsonify({'error': str(e)}), 500
    except OSError as e:
        return jsonify({'error': 'Failed to cleanup session files'}), 500