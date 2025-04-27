from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from models import db
from datetime import timedelta
import os
from flask_jwt_extended import JWTManager
from models.blacklist import blacklist
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load configuration
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    # Initialize extensions
    db.init_app(app)
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/bloom_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    @app.route('/')
    def index():
        return "Welcome to the Bloom API!"
    
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in blacklist

    # Import models here to avoid circular imports
    from models.user import User
    from models.session import Session, Interaction

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.tutor_routes import tutor_bp
    from routes.screen_routes import screen_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tutor_bp, url_prefix='/api/tutor')
    app.register_blueprint(screen_bp, url_prefix='/api/screen')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)