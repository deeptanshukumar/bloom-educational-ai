from functools import wraps
from flask import request, jsonify

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        # Replace with your own logic or user database
        if not auth or not (auth.username == 'admin' and auth.password == 'password'):
            return jsonify({'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated