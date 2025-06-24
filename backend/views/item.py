# backend/views/item.py
# Corrected imports to use absolute paths within the 'backend' package.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db # <--- Changed: Correct import for db
from backend.models import Item, User # <--- Changed: Correct import for Item, User

item_bp = Blueprint('item', __name__)

@item_bp.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    current_user_identity = get_jwt_identity()
    user_id = current_user_identity['id']

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    category = data.get('category')
    image_url = data.get('image_url')
    location = data.get('location')

    if not title or not description or not category:
        return jsonify({"msg": "Missing required item fields"}), 400

    new_item = Item(
        title=title,
        description=description,
        category=category,
        image_url=image_url,
        location=location,
        user_id=user_id
    )
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"msg": "Item created successfully", "item_id": new_item.id}), 201

@item_bp.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    output = []
    for item in items:
        owner = User.query.get(item.user_id) # Get the owner to display username
        output.append({
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "category": item.category,
            "image_url": item.image_url,
            "location": item.location,
            "created_at": item.created_at.isoformat(),
            "is_available": item.is_available,
            "user_id": item.user_id,
            "owner_username": owner.username if owner else "Unknown"
        })
    return jsonify(output), 200

# Add other item-related routes here (e.g., PUT/PATCH for update, DELETE)
