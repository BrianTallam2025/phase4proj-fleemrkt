# backend/app.py
# CHANGES:
# - Corrected Blueprint import name for auth_bp to explicitly match 'auth_bp'.

from flask import Flask, request, jsonify
from backend.extensions import db, bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object('backend.config.Config')

# Initialize extensions with the app instance
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
CORS(app)
migrate = Migrate(app, db)

# --- JWT Blacklist Configuration ---
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    from backend.models import TokenBlacklist 
    token = db.session.query(TokenBlacklist.id).filter_by(jti=jti).scalar()
    return token is not None

# Import models AFTER db, bcrypt, and app are fully initialized
from backend.models import User, Item, Request, Rating, TokenBlacklist

# --- Blueprint Imports ---
# THIS IS THE CRITICAL CHANGE FOR AUTH: Ensure it's 'auth_bp'
from backend.views.auth import auth_bp      # <--- THIS MUST BE 'auth_bp'
from backend.views.item import item_bp           
from backend.views.myrequest import request_bp   
from backend.views.admin import admin_bp         

# Register Blueprints with the main app
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(item_bp, url_prefix='/api')
app.register_blueprint(request_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# --- NEW: Logout route to blacklist tokens ---
@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    expires = datetime.fromtimestamp(get_jwt()["exp"], tz=timezone.utc)
    blacklisted_token = TokenBlacklist(jti=jti, expires=expires)
    db.session.add(blacklisted_token)
    db.session.commit()
    return jsonify({"msg": "Successfully logged out"}), 200

# --- Error handling ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({"msg": "Resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return jsonify({"msg": "Internal server error"}), 500

# Main block for running the Flask app.
if __name__ == '__main__':
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin', 
                email='admin@example.com', 
                password='adminpassword',
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username='admin', password='adminpassword'")
        
        if not User.query.filter_by(username='testuser').first():
            test_user = User(
                username='testuser', 
                email='test@example.com', 
                password='testpassword',
                role='user'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: username='testuser', password='testpassword'")

    app.run(debug=True, port=5000)
