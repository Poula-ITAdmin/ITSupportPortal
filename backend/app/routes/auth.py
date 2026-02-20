"""
Authentication routes
Handles login, token refresh, logout, and user registration
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging
from app.models import User, db
from app.services.ldap_service import ldap_service
from app.utils.decorators import handle_errors

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
@handle_errors
def login():
    """
    User login endpoint
    Supports both LDAP and local authentication
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data['username']
    password = data['password']
    
    # Try LDAP authentication first
    success, ldap_user_data = ldap_service.authenticate_user(username, password)
    
    if success:
        # Sync user to database
        user = ldap_service.sync_user(ldap_user_data)
    else:
        # Try local database authentication
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.password_hash or not user.is_ldap_user == False:
            logger.warning(f"Failed login attempt: {username}")
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'User account is disabled'}), 403
        
        # Verify password (implement bcrypt verification)
        import bcrypt
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            logger.warning(f"Failed login attempt: {username}")
            return jsonify({'error': 'Invalid username or password'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'username': user.username, 'role': user.role.value}
    )
    refresh_token = create_refresh_token(identity=user.id)
    
    logger.info(f"User logged in: {username}")
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'department': user.department,
            'job_title': user.job_title,
            'role': user.role.value,
            'phone': user.phone,
            'is_ldap_user': user.is_ldap_user,
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@handle_errors
def refresh():
    """Refresh access token using refresh token"""
    identity = get_jwt_identity()
    user = User.query.get(identity)
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'username': user.username, 'role': user.role.value}
    )
    
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@handle_errors
def logout():
    """User logout endpoint"""
    # In a real app, you'd add the token to a blacklist
    logger.info(f"User logged out: {get_jwt_identity()}")
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/register', methods=['POST'])
@handle_errors
def register():
    """
    Local user registration
    For non-LDAP users
    """
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Hash password
    import bcrypt
    password_hash = bcrypt.hashpw(
        data['password'].encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=password_hash,
        first_name=data['first_name'],
        last_name=data['last_name'],
        department=data.get('department'),
        job_title=data.get('job_title'),
        phone=data.get('phone'),
        is_ldap_user=False
    )
    
    db.session.add(user)
    db.session.commit()
    
    logger.info(f"New user registered: {user.username}")
    
    return jsonify({
        'message': 'User registered successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    }), 201


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@handle_errors
def get_current_user():
    """Get current authenticated user info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'department': user.department,
        'job_title': user.job_title,
        'role': user.role.value,
        'phone': user.phone,
        'is_ldap_user': user.is_ldap_user,
        'is_active': user.is_active,
        'ad_groups': user.ad_groups,
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@handle_errors
def change_password():
    """Change user password (local users only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.is_ldap_user:
        return jsonify({'error': 'LDAP users cannot change password here'}), 400
    
    data = request.get_json()
    
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing password fields'}), 400
    
    # Verify old password
    import bcrypt
    if not bcrypt.checkpw(data['old_password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid current password'}), 401
    
    # Hash and save new password
    password_hash = bcrypt.hashpw(
        data['new_password'].encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    user.password_hash = password_hash
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    logger.info(f"Password changed for user: {user.username}")
    
    return jsonify({'message': 'Password changed successfully'}), 200
