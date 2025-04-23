import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.file_service import file_service
from services.groq_service import GroqService

groq_service = GroqService()
from services.image_service import ImageService

image_service = ImageService()

import mimetypes

file_bp = Blueprint('file', __name__)

@file_bp.route('/session/create', methods=['POST'])
@jwt_required()
def create_session():
    """Create a new file upload session"""
    user_id = get_jwt_identity()
    session_id = file_service.create_session(user_id)
    return jsonify({
        'session_id': session_id,
        'message': 'Session created successfully'
    })

@file_bp.route('/upload/<session_id>', methods=['POST'])
@jwt_required()
def upload_file(session_id):
    """Upload a file to the session"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file was uploaded',
                'code': 'NO_FILE'
            }), 400
            
        file = request.files['file']
        if not file.filename:
            return jsonify({
                'error': 'No file was selected',
                'code': 'EMPTY_FILE'
            }), 400
            
        # Get additional text context if provided
        context = request.form.get('context', '')
        
        # Upload the file and get file info
        try:
            file_info = file_service.add_file_to_session(session_id, file)
        except ValueError as ve:
            return jsonify({
                'error': str(ve),
                'code': 'VALIDATION_ERROR'
            }), 400
        except IOError as ie:
            return jsonify({
                'error': f'File system error: {str(ie)}',
                'code': 'FILE_SYSTEM_ERROR'
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Failed to save file',
                'code': 'SAVE_ERROR',
                'details': str(e)
            }), 500
        
        # Process the file based on its type
        try:
            mime_type = file.content_type
            file_path = file_info['path']
            
            response_data = {
                'file_id': file_info['id'],
                'original_name': file_info['original_name'],
                'type': mime_type,
                'analysis': None
            }
            
            # Process different file types
            if mime_type.startswith('image/'):
                try:
                    extracted_text = image_service.extract_text_from_image(file_path)
                    if extracted_text:
                        prompt = f"Analyze this image content: {extracted_text}"
                        if context:
                            prompt += f"\nAdditional context provided by user: {context}"
                        analysis = groq_service.complete_prompt(prompt)
                        response_data['analysis'] = analysis
                except Exception as e:
                    response_data['error'] = 'Image processing failed'
                    response_data['error_details'] = str(e)
                    
            elif mime_type == 'application/pdf':
                if context:
                    response_data['context'] = context
                    
            elif mime_type.startswith('audio/'):
                if context:
                    response_data['context'] = context
                
            elif mime_type.startswith('text/'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        prompt = f"Analyze this text content: {content}"
                        if context:
                            prompt += f"\nAdditional context provided by user: {context}"
                        analysis = groq_service.complete_prompt(prompt)
                        response_data['analysis'] = analysis
                except UnicodeDecodeError:
                    response_data['error'] = 'Unable to read text file - invalid encoding'
                except Exception as e:
                    response_data['error'] = 'Text processing failed'
                    response_data['error_details'] = str(e)
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({
                'file_id': file_info['id'],
                'original_name': file_info['original_name'],
                'type': mime_type,
                'error': 'File processing failed',
                'error_details': str(e),
                'context': context if context else None
            })
            
    except Exception as e:
        return jsonify({
            'error': 'File upload failed',
            'code': 'UPLOAD_ERROR',
            'details': str(e)
        }), 500

@file_bp.route('/session/<session_id>/files', methods=['GET'])
@jwt_required()
def get_session_files(session_id):
    """Get list of files in a session"""
    try:
        files = file_service.get_session_files(session_id)
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@file_bp.route('/session/<session_id>/file/<file_id>', methods=['DELETE'])
@jwt_required()
def remove_file(session_id, file_id):
    """Remove a file from the session"""
    try:
        success = file_service.remove_file_from_session(session_id, file_id)
        if success:
            return jsonify({'message': 'File removed successfully'})
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/session/<session_id>', methods=['DELETE'])
@jwt_required()
def end_session(session_id):
    """End a file upload session and cleanup"""
    try:
        success = file_service.cleanup_session(session_id)
        if success:
            return jsonify({'message': 'Session ended successfully'})
        return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500