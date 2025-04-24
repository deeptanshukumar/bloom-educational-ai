from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
import os
from models.blacklist import blacklist
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig

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
            "max_age": 3600,
            "supports_credentials": True
        }
    })

    # Initialize extensions
    db.init_app(flask_app)
    jwt = JWTManager(flask_app)

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

if __name__ == '__main__':
    with app.app_context():
        # Ensure the database directory exists
        db_dir = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        os.makedirs(db_dir, exist_ok=True)
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)