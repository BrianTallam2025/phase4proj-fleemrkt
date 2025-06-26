# backend/app.py
# This is the main application file for the Flea Market backend.
# It initializes the Flask app, database, migrations, JWT, CORS,
# and registers all the API blueprints.

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request
)
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables from .env file.
load_dotenv()

# Initialize SQLAlchemy, Migrate, and JWTManager globally.
# These instances will be initialized with the app object within create_app().
from backend.extensions import db, bcrypt
migrate = Migrate() # Flask-Migrate instance
jwt = JWTManager() # Flask-JWT-Extended instance


# Import models and blueprints after extensions are globally initialized.
# This avoids circular import issues and ensures models/blueprints
# can access the 'db' object once it's fully initialized with the app.
from backend.models import User, Item, Request, TokenBlacklist, Rating 
from backend.views.auth import auth_bp           
from backend.views.item import item_bp           
from backend.views.myrequest import request_bp   
from backend.views.admin import admin_bp         


def create_app(config_name=None):
    """
    Creates and configures the Flask application.
    This function acts as an application factory.
    """
    app = Flask(__name__)

    # Determine which configuration to load (development, production, etc.)
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Import configuration settings from backend.config module and apply them to the app.
    from backend.config import config_by_name
    app.config.from_object(config_by_name[config_name])

    # --- CRITICAL: Initialize all extensions WITH THE APP instance ---
    # This must happen before models or blueprints that use 'db' are registered,
    # and it ensures Flask-Migrate's 'db' commands are available via the app context.
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db) # CRUCIAL: Binds Flask-Migrate to the app and db


    # Configure CORS to allow requests from the specified frontend URL(s).
    # This expects 'FRONTEND_URL' environment variable on Render to be comma-separated.
    allowed_origins = [url.strip() for url in app.config['FRONTEND_URL'].split(',')]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)


    # Register blueprints with their respective URL prefixes.
    # This organizes API routes into modular components.
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(item_bp, url_prefix='/api')
    app.register_blueprint(request_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # --- JWT Callbacks for token management and user loading ---
    # These functions are crucial for how Flask-JWT-Extended operates.

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Callback to load a user from the database given their ID (identity) from the JWT.
        Used by @jwt_required() to populate `current_user`.
        """
        identity = jwt_data["sub"] # 'sub' (subject) field holds the user ID
        return User.query.get(identity) # Retrieve user by primary key

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """
        Callback to check if a JWT's JTI (unique ID) is present in the blacklist.
        If found, the token is considered revoked.
        """
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
        return token is not None # Returns True if token is blacklisted, False otherwise

    # --- JWT Error Handlers ---
    # These define custom responses for various JWT-related errors.

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        """Handler for missing JWT (e.g., no Authorization header)."""
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        """Handler for invalid JWT (e.g., malformed token, invalid signature)."""
        return jsonify({"msg": "Token signature verification failed or token is malformed."}), 422 

    @jwt.expired_token_loader
    def expired_token_response(callback):
        """Handler for expired JWT."""
        return jsonify({"msg": "Token has expired"}), 401

    # --- API Routes defined directly in app.py (can be moved to blueprints) ---

    # Logout route for token blacklisting.
    # Requires a valid JWT to identify and blacklist the token.
    @app.route('/api/logout', methods=['POST'])
    @jwt_required() # Ensures only authenticated users can logout their token
    def logout():
        jti = get_jwt()["jti"] # Get the unique ID of the current token
        expires_timestamp = get_jwt()["exp"] # Get expiration timestamp (seconds since epoch)
        # Convert timestamp to datetime object with UTC timezone for database storage.
        expires = datetime.fromtimestamp(expires_timestamp, tz=timezone.utc) 

        # Add the token's JTI to the blacklist table.
        blacklisted_token = TokenBlacklist(jti=jti, expires=expires)
        db.session.add(blacklisted_token)
        db.session.commit()
        return jsonify(msg="Successfully logged out and token revoked"), 200

    # Basic root route for health check or welcome message.
    @app.route('/')
    def index():
        return jsonify({"message": "Flea Market API is running!"})

    # Example of a protected route defined directly in app.py
    # This route requires a valid JWT to access.
    @app.route('/api/protected', methods=['GET'])
    @jwt_required()
    def protected_route():
        current_user = get_jwt_identity() 
        return jsonify(logged_in_as={"user_id": current_user, "message": "Access granted to protected route!"}), 200

    return app

# --- CRITICAL: Global app instance for Gunicorn and Flask CLI ---
# Gunicorn expects a callable named 'app' at the top level of the module it loads.
# By calling create_app() here and assigning its return value to 'app',
# Gunicorn can find and run your Flask application.
# We explicitly pass the FLASK_ENV to ensure the correct configuration (e.g., 'production') is used.
app = create_app(os.getenv('FLASK_ENV', 'production'))

# Note: The `if __name__ == '__main__':` block below will still run if you execute `python app.py` directly,
# but Gunicorn will use the `app` instance created above.
if __name__ == '__main__':
    app.run(debug=True)
