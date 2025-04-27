from flask import Flask
from routes.auth_routes import auth_bp
from routes.ai_routes import ai_bp
from routes.file_routes import file_bp
from routes.screen_routes import screen_bp
from routes.tutor_routes import tutor_bp

def register_routes(app: Flask):
    """Register all blueprint routes"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(file_bp, url_prefix='/api/file')
    app.register_blueprint(screen_bp, url_prefix='/api/screen')
    app.register_blueprint(tutor_bp, url_prefix='/api/tutor')