# backend/config.py
import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file for local development
# On Render, these will be set directly in the dashboard
load_dotenv()

class Config:
    # Flask application's secret key for sessions, etc.
    # It will be read from the 'SECRET_KEY' environment variable on Render.
    # Provide a strong default for local development.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_flask_app_secret_key_change_this_for_production'
    
    # JWT secret key for signing and verifying tokens.
    # It will be read from the 'JWT_SECRET_KEY' environment variable on Render.
    # This value MUST precisely match what's set on Render's environment.
    # The default is for local development fallback.
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key_for_dev_only_ensure_strong'
    
    # SQLAlchemy database configuration.
    # Prioritizes DATABASE_URL (for PostgreSQL on Render) or falls back to SQLite for local development.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT token expiration time.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24) 

    # --- IMPORTANT: JWT Cookie settings removed/commented out ---
    # These settings are only relevant if JWT_TOKEN_LOCATION is explicitly set to ['cookies'].
    # Your frontend sends JWTs in the Authorization header, so these settings were causing conflicts
    # leading to "Token signature verification failed" errors.
    # JWT_TOKEN_LOCATION defaults to ['headers'] which is what we want.
    # JWT_COOKIE_SECURE = True       
    # JWT_COOKIE_SAMESITE = "None"   
    # JWT_COOKIE_DOMAIN = ".onrender.com" 

    PROPAGATE_EXCEPTIONS = True # For clearer error messages during development

    # Frontend URL(s) for CORS. Should be a comma-separated list of origins in the Render environment variable.
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:5173'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

# Dictionary to easily select the configuration class based on the environment.
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig 
}
