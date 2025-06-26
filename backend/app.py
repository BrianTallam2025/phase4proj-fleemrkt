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
from backend.extensions import db, bcrypt
migrate = Migrate()
jwt = JWTManager()


# Import models and blueprints after extensions are globally initialized
from backend.models import User, Item, Request, TokenBlacklist, Rating 
from backend.views.auth import auth_bp           
from backend.views.item import item_bp           
from backend.views.myrequest import request_bp   
from backend.views.admin import admin_bp         


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    from backend.config import config_by_name
    app.config.from_object(config_by_name[config_name])

    # Initialize all extensions with the app instance
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db) # This line is crucial for 'flask db' commands


    # --- CRITICAL FIX: Revert CORS to use environment variable from config.py ---
    # This expects FRONTEND_URL in Render's environment variables to be comma-separated.
    allowed_origins = [url.strip() for url in app.config['FRONTEND_URL'].split(',')]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)


    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(item_bp, url_prefix='/api')
    app.register_blueprint(request_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # JWT Callbacks
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        # print(f"DEBUG: user_lookup_callback - JWT Identity: {identity}") # Removed debug print
        return User.query.get(identity)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        # print(f"DEBUG: token_in_blocklist_loader - JTI: {jti}") # Removed debug print
        token = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
        return token is not None

    # JWT Error Handlers
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        # print(f"DEBUG: Unauthorized request: {callback}") # Removed debug print
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        # print(f"DEBUG: Invalid Token Detected - Callback message: {callback}") # Removed debug print
        return jsonify({"msg": "Token signature verification failed or token is malformed."}), 422 

    @jwt.expired_token_loader
    def expired_token_response(callback):
        # print(f"DEBUG: Expired Token Detected: {callback}") # Removed debug print
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

# Global app instance for Gunicorn and Flask CLI
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run(debug=True)
