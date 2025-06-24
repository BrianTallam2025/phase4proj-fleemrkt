# backend/views/admin.py
# This file handles administration-related routes (e.g., managing users, all requests).

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, bcrypt # <--- Changed: Correct import for db, bcrypt
from backend.models import User, Item, Request, TokenBlacklist # <--- Changed: Correct import for models
from sqlalchemy import desc # For sorting if needed, no change to import path for this

admin_bp = Blueprint('admin', __name__)

# Helper function to check if the current user is an admin
def admin_required():
    current_user_identity = get_jwt_identity()
    user_id = current_user_identity['id']
    user = User.query.get(user_id)
    if user and user.role == 'admin':
        return True
    return False

# Route to get all users (Admin only)
@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
    
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        })
    return jsonify(output), 200

# Route to create a new admin user (Admin only)
@admin_bp.route('/admin/create_admin_user', methods=['POST'])
@jwt_required()
def create_admin_user():
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    if User.query.filter_by(username=username).first() or \
       User.query.filter_by(email=email).first():
        return jsonify({"msg": "User with that username or email already exists"}), 409

    # User model's __init__ method now handles hashing the password
    new_admin = User(username=username, email=email, password=password, role='admin')
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({"msg": "Admin user created successfully", "username": username}), 201

# Route to get all requests (Admin only)
@admin_bp.route('/admin/requests', methods=['GET'])
@jwt_required()
def admin_get_all_requests():
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
    
    all_requests = Request.query.all()
    output = []
    for req in all_requests:
        item_title = req.item.title if req.item else "Unknown Item"
        requester_username = req.requester.username if req.requester else "Unknown Requester"
        item_owner_username = req.item_owner.username if req.item_owner else "Unknown Owner"

        output.append({
            "request_id": req.id,
            "item_id": req.item_id,
            "item_title": item_title,
            "requester_id": req.requester_id,
            "requester_username": requester_username,
            "item_owner_id": req.item_owner_id,
            "item_owner_username": item_owner_username,
            "status": req.status,
            "requested_at": req.requested_at.isoformat()
        })
    return jsonify(output), 200

# Route to delete any request (Admin only)
@admin_bp.route('/admin/requests/<int:request_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_request(request_id):
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
    
    req = Request.query.get(request_id)
    if not req:
        return jsonify({"msg": "Request not found"}), 404

    db.session.delete(req)
    db.session.commit()
    return jsonify({"msg": f"Request {request_id} deleted successfully"}), 200

# Other admin routes can be added here
