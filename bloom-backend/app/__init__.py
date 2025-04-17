from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    CORS(app)
    db.init_app(app)
    limiter.init_app(app)
    
    with app.app_context():
        from .routes.ai import ai_bp
        from .routes.terminator import terminator_bp
        from .routes.auth import auth_bp
        app.register_blueprint(ai_bp)
        app.register_blueprint(terminator_bp)
        app.register_blueprint(auth_bp)
        
        db.create_all()
        
    return app