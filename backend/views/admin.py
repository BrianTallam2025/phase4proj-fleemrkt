# backend/views/admin.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, bcrypt # Import from extensions
from models import User, Item, Request # Import models needed for admin tasks
import functools # Needed for @functools.wraps

# Define the Blueprint for admin management
admin_bp = Blueprint('admin', __name__) # <--- Blueprint variable named 'admin_bp'

# Helper function to check if current user is admin
def admin_required(f):
    @functools.wraps(f) # CRITICAL: preserves original function name for Flask
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({"msg": "Access denied: Admins only"}), 403
        return f(*args, **kwargs)
    return wrapper

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required # Use our custom decorator
def get_all_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "email": user.email, "role": user.role} for user in users]
    return jsonify(user_list), 200

@admin_bp.route('/admin/create_admin_user', methods=['POST'])
@admin_required # Use our custom decorator
def create_admin_user():
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
    new_admin = User(username=username, email=email, password=password, role='admin') # Pass RAW password
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({"msg": f"Admin user '{username}' created successfully"}), 201

@admin_bp.route('/admin/requests', methods=['GET'])
@admin_required # Use our custom decorator
def admin_get_all_requests():
    all_requests = Request.query.all()
    requests_data = []
    for req in all_requests:
        item = Item.query.get(req.item_id)
        requester = User.query.get(req.requester_id)
        owner = User.query.get(req.item_owner_id)
        requests_data.append({
            "request_id": req.id, "item_title": item.title if item else "N/A",
            "requester_username": requester.username if requester else "N/A",
            "item_owner_username": owner.username if owner else "N/A",
            "status": req.status, "requested_at": req.requested_at.isoformat()
        })
    return jsonify(requests_data), 200

@admin_bp.route('/admin/requests/<int:request_id>', methods=['DELETE'])
@admin_required # Use our custom decorator
def admin_delete_request(request_id):
    req = Request.query.get(request_id)
    if not req:
        return jsonify({"msg": "Request not found"}), 404
    
    db.session.delete(req)
    db.session.commit()
    return jsonify({"msg": f"Request {request_id} deleted successfully"}), 200
