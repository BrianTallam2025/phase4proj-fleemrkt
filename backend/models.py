# backend/models.py
# This file defines your database models using SQLAlchemy.

from datetime import datetime
from backend.extensions import db, bcrypt # Correctly importing from extensions

# User Model: Represents a user in the system (regular or admin).
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False) 
    
    # Relationships for user-generated content
    items = db.relationship('Item', backref='owner', lazy=True)
    sent_requests = db.relationship('Request', foreign_keys='Request.requester_id', backref='requester', lazy=True)
    received_requests = db.relationship('Request', foreign_keys='Request.item_owner_id', backref='item_owner', lazy=True)
    ratings_given = db.relationship('Rating', foreign_keys='Rating.rater_id', backref='rater', lazy=True)
    ratings_received = db.relationship('Rating', foreign_keys='Rating.rated_user_id', backref='rated_user', lazy=True)


    def __init__(self, username, email, password, role='user'): # Expects RAW password, hashes internally
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

# Item Model: Represents a resource/item listed by a user.
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=True) 
    location = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_available = db.Column(db.Boolean, default=True)
    
    # Foreign key to link item to its owner (User)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship for item requests
    requests = db.relationship('Request', backref='item', lazy=True)

    def __repr__(self):
        return f"Item('{self.title}', '{self.category}', '{self.owner.username}')"

# Request Model: Represents a request from one user to another for an item.
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Owner of the item
    status = db.Column(db.String(20), default='pending', nullable=False) # e.g., 'pending', 'accepted', 'rejected', 'completed'
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Request('{self.requester.username}' to '{self.item_owner.username}' for '{self.item.title}', Status: '{self.status}')"

# Rating Model: For user-to-user ratings.
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False) # e.g., 1 to 5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Rating by '{self.rater.username}' for '{self.rated_user.username}': {self.score}"

# NEW: TokenBlacklist Model for JWT revocation
class TokenBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True) # JWT ID
    expires = db.Column(db.DateTime, nullable=False) # When the token naturally expires

    def __repr__(self):
        return f"TokenBlacklist(jti='{self.jti}', expires='{self.expires}')"
