import os

class Config:
    # Common configurations
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Base directory and database path
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASEDIR, 'instance')
    
    # Ensure instance directory exists with proper permissions
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR, mode=0o777, exist_ok=True)
    
    # Database configuration - use absolute path
    DB_FILE = os.path.join(INSTANCE_DIR, 'bloom_dev.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_FILE}'
    
    # API Keys
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    # Service configurations
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    UPLOAD_TIMEOUT = 300  # 5 minutes timeout for uploads
    REQUEST_TIMEOUT = 120  # 2 minutes timeout for regular requests
    
    # Upload configurations
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure uploads directory exists
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'mp3', 'wav'}
    
    # Session configurations
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # JWT configurations
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

    # CORS settings
    CORS_HEADERS = [
        'Content-Type',
        'Authorization',
        'Access-Control-Allow-Credentials',
        'Access-Control-Allow-Headers',
        'Access-Control-Allow-Methods',
        'Access-Control-Allow-Origin'
    ]
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    PREFERRED_URL_SCHEME = 'https'