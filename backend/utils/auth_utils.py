from flask_jwt_extended import get_jwt_identity
from models.user import User
from flask import jsonify

def get_current_user():
    """
    Get the current user from JWT token
    Returns user object or None
    """
    try:
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except:
        return None

def user_to_dict(user):
    """
    Convert a user object to a dictionary for JSON response
    Excludes sensitive information like password hash
    """
    if not user:
        return None
        
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'roles': [role.name for role in user.roles],
        'created_at': user.created_at.isoformat(),
        'is_active': user.is_active
    }

def authorize_session_access(session_id, user_id):
    """
    Check if a user is authorized to access a specific tutoring session
    Example use case: only allow users to access their own sessions
    """
    from models.session import Session
    
    session = Session.query.get(session_id)
    if not session:
        return False
        
    # Check if the user owns this session
    if session.user_id == user_id:
        return True
        
    # Check if user has admin privileges
    user = User.query.get(user_id)
    if user and user.is_admin:
        return True
        
    return False