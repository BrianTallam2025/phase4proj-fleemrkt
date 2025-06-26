# backend/config.py
import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file for local development
load_dotenv()

class Config:
    # Flask application's secret key for sessions, etc.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_should_be_changed'
    
    # JWT secret key for signing and verifying tokens.
    # It will be read from the 'JWT_SECRET_KEY' environment variable on Render.
    # The provided string '250426d50f8846a7a79f32fdb5248c8f251ee0fb09edcdbf'
    # will serve as a default fallback for local development if the env var isn't set.
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or '250426d50f8846a7a79f32fdb5248c8f251ee0fb09edcdbf'
    
    # SQLAlchemy database configuration.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT token expiration time.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24) 

    # --- REMOVED JWT_COOKIE_SECURE, JWT_COOKIE_SAMESITE, JWT_COOKIE_DOMAIN ---
    # These settings are only relevant if JWT_TOKEN_LOCATION is set to ['cookies'].
    # Since your frontend sends tokens in the Authorization header, these were causing conflicts.
    PROPAGATE_EXCEPTIONS = True # Helps with clearer error messages

    # Frontend URL for CORS. Should be a comma-separated list of origins in the Render environment variable.
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
