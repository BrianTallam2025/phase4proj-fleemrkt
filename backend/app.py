# backend/app.py
# This is the main application file for the Flea Market backend.
# It initializes the Flask app, database, migrations, JWT, CORS,
# and registers all the API blueprints.

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
# This ensures that variables like DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY,
# and FRONTEND_URL are available to the application.
load_dotenv()

# Initialize SQLAlchemy, Migrate, and JWTManager without binding them to an app yet.
# This pattern is good for creating an application factory.
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager() # Initialize JWTManager globally as well

# Import models after db is initialized to prevent circular imports if models
# reference db or other extensions.
# Ensure all models (User, Item, Request, TokenBlacklist, Rating) are imported.
from backend.models import User, Item, Request, TokenBlacklist, Rating 

# Import blueprints with their fully qualified names
# Assuming your blueprint files (auth.py, item.py, etc.) are inside backend/views/
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

    # Import configuration settings from backend.config module
    from backend.config import config_by_name
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with the Flask app instance.
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app) # Bind JWTManager to the app

    # Configure CORS to allow requests from the specified frontend URL(s).
    # The FRONTEND_URL environment variable on Render should be a comma-separated
    # list of origins if you have multiple (e.g., main Vercel + preview Vercel).
    # This line parses that comma-separated string into a list of allowed origins.
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
        # Query the TokenBlacklist model (correctly spelled) to check for the JTI.
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
        # Note: Callback argument is often the error message itself
        return jsonify({"msg": "Token signature verification failed or token is malformed."}), 422 # 422 Unprocessable Entity often used for malformed data

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
        current_user = get_jwt_identity() # Get user identity from the token
        return jsonify(logged_in_as={"user_id": current_user, "message": "Access granted to protected route!"}), 200

    # Example login and register routes if not fully moved to auth blueprint yet
    # You might remove these if auth_bp handles them exclusively.
    # @app.route('/api/register', methods=['POST'])
    # def register_user_direct():
    #     data = request.get_json()
    #     username = data.get('username')
    #     email = data.get('email')
    #     password = data.get('password')
    #     role = data.get('role', 'user')

    #     if not username or not email or not password:
    #         return jsonify({"msg": "Missing username, email, or password"}), 400
    #     if User.query.filter_by(username=username).first():
    #         return jsonify({"msg": "Username already exists"}), 409
    #     if User.query.filter_by(email=email).first():
    #         return jsonify({"msg": "Email already exists"}), 409

    #     new_user = User(username=username, email=email, password=password, role=role)
    #     db.session.add(new_user)
    #     db.session.commit()
    #     return jsonify({"msg": "User created successfully", "user_id": new_user.id}), 201

    # @app.route('/api/login', methods=['POST'])
    # def login_user_direct():
    #     data = request.get_json()
    #     username = data.get('username')
    #     password = data.get('password')
    #     user = User.query.filter_by(username=username).first()

    #     if user and user.check_password(password):
    #         access_token = create_access_token(identity=user.id) # create_access_token imported above
    #         return jsonify(access_token=access_token, user_id=user.id, username=user.username, role=user.role), 200
    #     else:
    #         return jsonify({"msg": "Bad username or password"}), 401

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
    # This block is primarily for local Flask development server.
    # It allows running `python app.py` instead of `flask run` or gunicorn.
    # It will run on http://127.0.0.1:5000/ by default.
    app.run(debug=True)
