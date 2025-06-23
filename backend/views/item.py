# backend/views/item.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db # Import from extensions
from models import Item, User # Import models
from datetime import datetime

# Define the Blueprint for item management
item_bp = Blueprint('item', __name__) # <--- Blueprint variable named 'item_bp'

@item_bp.route('/items', methods=['POST'])
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
        title=title,
        description=description,
        category=category,
        location=location,
        image_url=image_url,
        user_id=user_id
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"msg": "Item created successfully", "item_id": new_item.id}), 201

@item_bp.route('/items', methods=['GET'])
def get_items():
    items = Item.query.filter_by(is_available=True).all()
    item_list = []
    for item in items:
        owner_username = User.query.get(item.user_id).username if item.user_id else "Unknown"
        item_list.append({
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "category": item.category,
            "image_url": item.image_url,
            "location": item.location,
            "is_available": item.is_available,
            "owner_username": owner_username,
            "created_at": item.created_at.isoformat()
        })
    return jsonify(item_list), 200
