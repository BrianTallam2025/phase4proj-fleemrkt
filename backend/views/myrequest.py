# backend/views/myrequest.py
from flask import Blueprint, request, jsonify # Keep flask.request here for API route handling
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db # Import from extensions
from models import Item, User, Request # Import models
from datetime import datetime

# Define the Blueprint for request management
request_bp = Blueprint('my_request', __name__) # <--- Blueprint variable named 'request_bp'

@request_bp.route('/requests', methods=['POST'])
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
        item_id=item_id,
        requester_id=requester_id,
        status='pending'
    ).first()

    if existing_request:
        return jsonify({"msg": "You already have a pending request for this item"}), 409

    new_request = Request(
        item_id=item_id,
        requester_id=requester_id,
        item_owner_id=item.user_id,
        status='pending',
        requested_at=datetime.utcnow()
    )
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"msg": "Request sent successfully", "request_id": new_request.id}), 201


@request_bp.route('/requests/sent', methods=['GET'])
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
            "request_id": req.id,
            "item_title": item.title if item else "Unknown Item",
            "item_owner_username": item_owner.username if item_owner else "Unknown Owner",
            "status": req.status,
            "requested_at": req.requested_at.isoformat()
        })
    return jsonify(requests_list), 200


@request_bp.route('/requests/received', methods=['GET'])
@jwt_required()
def get_received_requests():
    current_user_identity = get_jwt_identity()
    item_owner_id = current_user_identity['id']

    user_items = Item.query.filter_by(user_id=item_owner_id).all()
    user_item_ids = [item.id for item in user_items]

    received_requests = Request.query.filter(
        Request.item_id.in_(user_item_ids),
        Request.item_owner_id == item_owner_id
    ).all()
    
    requests_list = []
    for req in received_requests:
        item = Item.query.get(req.item_id)
        requester = User.query.get(req.requester_id)
        requests_list.append({
            "request_id": req.id,
            "item_title": item.title if item else "Unknown Item",
            "requester_username": requester.username if requester else "Unknown Requester",
            "status": req.status,
            "requested_at": req.requested_at.isoformat()
        })
    return jsonify(requests_list), 200

@request_bp.route('/requests/<int:request_id>/status', methods=['PUT'])
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
