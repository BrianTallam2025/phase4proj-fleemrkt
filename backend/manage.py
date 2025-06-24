# backend/manage.py
# This script is used to run Flask-Migrate commands and other custom CLI commands.

import os
from flask.cli import FlaskGroup
from backend.app import app, db # <--- Changed: Import from backend.app
from backend.models import User, Item, Request, Rating, TokenBlacklist # <--- Changed: Import from backend.models
from datetime import datetime
# Bcrypt is used in User.__init__, so no direct import needed here if User model is consistent.

cli = FlaskGroup(app)

@cli.command("create_initial_users")
def create_initial_users():
    """
    Creates the initial admin and test user if they don't exist.
    Run this AFTER `flask db upgrade`.
    """
    with app.app_context(): # Ensure we are in the Flask application context
        
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin', 
                email='admin@example.com', 
                password='adminpassword', # Pass RAW password, User.__init__ handles hashing
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
                password='testpassword', # Pass RAW password, User.__init__ handles hashing
                role='user'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: username='testuser', password='testpassword'")
        else:
            print("Test user already exists.")

if __name__ == '__main__':
    cli()
