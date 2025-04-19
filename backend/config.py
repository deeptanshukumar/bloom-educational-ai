import os

class Config:
    # Common configurations
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    # Service configurations
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bloom_dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')