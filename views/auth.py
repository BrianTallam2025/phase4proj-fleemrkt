from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, bcrypt # Import db and bcrypt from the main app instance
from models import User # Import the User model

# Create a Blueprint for user authentication
user_auth_bp = Blueprint('user_auth', __name__)

@user_auth_bp.route('/register', methods=['POST'])
def register():
    """
    Handles user registration.
    Expects JSON with 'username', 'email', and 'password'.
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    # Check if user already exists
    if User.query.filter_by(username=username).first() or \
       User.query.filter_by(email=email).first():
        return jsonify({"msg": "User with that username or email already exists"}), 409

    # Create new user (default role is 'user')
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully", "username": username}), 201

@user_auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handles user login.
    Expects JSON with 'username' and 'password'.
    Returns an access token upon successful login.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Create access token
    access_token = create_access_token(identity={'id': user.id, 'username': user.username, 'role': user.role})
    return jsonify(access_token=access_token, user_id=user.id, username=user.username, role=user.role), 200

@user_auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """
    A protected route that requires a valid JWT.
    Returns the identity of the current user.
    """
    current_user_identity = get_jwt_identity()
    return jsonify(logged_in_as=current_user_identity), 200
