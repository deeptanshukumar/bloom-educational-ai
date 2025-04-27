from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
import os
from models.blacklist import blacklist
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig
import logging
from init_db import init_database
load_dotenv()

def create_app(config_class=DevelopmentConfig):
    # Ensure instance directory exists
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    flask_app = Flask(__name__, instance_path=instance_path)
    flask_app.config.from_object(config_class)

    # Configure CORS with longer timeout
    CORS(flask_app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Authorization"],
            "max_age": 3600,
            "supports_credentials": True
        }
    })

    # Initialize extensions
    db.init_app(flask_app)
    jwt = JWTManager(flask_app)

    # Initialize database and create initial user
    with flask_app.app_context():
        db.create_all()
        init_database()

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(_, jwt_payload):
        jti = jwt_payload['jti']
        return jti in blacklist

    # Register routes
    with flask_app.app_context():
        from routes import register_routes
        register_routes(flask_app)

    @flask_app.route('/')
    def index():
        return "Welcome to the Bloom API!"

    return flask_app

# Create the application instance
app = create_app(DevelopmentConfig if os.environ.get('FLASK_ENV') == 'development' else ProductionConfig)

# Add after app creation
app.logger.setLevel(logging.DEBUG)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    try:
        body = request.get_json()
        app.logger.debug('Body: %s', body)
    except Exception:
        app.logger.debug('Body: %s', request.get_data())
    app.logger.debug('URL: %s', request.url)
    app.logger.debug('Method: %s', request.method)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)