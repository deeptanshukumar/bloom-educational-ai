from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User

def admin_required(f):
    """
    Decorator to protect routes for admin users only
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        # Check if user exists and is admin
        user = User.query.get(current_user_id)
        if not user or not getattr(user, 'is_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name):
    """
    Decorator to protect routes based on user role
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # Check if user exists and has the required role
            user = User.query.get(current_user_id)
            # This assumes there's a roles relationship or attribute
            # You would need to implement this based on your role model
            if not user or role_name not in getattr(user, 'roles', []):
                return jsonify({'error': f'Role {role_name} required'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator