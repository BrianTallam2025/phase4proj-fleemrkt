# backend/config.py
import os
from datetime import timedelta 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_super_secret_key_that_should_be_random_and_long'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'another_very_secret_jwt_key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) 
