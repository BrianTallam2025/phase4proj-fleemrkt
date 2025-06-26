# backend/app.py
# This is the main application file for the Flea Market backend.
# It initializes the Flask app, database, migrations, JWT, CORS,
# and registers all the API blueprints.

import os
from flask import Flask, jsonify, request
# Consolidated Flask-JWT-Extended imports for all used components
from flask_jwt_extended import (
    JWTManager,
    jwt_required,         # Needed for protected routes
    create_access_token,  # Needed for login
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request # Often used implicitly by jwt_required, but good to have if needed directly
)
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timezone # For token expiration in blacklist

# Load environment variables from .env file.
load_dotenv()

# Initialize extensions globally, but NOT with an app yet.
# These will be initialized with the app inside create_app().
from backend.extensions import db, bcrypt # Import db and bcrypt here
jwt = JWTManager() # JWTManager also needs to be initialized globally


def create_app(config_name=None):
    """
    Creates and configures the Flask application.
    This function acts as an application factory.
    """
    app = Flask(__name__)

    # Determine which configuration to load (development, production, etc.)
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Import configuration settings from backend.config module
    from backend.config import config_by_name
    app.config.from_object(config_by_name[config_name])

    # --- CRITICAL FIX: Initialize extensions WITH THE APP first ---
    db.init_app(app)
    bcrypt.init_app(app) # Initialize bcrypt with the app
    jwt.init_app(app) # Bind JWTManager to the app

    # --- CRITICAL FIX: Import models and blueprints *AFTER* extensions are initialized with the app ---
    # This ensures that when models and blueprints are loaded,
    # `db` (and `bcrypt` and `jwt`) are already properly bound to the `app`.
    from backend.models import User, Item, Request, TokenBlacklist, Rating 
    from backend.views.auth import auth_bp           
    from backend.views.item import item_bp           
    from backend.views.myrequest import request_bp   
    from backend.views.admin import admin_bp         

    # Configure CORS to allow requests from the specified frontend URL(s).
    # The FRONTEND_URL environment variable on Render should be a comma-separated
    # list of origins if you have multiple (e.g., main Vercel + preview Vercel).
    # This line parses that comma-separated string into a list of allowed origins.
    # --- TEMPORARY DEBUG CORS (REVERT LATER) ---
    allowed_origins = [
        "http://localhost:5173", # Your local frontend development server
        "https://phase4proj-fleemrkt.vercel.app", # Your main Vercel production URL
        "https://phase4proj-fleemrkt-h2vbaatflt-tallams-projects.vercel.app", # The specific preview URL you last saw
        # Add any other Vercel preview URLs you encounter during testing, comma-separated.
    ]
    # --- END TEMPORARY DEBUG CORS ---
    # REVERT TO: allowed_origins = [url.strip() for url in app.config['FRONTEND_URL'].split(',')]

    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

    # Register blueprints with their respective URL prefixes.
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(item_bp, url_prefix='/api')
    app.register_blueprint(request_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # --- JWT Callbacks for token management and user loading ---
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
        return token is not None

    # --- JWT Error Handlers ---
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"msg": "Token signature verification failed or token is malformed."}), 422 

    @jwt.expired_token_loader
    def expired_token_response(callback):
        return jsonify({"msg": "Token has expired"}), 401

    # --- API Routes defined directly in app.py (can be moved to blueprints) ---

    # Logout route for token blacklisting.
    @app.route('/api/logout', methods=['POST'])
    @jwt_required()
    def logout():
        jti = get_jwt()["jti"]
        expires_timestamp = get_jwt()["exp"] 
        expires = datetime.fromtimestamp(expires_timestamp, tz=timezone.utc) 

        blacklisted_token = TokenBlacklist(jti=jti, expires=expires)
        db.session.add(blacklisted_token)
        db.session.commit()
        return jsonify(msg="Successfully logged out and token revoked"), 200

    # Basic root route for health check or welcome message.
    @app.route('/')
    def index():
        return jsonify({"message": "Flea Market API is running!"})

    # Example of a protected route defined directly in app.py
    @app.route('/api/protected', methods=['GET'])
    @jwt_required()
    def protected_route():
        current_user = get_jwt_identity() 
        return jsonify(logged_in_as={"user_id": current_user, "message": "Access granted to protected route!"}), 200

    # Removed direct register/login routes as they should be handled by auth_bp.
    # If auth_bp is not fully set up or missing, you may need to re-add them here
    # or ensure auth_bp is correctly configured and working.

    return app

# --- CRITICAL GUNICORN FIX: Expose the Flask app instance ---
# Gunicorn expects a callable named 'app' at the top level of the module it loads.
# By calling create_app() here and assigning its return value to 'app',
# Gunicorn can find and run your Flask application.
# We explicitly pass the FLASK_ENV to ensure the correct configuration (e.g., 'production') is used.
app = create_app(os.getenv('FLASK_ENV', 'production'))

# Note: The `if __name__ == '__main__':` block below will still run if you execute `python app.py` directly,
# but Gunicorn will use the `app` instance created above.
if __name__ == '__main__':
    app.run(debug=True)
