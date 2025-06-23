
import os
from flask.cli import FlaskGroup
from app import app, db # Import your app and db instances from app.py
from models import User, Item, Request, Rating # Import all your models from models.py
from datetime import datetime
from flask_bcrypt import Bcrypt # Import Bcrypt to hash passwords for initial users

# Create a FlaskGroup instance to enable Flask CLI commands
# This tells Flask-CLI to use 'app' as the Flask application.
cli = FlaskGroup(app)

# Custom command to create initial users (admin and testuser)
@cli.command("create_initial_users")
def create_initial_users():
    """
    Creates the initial admin and test user if they don't exist.
    Run this AFTER `flask db upgrade`.
    """
    with app.app_context(): # Ensure we are in the Flask application context
        # Bcrypt is initialized with the app instance, so we need to access it from app.
        # This prevents circular imports if Bcrypt was initialized in models.py
        app_bcrypt = Bcrypt(app) 

        # Check for and create admin user
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin', 
                email='admin@example.com', 
                password_hash=app_bcrypt.generate_password_hash('adminpassword').decode('utf-8'), 
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username='admin', password='adminpassword'")
        else:
            print("Admin user already exists.")
        
        # Check for and create test user
        if not User.query.filter_by(username='testuser').first():
            test_user = User(
                username='testuser', 
                email='test@example.com', 
                password_hash=app_bcrypt.generate_password_hash('testpassword').decode('utf-8'), 
                role='user'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: username='testuser', password='testpassword'")
        else:
            print("Test user already exists.")

# This is the standard entry point for Flask-CLI commands
if __name__ == '__main__':
    cli()