# backend/config.py
import os
from dotenv import load_dotenv
from datetime import timedelta # Ensure timedelta is imported if used in Config

# Load environment variables from .env file for local development
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_should_be_changed'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'bab4bdd235864a4eaed6c1a64794d3fe'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24) # Ensure timedelta is imported if this line is active

    # JWT Cookie settings for cross-domain usage (important for Vercel/Render)
    JWT_COOKIE_SECURE = True       # Only send cookies over HTTPS
    JWT_COOKIE_SAMESITE = "None"   # Required for cross-domain
    # JWT_COOKIE_DOMAIN = ".onrender.com" # This might need to be .vercel.app or specific to frontend
                                      # Often best to let Flask-JWT-Extended handle it or set it dynamically
                                      # Remove or comment out if causing issues, or set to your frontend domain pattern.
    PROPAGATE_EXCEPTIONS = True    # For better error messages during development

    # Frontend URL for CORS. Should be comma-separated list of origins in Render env var.
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:5173'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

# This dictionary needs to be directly accessible when imported.
# Ensure its name is exactly 'config_by_name'.
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig 
}

# No explicit 'export' keyword in Python. Defining it at the top level
# like this makes it importable. The problem is usually a typo or
# an issue with how the interpreter is loading the file if this is set.

# Let's ensure the pathing is absolutely robust for SQLALCHEMY_DATABASE_URI
# by making basedir explicit as a top-level variable if needed.
# For Flask-Migrate to reliably find models, it should be able to load app.py and models.py.
