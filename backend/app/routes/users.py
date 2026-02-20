"""
User management routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.models import User, UserRole, db
from app.utils.decorators import handle_errors, require_role

logger = logging.getLogger(__name__)
users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('', methods=['GET'])
@jwt_required()
@require_role('it_level1', 'it_level2', 'admin', 'manager')
@handle_errors
def list_users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    search = request.args.get('search')
    department = request.args.get('department')
    role = request.args.get('role')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%'))
        )
    
    if department:
        query = query.filter_by(department=department)
    
    if role:
        try:
            role_enum = UserRole[role.upper()]
            query = query.filter_by(role=role_enum)
        except KeyError:
            pass
    
    total = query.count()
    users = query.paginate(page=page, per_page=limit)
    
    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit,
        'users': [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'department': u.department,
                'job_title': u.job_title,
                'role': u.role.value,
                'is_active': u.is_active,
                'is_ldap_user': u.is_ldap_user,
                'created_at': u.created_at.isoformat(),
                'last_login': u.last_login.isoformat() if u.last_login else None
            }
            for u in users.items
        ]
    }), 200


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_user(user_id):
    """Get user details"""
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
        'phone': user.phone,
        'role': user.role.value,
        'is_active': user.is_active,
        'is_ldap_user': user.is_ldap_user,
        'ad_groups': user.ad_groups,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    }), 200


@users_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
@handle_errors
def update_user(user_id):
    """Update user"""
    data = request.get_json()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update allowed fields
    allowed_fields = ['department', 'job_title', 'phone', 'role', 'is_active']
    
    for field in allowed_fields:
        if field in data:
            if field == 'role':
                try:
                    user.role = UserRole[data[field].upper()]
                except KeyError:
                    return jsonify({'error': 'Invalid role'}), 400
            else:
                setattr(user, field, data[field])
    
    db.session.commit()
    logger.info(f"User updated: {user.username}")
    
    return jsonify({'message': 'User updated', 'user_id': user.id}), 200


@users_bp.route('/<user_id>/disable', methods=['POST'])
@jwt_required()
@require_role('admin')
@handle_errors
def disable_user(user_id):
    """Disable user account"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.is_active = False
    db.session.commit()
    logger.info(f"User disabled: {user.username}")
    
    return jsonify({'message': 'User disabled'}), 200


@users_bp.route('/<user_id>/enable', methods=['POST'])
@jwt_required()
@require_role('admin')
@handle_errors
def enable_user(user_id):
    """Enable user account"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.is_active = True
    db.session.commit()
    logger.info(f"User enabled: {user.username}")
    
    return jsonify({'message': 'User enabled'}), 200


@users_bp.route('/sync-ldap', methods=['POST'])
@jwt_required()
@require_role('admin')
@handle_errors
def sync_ldap():
    """Sync users from LDAP"""
    from app.services.ldap_service import ldap_service
    
    created, updated = ldap_service.sync_all_users()
    
    return jsonify({
        'message': 'LDAP sync complete',
        'created': created,
        'updated': updated
    }), 200
