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
# This allows us to create them globally and then initialize them with app
# later in the create_app function, which is good practice for testing and
# factory patterns.
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """
    Creates and configures the Flask application.

    Args:
        config_name (str, optional): The name of the configuration to use
                                     (e.g., 'development', 'production').
                                     If None, it tries to get from FLASK_ENV
                                     or defaults to 'development'.
    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)

    # Determine which configuration to load.
    # It checks the FLASK_ENV environment variable, otherwise defaults to 'development'.
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Import configuration from the config.py file.
    # This loads settings like DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, etc.
    from config import config_by_name
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with the Flask app instance.
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure CORS to allow requests from the specified frontend URL.
    # This is crucial for allowing your React frontend to communicate with Flask.
    CORS(app, resources={r"/api/*": {"origins": app.config['FRONTEND_URL']}})

    # Import and register blueprints for API routes.
    # Blueprints modularize the application, making it scalable and organized.
    from backend.views.auth import auth_bp           # <--- THIS MUST BE 'auth_bp'
    from backend.views.item import item_bp           
    from backend.views.myrequest import request_bp   
    from backend.views.admin import admin_bp         


    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(item_bp, url_prefix='/api')
    app.register_blueprint(request_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin') # Admin routes usually have a distinct prefix

    # Import models so Flask-Migrate can detect them.
    # This is important for database migrations.
    from models import User, Item, Request, TokenBlocklist

    # JWT Error Handlers
    # These functions define how the application responds to JWT-related errors.

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        """Handler for missing JWT (401 Unauthorized)."""
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        """Handler for invalid JWT (422 Unprocessable Entity, often for malformed tokens)."""
        return jsonify({"msg": "Signature verification failed"}), 422

    @jwt.expired_token_loader
    def expired_token_response(callback):
        """Handler for expired JWT (401 Unauthorized)."""
        return jsonify({"msg": "Token has expired"}), 401
    
    @jwt.token_verification_loader
    def verify_token_callback(jwt_header, jwt_payload):
        """
        Custom token verification loader to check if the token is blacklisted.
        This function is called automatically by Flask-JWT-Extended during verification.
        """
        jti = jwt_payload['jti'] # Get the unique JWT ID
        is_blacklisted = TokenBlocklist.query.filter_by(jti=jti).first()
        return is_blacklisted is None # Return True if not blacklisted, False otherwise

    # Basic root route for health check or welcome message
    @app.route('/')
    def index():
        return jsonify({"message": "Flea Market API is running!"})

    return app

# When running app.py directly, create the app instance.
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) # Run in debug mode for development
