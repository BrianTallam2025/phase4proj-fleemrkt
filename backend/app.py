from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.extensions import db, migrate, bcrypt
from backend.config import Config
import logging
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure database path for migrations
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'site.db')}"
    
    # Initialize extensions with proper paths
    db.init_app(app)
    migrate.init_app(app, db, directory=os.path.join(os.path.dirname(__file__), '..', 'migrations'))
    jwt = JWTManager(app)
    bcrypt.init_app(app)

    # Configure CORS (keep your existing CORS configuration)
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://phase4proj-fleemrkt.vercel.app",
                "http://localhost:5173"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Authorization", "X-CSRF-TOKEN"],
            "max_age": 86400
        }
    })

    # Register blueprints
    from backend.views.auth import auth_bp
    from backend.views.item import item_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(item_bp, url_prefix='/api')

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    return app

app = create_app()

if __name__ == '__main__':
    app.run()