# backend/views/myrequest.py
# This file handles request-related routes for users (creating, viewing sent/received, updating status).

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db # <--- Changed: Correct import for db
from backend.models import Item, User, Request # <--- Changed: Correct import for Item, User, Request
from datetime import datetime

request_bp = Blueprint('request', __name__)

# Route to create a new request for an item
@request_bp.route('/requests', methods=['POST'])
@jwt_required()
def create_request():
    current_user_identity = get_jwt_identity()
    requester_id = current_user_identity['id']

    data = request.get_json()
    item_id = data.get('item_id')

    if not item_id:
        return jsonify({"msg": "Item ID is required"}), 400

    item = Item.query.get(item_id)
    if not item:
        return jsonify({"msg": "Item not found"}), 404
    
    # Prevent requesting own item
    if item.user_id == requester_id:
        return jsonify({"msg": "Cannot request your own item"}), 400

    # Check for existing pending request by the same requester for the same item
    existing_request = Request.query.filter_by(
        item_id=item_id,
        requester_id=requester_id,
        status='pending'
    ).first()

    if existing_request:
        return jsonify({"msg": "You already have a pending request for this item"}), 409

    new_request = Request(
        item_id=item_id,
        requester_id=requester_id,
        item_owner_id=item.user_id, # Set the owner of the item as the recipient of the request
        status='pending'
    )
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"msg": "Request sent successfully", "request_id": new_request.id}), 201

# Route to get all requests sent by the current user
@request_bp.route('/requests/sent', methods=['GET'])
@jwt_required()
def get_sent_requests():
    current_user_identity = get_jwt_identity()
    requester_id = current_user_identity['id']

    sent_requests = Request.query.filter_by(requester_id=requester_id).all()
    
    output = []
    for req in sent_requests:
        item_title = req.item.title if req.item else "Unknown Item"
        item_owner_username = req.item_owner.username if req.item_owner else "Unknown Owner"
        output.append({
            "request_id": req.id,
            "item_id": req.item_id,
            "item_title": item_title,
            "requester_id": req.requester_id,
            "item_owner_id": req.item_owner_id,
            "item_owner_username": item_owner_username,
            "status": req.status,
            "requested_at": req.requested_at.isoformat()
        })
    return jsonify(output), 200

# Route to get all requests received by the current user (for their items)
@request_bp.route('/requests/received', methods=['GET'])
@jwt_required()
def get_received_requests():
    current_user_identity = get_jwt_identity()
    item_owner_id = current_user_identity['id']

    # Filter requests where the current user is the item owner
    received_requests = Request.query.filter_by(item_owner_id=item_owner_id).all()
    
    output = []
    for req in received_requests:
        item_title = req.item.title if req.item else "Unknown Item"
        requester_username = req.requester.username if req.requester else "Unknown Requester"
        output.append({
            "request_id": req.id,
            "item_id": req.item_id,
            "item_title": item_title,
            "requester_id": req.requester_id,
            "requester_username": requester_username,
            "item_owner_id": req.item_owner_id,
            "status": req.status,
            "requested_at": req.requested_at.isoformat()
        })
    return jsonify(output), 200

# Route to update the status of a request (by the item owner)
@request_bp.route('/requests/<int:request_id>/status', methods=['PUT'])
@jwt_required()
def update_request_status(request_id):
    current_user_identity = get_jwt_identity()
    user_id = current_user_identity['id']

    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['accepted', 'rejected', 'completed']:
        return jsonify({"msg": "Invalid status provided"}), 400

    req = Request.query.get(request_id)
    if not req:
        return jsonify({"msg": "Request not found"}), 404

    # Ensure only the item owner can update the status
    if req.item_owner_id != user_id:
        return jsonify({"msg": "You are not authorized to update this request"}), 403

    req.status = new_status
    db.session.commit()



    return jsonify({"msg": f"Request {request_id} status updated to {new_status}"}), 200
