"""
Flask Application Factory
Creates and configures the Flask app with all dependencies
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from dotenv import load_dotenv

from config import get_config
from app.models import db

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory"""
    
    # Load config
    config = get_config()
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    jwt = JWTManager(app)
    socketio = SocketIO(
        app,
        cors_allowed_origins=app.config['CORS_ORIGINS'],
        message_queue=app.config['SOCKETIO_MESSAGE_QUEUE']
    )
    
    # Register error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Missing token'}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({'error': 'Token expired'}), 401
    
    # Create database context
    with app.app_context():
        # Create tables
        db.create_all()
        logger.info("Database initialized")
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.tickets import tickets_bp
    from app.routes.users import users_bp
    from app.routes.chat import chat_bp
    from app.routes.tasks import tasks_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(tasks_bp)
    
    # Register WebSocket events
    from app.websocket.events import register_websocket_events
    register_websocket_events(socketio)
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'version': '2.0.0'}), 200
    
    logger.info("Flask app created successfully")
    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
