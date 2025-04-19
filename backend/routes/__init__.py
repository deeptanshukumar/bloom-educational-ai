from .auth_routes import auth_bp
from .tutor_routes import tutor_bp
from .screen_routes import screen_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tutor_bp, url_prefix='/api/tutor')
    app.register_blueprint(screen_bp, url_prefix='/api/screenpipe')