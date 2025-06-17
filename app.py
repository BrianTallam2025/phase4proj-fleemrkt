from flask import Flask, request, jsonify
from extensions import db, bcrypt  # Changed from direct imports
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

# Initialize extensions
db.init_app(app)  # Now using the db from extensions
bcrypt.init_app(app)  # Now using the bcrypt from extensions
jwt = JWTManager(app)
CORS(app)
migrate = Migrate(app, db)

# Now it's safe to import models
from models import User, Item, Request, Rating

# Import Blueprints
from views.auth import auth
from views.item import item_bp
from views.request import request
from views.admin import admin

# Register Blueprints
app.register_blueprint(auth, url_prefix='/api')
app.register_blueprint(item, url_prefix='/api')
app.register_blueprint(request, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/api')

# --- API Routes (all routes remain the same, just their context changes) ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400
    if User.query.filter_by(username=username).first() or \
       User.query.filter_by(email=email).first():
        return jsonify({"msg": "User with that username or email already exists"}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password, role='user') # Pass hashed password
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User registered successfully", "username": username}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity={'id': user.id, 'username': user.username, 'role': user.role})
    return jsonify(access_token=access_token, user_id=user.id, username=user.username, role=user.role), 200

@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_identity = get_jwt_identity()
    return jsonify(logged_in_as=current_user_identity), 200

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access denied: Admins only"}), 403
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "email": user.email, "role": user.role} for user in users]
    return jsonify(user_list), 200

@app.route('/api/admin/create_admin_user', methods=['POST'])
@jwt_required()
def create_admin_user():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access denied: Admins only"}), 403
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400
    if User.query.filter_by(username=username).first() or \
       User.query.filter_by(email=email).first():
        return jsonify({"msg": "User with that username or email already exists"}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_admin = User(username=username, email=email, password_hash=hashed_password, role='admin') # Pass hashed password
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({"msg": f"Admin user '{username}' created successfully"}), 201

@app.route('/api/items', methods=['POST'])
@jwt_required()
def create_item():
    current_user_identity = get_jwt_identity()
    user_id = current_user_identity['id']
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    category = data.get('category')
    location = data.get('location')
    image_url = data.get('image_url')
    if not title or not description or not category:
        return jsonify({"msg": "Missing title, description, or category"}), 400
    new_item = Item(
        title=title, description=description, category=category,
        location=location, image_url=image_url, user_id=user_id
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"msg": "Item created successfully", "item_id": new_item.id}), 201

@app.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.filter_by(is_available=True).all()
    item_list = []
    for item in items:
        owner_username = User.query.get(item.user_id).username if item.user_id else "Unknown"
        item_list.append({
            "id": item.id, "title": item.title, "description": item.description,
            "category": item.category, "image_url": item.image_url,
            "location": item.location, "is_available": item.is_available,
            "owner_username": owner_username, "created_at": item.created_at.isoformat()
        })
    return jsonify(item_list), 200

@app.route('/api/requests', methods=['POST'])
@jwt_required()
def create_request():
    current_user_identity = get_jwt_identity()
    requester_id = current_user_identity['id']
    data = request.get_json()
    item_id = data.get('item_id')
    if not item_id:
        return jsonify({"msg": "Missing item_id"}), 400
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"msg": "Item not found"}), 404
    if item.user_id == requester_id:
        return jsonify({"msg": "Cannot request your own item"}), 400
    existing_request = Request.query.filter_by(
        item_id=item_id, requester_id=requester_id, status='pending'
    ).first()
    if existing_request:
        return jsonify({"msg": "You already have a pending request for this item"}), 409
    new_request = Request(
        item_id=item_id, requester_id=requester_id, item_owner_id=item.user_id,
        status='pending', requested_at=datetime.utcnow()
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({"msg": "Request sent successfully", "request_id": new_request.id}), 201

@app.route('/api/requests/sent', methods=['GET'])
@jwt_required()
def get_sent_requests():
    current_user_identity = get_jwt_identity()
    requester_id = current_user_identity['id']
    sent_requests = Request.query.filter_by(requester_id=requester_id).all()
    requests_list = []
    for req in sent_requests:
        item = Item.query.get(req.item_id)
        item_owner = User.query.get(req.item_owner_id)
        requests_list.append({
            "request_id": req.id, "item_title": item.title if item else "Unknown Item",
            "item_owner_username": item_owner.username if item_owner else "Unknown Owner",
            "status": req.status, "requested_at": req.requested_at.isoformat()
        })
    return jsonify(requests_list), 200

@app.route('/api/requests/received', methods=['GET'])
@jwt_required()
def get_received_requests():
    current_user_identity = get_jwt_identity()
    item_owner_id = current_user_identity['id']
    user_items = Item.query.filter_by(user_id=item_owner_id).all()
    user_item_ids = [item.id for item in user_items]
    received_requests = Request.query.filter(
        Request.item_id.in_(user_item_ids), Request.item_owner_id == item_owner_id
    ).all()
    requests_list = []
    for req in received_requests:
        item = Item.query.get(req.item_id)
        requester = User.query.get(req.requester_id)
        requests_list.append({
            "request_id": req.id, "item_title": item.title if item else "Unknown Item",
            "requester_username": requester.username if requester else "Unknown Requester",
            "status": req.status, "requested_at": req.requested_at.isoformat()
        })
    return jsonify(requests_list), 200

@app.route('/api/requests/<int:request_id>/status', methods=['PUT'])
@jwt_required()
def update_request_status(request_id):
    current_user_identity = get_jwt_identity()
    current_user_id = current_user_identity['id']
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['accepted', 'rejected']:
        return jsonify({"msg": "Invalid status. Must be 'accepted' or 'rejected'."}), 400
    req = Request.query.get(request_id)
    if not req:
        return jsonify({"msg": "Request not found"}), 404
    if req.item_owner_id != current_user_id:
        return jsonify({"msg": "Unauthorized: You do not own this request"}), 403
    if req.status != 'pending':
        return jsonify({"msg": f"Request status is already '{req.status}'. Cannot change."}), 400
    req.status = new_status
    db.session.commit()
    return jsonify({"msg": f"Request {request_id} status updated to {new_status}"}), 200

@app.route('/api/admin/requests', methods=['GET'])
@jwt_required()
def admin_get_all_requests():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access denied: Admins only"}), 403
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

@app.route('/api/admin/requests/<int:request_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_request(request_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access denied: Admins only"}), 403
    req = Request.query.get(request_id)
    if not req:
        return jsonify({"msg": "Request not found"}), 404
    db.session.delete(req)
    db.session.commit()
    return jsonify({"msg": f"Request {request_id} deleted successfully"}), 200

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
        # This part ensures initial users are created AFTER the database schema
        # has been set up via migrations (run 'flask db upgrade' separately).
        # We put it here for development convenience, but in production,
        # seeding might be a separate script or part of deployment.
        
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin', 
                email='admin@example.com', 
                # Hashing password directly in this block for initial users
                password_hash=bcrypt.generate_password_hash('adminpassword').decode('utf-8'), 
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
                # Hashing password directly in this block for initial users
                password_hash=bcrypt.generate_password_hash('testpassword').decode('utf-8'), 
                role='user'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: username='testuser', password='testpassword'")
        else:
            print("Test user already exists.")

    app.run(debug=True, port=5000)
