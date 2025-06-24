# backend/extensions.py
# This file initializes SQLAlchemy and Bcrypt instances.
# It should NOT import app or models directly here.

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
