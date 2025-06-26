# backend/app.py
# This is the main application file for the Flea Market backend.
# It initializes the Flask app, database, migrations, JWT, CORS,
# and registers all the API blueprints.

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate # Make sure Migrate is imported
# Consolidated Flask-JWT-Extended imports for all used components
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
from backend.extensions import db, bcrypt # Import db and bcrypt here
migrate = Migrate() # Make sure this is globally initialized
jwt = JWTManager()


# Import models after extensions are globally initialized (but before app.init_app)
from backend.models import User, Item, Request, TokenBlacklist, Rating 

# Import blueprints with their fully qualified names
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

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    from backend.config import config_by_name
    app.config.from_object(config_by_name[config_name])

    # --- CRITICAL FIX: Initialize all extensions WITH THE APP instance ---
    # This must happen before models or blueprints that use 'db' are registered,
    # and it ensures Flask-Migrate's 'db' commands are available.
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db) # <--- THIS LINE IS CRUCIAL AND WAS MISSING IN THE LAST VERSION!


    # --- TEMPORARY DEBUG CORS (REVERT LATER) ---
    allowed_origins = [
        "http://localhost:5173",
        "https://phase4proj-fleemrkt.vercel.app",
        "https://phase4proj-fleemrkt-h2vbaatflt-tallams-projects.vercel.app",
    ]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)
    # --- END TEMPORARY DEBUG CORS ---

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(item_bp, url_prefix='/api')
    app.register_blueprint(request_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # JWT Callbacks
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
        return token is not None

    # JWT Error Handlers
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"msg": "Token signature verification failed or token is malformed."}), 422 

    @jwt.expired_token_loader
    def expired_token_response(callback):
        return jsonify({"msg": "Token has expired"}), 401

    # Logout route
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

    # Basic root route
    @app.route('/')
    def index():
        return jsonify({"message": "Flea Market API is running!"})

    # Example protected route
    @app.route('/api/protected', methods=['GET'])
    @jwt_required()
    def protected_route():
        current_user = get_jwt_identity() 
        return jsonify(logged_in_as={"user_id": current_user, "message": "Access granted to protected route!"}), 200

    return app

# --- CRITICAL GUNICORN FIX: Expose the Flask app instance ---
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run(debug=True)
