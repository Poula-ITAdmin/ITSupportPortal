"""
Utility decorators for Flask routes
"""

from functools import wraps
from flask import jsonify, request
import logging
from app.models import db, AuditLog, User

logger = logging.getLogger(__name__)


def handle_errors(f):
    """Decorator to handle exceptions and return proper error responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except PermissionError as e:
            logger.error(f"Permission error: {str(e)}")
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return jsonify({'error': 'An unexpected error occurred'}), 500
    
    return decorated_function


def log_audit(resource_type: str, action: str):
    """Decorator to log audit trail"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_jwt_extended import get_jwt_identity
            
            try:
                result = f(*args, **kwargs)
                
                # Log successful action
                user_id = get_jwt_identity()
                ip_address = request.remote_addr
                
                audit_log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=kwargs.get('id', 'unknown'),
                    ip_address=ip_address,
                    status='success'
                )
                db.session.add(audit_log)
                db.session.commit()
                
                logger.info(f"Audit: {action} on {resource_type}")
                
                return result
                
            except Exception as e:
                # Log failed action
                user_id = get_jwt_identity()
                ip_address = request.remote_addr
                
                audit_log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=kwargs.get('id', 'unknown'),
                    ip_address=ip_address,
                    status='failure'
                )
                db.session.add(audit_log)
                db.session.commit()
                
                raise
        
        return decorated_function
    return decorator


def require_role(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_jwt_extended import get_jwt_identity
            
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role.value not in roles:
                logger.warning(f"User {user_id} attempted access without required role")
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_json(*required_fields):
    """Decorator to validate JSON request has required fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Request body must be JSON'}), 400
            
            missing = [field for field in required_fields if field not in data]
            if missing:
                return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
