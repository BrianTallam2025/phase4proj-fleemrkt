# backend/app.py
# This is the main application file for the Flea Market backend.
# It initializes the Flask app, database, migrations, JWT, CORS,
# and registers all the API blueprints.

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity, get_jwt # Removed create_access_token if not needed globally
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timezone # For token expiration in blacklist

# Load environment variables from .env file.
load_dotenv()

# Initialize SQLAlchemy, Migrate, and JWTManager without binding them to an app yet.
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager() # Initialize JWTManager globally as well

# Import models after db is initialized to prevent circular imports if models
# reference db or other extensions.
# Also ensures TokenBlacklist is correctly spelled.
from backend.models import User, Item, Request, TokenBlacklist, Rating 

# Import blueprints
from backend.views.auth import auth_bp           
from backend.views.item import item_bp           
from backend.views.myrequest import request_bp   
from backend.views.admin import admin_bp         


def create_app(config_name=None):
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    from backend.config import config_by_name
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with the Flask app instance.
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app) # Initialize JWTManager with the app here too

    # Parse allowed origins from environment variable
    allowed_origins = [url.strip() for url in app.config['FRONTEND_URL'].split(',')]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(item_bp, url_prefix='/api')
    app.register_blueprint(request_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # JWT Callbacks (for token blacklisting and user loading)
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity) # Use get for primary key lookup

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
        return token is not None

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"msg": "Signature verification failed"}), 422

    @jwt.expired_token_loader
    def expired_token_response(callback):
        return jsonify({"msg": "Token has expired"}), 401

    # --- Logout route for token blacklisting ---
    @app.route('/api/logout', methods=['POST'])
    @jwt_required()
    def logout():
        jti = get_jwt()["jti"]
        expires_timestamp = get_jwt()["exp"] # Get expiration timestamp
        expires = datetime.fromtimestamp(expires_timestamp, tz=timezone.utc) # Convert to datetime object with UTC timezone

        blacklisted_token = TokenBlacklist(jti=jti, expires=expires)
        db.session.add(blacklisted_token)
        db.session.commit()
        return jsonify(msg="Successfully logged out"), 200

    # Basic root route for health check or welcome message
    @app.route('/')
    def index():
        return jsonify({"message": "Flea Market API is running!"})

    return app

# --- CRITICAL GUNICORN FIX: Expose the app instance ---
# Gunicorn expects a callable named 'app' at the top level.
# We call create_app() here to get the Flask app instance for Gunicorn.
# We default to 'production' config when running with Gunicorn for deployment.
app = create_app(os.getenv('FLASK_ENV', 'production'))

# Note: The `if __name__ == '__main__':` block below will still run if you execute `python app.py` directly,
# but Gunicorn will use the `app` instance created above.
if __name__ == '__main__':
    # This block is primarily for local Flask development server
    # It allows running `python app.py` instead of `flask run` or gunicorn
    app.run(debug=True)
