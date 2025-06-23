# backend/views/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db, bcrypt # Import from extensions
from models import User # Import User model

# Define the Blueprint for authentication
auth_bp = Blueprint('auth', __name__) # <--- Blueprint variable named 'auth_bp'

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password') # This is the raw password

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    if User.query.filter_by(username=username).first() or \
       User.query.filter_by(email=email).first():
        return jsonify({"msg": "User with that username or email already exists"}), 409

    # User model's __init__ now handles hashing using its internal bcrypt
    new_user = User(username=username, email=email, password=password, role='user') # Pass RAW password
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully", "username": username}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity={'id': user.id, 'username': user.username, 'role': user.role})
    return jsonify(access_token=access_token, user_id=user.id, username=user.username, role=user.role), 200

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_identity = get_jwt_identity()
    return jsonify(logged_in_as=current_user_identity), 200
