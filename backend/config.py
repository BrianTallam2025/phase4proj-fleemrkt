# backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development
# On Render, these will be set directly in the dashboard
load_dotenv()

class Config:
    # Use os.environ.get to fetch from environment variables.
    # Provide a default for local development, but ensure these are set strongly in production.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_for_dev_only_change_me'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super_secret_jwt_key_for_dev_only_change_me'

    # Database URI: Prioritize DATABASE_URL (for Render/PostgreSQL) or fall back to SQLite for local development
    # IMPORTANT: For production, DATABASE_URL should point to a PostgreSQL database
    # For local testing with SQLite, 'sqlite:///site.db' is fine.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Set to False in production for better performance and security
    DEBUG = os.environ.get('FLASK_DEBUG') == '1'
    JWT_COOKIE_SECURE = True  # Only send cookies over HTTPS
    JWT_COOKIE_SAMESITE = "None"  # Required for cross-domain
    JWT_COOKIE_DOMAIN = ".onrender.com"  # Note the leading dot
    PROPAGATE_EXCEPTIONS = True  # Better error messages