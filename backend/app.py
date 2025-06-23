
from flask import Flask, request, jsonify # Keep flask.request here for API route handling
from extensions import db, bcrypt # Import db and bcrypt from extensions.py
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions with the app instance
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
CORS(app)
migrate = Migrate(app, db)

# Import models AFTER db, bcrypt, and app are fully initialized
# This order is crucial.
# models.py itself imports db and bcrypt from extensions, so no circular import here.
from models import User, Item, Request, Rating

# --- CORRECTED BLUEPRINT IMPORTS ---
# Import the blueprint OBJECTS from their respective files
# Ensure these match the actual blueprint variable names defined in each views file.
from views.auth import auth_bp           # Assuming auth.py has 'auth_bp = Blueprint(...)'
from views.item import item_bp           # Assuming item.py has 'item_bp = Blueprint(...)'
from views.myrequest import request_bp   # <--- RENAMED to request_bp to avoid collision with flask.request
from views.admin import admin_bp         # Assuming admin.py has 'admin_bp = Blueprint(...)'

# Register Blueprints with the main app
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(item_bp, url_prefix='/api')
app.register_blueprint(request_bp, url_prefix='/api') # <--- Use request_bp here
app.register_blueprint(admin_bp, url_prefix='/api')


# --- REMOVE ALL DIRECT @app.route(...) DEFINITIONS FROM HERE ---
# All your API routes (register, login, protected, items, requests, admin)
# should now live WITHIN their respective Blueprint files.
# If you have duplicate route definitions here, they will conflict.
# The code below this comment should ONLY contain error handlers and the main run block.


# --- Error handling (these remain in app.py as they are global) ---
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
        # This part ensures initial users are created AFTER the database schema
        # has been set up via migrations (run 'flask db upgrade' separately).
        # We put it here for development convenience, but in production,
        # seeding might be a separate script or part of deployment.
        
        # models.py's User.__init__ now handles hashing, so pass raw password
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin', 
                email='admin@example.com', 
                password='adminpassword', # Pass RAW password, models.py handles hashing
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username='admin', password='adminpassword'")
        else:
            print("Admin user already exists.")
        
        if not User.query.filter_by(username='testuser').first():
            test_user = User(
                username='testuser', 
                email='test@example.com', 
                password='testpassword', # Pass RAW password, models.py handles hashing
                role='user'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: username='testuser', password='testpassword'")
        else:
            print("Test user already exists.")

    app.run(debug=True, port=5000)
