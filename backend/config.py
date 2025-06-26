import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Core Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))
    PROPAGATE_EXCEPTIONS = True
    
    # Database Config
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 0
    }

    # JWT Config
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.urandom(32))
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = 'None'
    JWT_COOKIE_DOMAIN = '.onrender.com'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_SESSION_COOKIE = False  # Prevents conflicts with Flask's session cookie

    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_SAMESITE = 'None'