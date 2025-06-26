# backend/app.py
# This is the main application file for the Flea Market backend.
# It initializes the Flask app, database, migrations, JWT, CORS,
# and registers all the API blueprints.

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file.
# This ensures that variables like DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY,
# and FRONTEND_URL are available to the application.
load_dotenv()

# Initialize SQLAlchemy and Migrate without binding them to an app yet.
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # --- CRITICAL CHANGE HERE: Use fully qualified import ---
    from backend.config import config_by_name # Changed from 'from config'

    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with the Flask app instance.
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure CORS to allow requests from the specified frontend URL.
    # This is crucial for allowing your React frontend to communicate with Flask.
    # The FRONTEND_URL environment variable on Render should be comma-separated
    # if you have multiple origins (e.g., main Vercel + preview Vercel).
    allowed_origins = [url.strip() for url in app.config['FRONTEND_URL'].split(',')]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

    # Import and register blueprints for API routes.
    # --- CRITICAL CHANGE HERE: Use fully qualified imports for blueprints ---
    # Assuming your blueprints are in backend/views/
    from backend.views.auth import auth_bp           
    from backend.views.item import item_bp           
    from backend.views.myrequest import request_bp   # Changed from 'request' to 'myrequest' if that's the filename
    from backend.views.admin import admin_bp         

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(item_bp, url_prefix='/api')
    app.register_blueprint(request_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin') 

    # Import models so Flask-Migrate can detect them.
    # --- CRITICAL CHANGE HERE: Use fully qualified imports for models ---
    from backend.models import User, Item, Request, TokenBlacklist

    # JWT Error Handlers (rest of your code for JWT handlers)
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"msg": "Signature verification failed"}), 422

    @jwt.expired_token_loader
    def expired_token_response(callback):
        return jsonify({"msg": "Token has expired"}), 401
    
    @jwt.token_verification_loader
    def verify_token_callback(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        is_blacklisted = TokenBlacklist.query.filter_by(jti=jti).first()
        return is_blacklisted is None

    # Basic root route for health check or welcome message
    @app.route('/')
    def index():
        return jsonify({"message": "Flea Market API is running!"})

    return app

# When running app.py directly, create the app instance.
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
