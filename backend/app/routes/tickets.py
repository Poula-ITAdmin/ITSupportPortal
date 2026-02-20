"""
Ticket routes / API endpoints
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime

from app.models import (
    db, Ticket, TicketStatus, TicketPriority, TicketCategory,
    TicketComment, User, UserRole, Attachment
)
from app.services.ticket_service import TicketService
from app.utils.decorators import handle_errors, require_role, log_audit, validate_json

logger = logging.getLogger(__name__)
tickets_bp = Blueprint('tickets', __name__, url_prefix='/api/tickets')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip'}


@tickets_bp.route('', methods=['POST'])
@jwt_required()
@handle_errors
def create_ticket():
    """Create a new ticket"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['title', 'description', 'category', 'priority']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        ticket = TicketService.create_ticket(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            priority=data['priority'],
            created_by=user_id,
            department=data.get('department')
        )
        
        return jsonify({
            'id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'title': ticket.title,
            'category': ticket.category.value,
            'priority': ticket.priority.value,
            'status': ticket.status.value,
            'created_at': ticket.created_at.isoformat()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@tickets_bp.route('/<ticket_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_ticket(ticket_id):
    """Get ticket details"""
    user_id = get_jwt_identity()
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Check permissions
    user = User.query.get(user_id)
    is_creator = ticket.created_by == user_id
    is_assigned = ticket.assigned_to == user_id
    is_it = user.role in [UserRole.IT_LEVEL1, UserRole.IT_LEVEL2, UserRole.ADMIN]
    
    if not (is_creator or is_assigned or is_it):
        return jsonify({'error': 'No access to this ticket'}), 403
    
    # Build response
    response = {
        'id': ticket.id,
        'ticket_number': ticket.ticket_number,
        'title': ticket.title,
        'description': ticket.description,
        'category': ticket.category.value,
        'priority': ticket.priority.value,
        'status': ticket.status.value,
        'department': ticket.department,
        'created_by': {
            'id': ticket.creator.id,
            'username': ticket.creator.username,
            'email': ticket.creator.email,
            'full_name': ticket.creator.get_full_name()
        },
        'assigned_to': None,
        'created_at': ticket.created_at.isoformat(),
        'updated_at': ticket.updated_at.isoformat(),
        'assigned_at': ticket.assigned_at.isoformat() if ticket.assigned_at else None,
        'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None,
        'sla_due_date': ticket.sla_due_date.isoformat() if ticket.sla_due_date else None,
        'sla_violated': ticket.sla_violated,
        'internal_notes': ticket.internal_notes if is_it else None,
        'comments': [
            {
                'id': c.id,
                'author': {
                    'id': c.author.id,
                    'username': c.author.username,
                    'full_name': c.author.get_full_name()
                },
                'content': c.content,
                'is_internal': c.is_internal if is_it else False,
                'created_at': c.created_at.isoformat()
            }
            for c in ticket.comments
            if not c.is_internal or is_it
        ],
        'attachments': [
            {
                'id': a.id,
                'filename': a.filename,
                'file_size': a.file_size,
                'mime_type': a.mime_type,
                'uploaded_at': a.created_at.isoformat()
            }
            for a in ticket.attachments
        ]
    }
    
    if ticket.assigned_to:
        assignee = User.query.get(ticket.assigned_to)
        response['assigned_to'] = {
            'id': assignee.id,
            'username': assignee.username,
            'email': assignee.email,
            'full_name': assignee.get_full_name()
        }
    
    return jsonify(response), 200


@tickets_bp.route('/<ticket_id>', methods=['PUT'])
@jwt_required()
@handle_errors
def update_ticket(ticket_id):
    """Update ticket"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    user = User.query.get(user_id)
    
    # Permission checks
    is_creator = ticket.created_by == user_id
    is_assigned = ticket.assigned_to == user_id
    is_it = user.role in [UserRole.IT_LEVEL1, UserRole.IT_LEVEL2, UserRole.ADMIN]
    
    if not (is_creator or is_assigned or is_it):
        return jsonify({'error': 'No permission to update'}), 403
    
    # Employees can only update description/internal notes
    if not is_it and 'status' in data:
        return jsonify({'error': 'Only IT can change status'}), 403
    
    try:
        updated = TicketService.update_ticket(ticket_id, user_id, **data)
        
        return jsonify({
            'id': updated.id,
            'ticket_number': updated.ticket_number,
            'status': updated.status.value,
            'priority': updated.priority.value,
            'updated_at': updated.updated_at.isoformat()
        }), 200
    
    except (ValueError, PermissionError) as e:
        return jsonify({'error': str(e)}), 400


@tickets_bp.route('/<ticket_id>/assign', methods=['POST'])
@jwt_required()
@require_role('it_level1', 'it_level2', 'admin')
@handle_errors
def assign_ticket(ticket_id):
    """Assign ticket to user"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('assigned_to'):
        return jsonify({'error': 'Missing assigned_to'}), 400
    
    try:
        ticket = TicketService.assign_ticket(ticket_id, data['assigned_to'], user_id)
        
        return jsonify({
            'id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'status': ticket.status.value,
            'assigned_to': ticket.assigned_to,
            'assigned_at': ticket.assigned_at.isoformat()
        }), 200
    
    except (ValueError, PermissionError) as e:
        return jsonify({'error': str(e)}), 400


@tickets_bp.route('/<ticket_id>/close', methods=['POST'])
@jwt_required()
@require_role('it_level1', 'it_level2', 'admin')
@handle_errors
def close_ticket(ticket_id):
    """Close ticket"""
    user_id = get_jwt_identity()
    
    try:
        ticket = TicketService.close_ticket(ticket_id, user_id)
        
        return jsonify({
            'id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'status': ticket.status.value,
            'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@tickets_bp.route('/<ticket_id>/comment', methods=['POST'])
@jwt_required()
@handle_errors
def add_comment(ticket_id):
    """Add comment to ticket"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('content'):
        return jsonify({'error': 'Missing content'}), 400
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    is_internal = data.get('is_internal', False)
    user = User.query.get(user_id)
    
    # Only IT can add internal notes
    if is_internal and user.role == UserRole.EMPLOYEE:
        return jsonify({'error': 'Only IT can add internal notes'}), 403
    
    try:
        comment = TicketService.add_comment(ticket_id, user_id, data['content'], is_internal)
        
        return jsonify({
            'id': comment.id,
            'author': {
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name()
            },
            'content': comment.content,
            'is_internal': comment.is_internal,
            'created_at': comment.created_at.isoformat()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@tickets_bp.route('/<ticket_id>/upload', methods=['POST'])
@jwt_required()
@handle_errors
def upload_attachment(ticket_id):
    """Upload file attachment"""
    user_id = get_jwt_identity()
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        upload_folder = os.environ.get('UPLOAD_FOLDER', './data/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, f"{ticket_id}_{filename}")
        file.save(filepath)
        
        # Create attachment record
        attachment = Attachment(
            ticket_id=ticket_id,
            filename=filename,
            filepath=filepath,
            file_size=os.path.getsize(filepath),
            mime_type=file.content_type,
            uploaded_by=user_id
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify({
            'id': attachment.id,
            'filename': attachment.filename,
            'file_size': attachment.file_size
        }), 201
    
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'File upload failed'}), 500


@tickets_bp.route('/<ticket_id>/download/<attachment_id>', methods=['GET'])
@jwt_required()
@handle_errors
def download_attachment(ticket_id, attachment_id):
    """Download file attachment"""
    
    attachment = Attachment.query.get(attachment_id)
    if not attachment or attachment.ticket_id != ticket_id:
        return jsonify({'error': 'Attachment not found'}), 404
    
    try:
        return send_file(attachment.filepath, as_attachment=True, download_name=attachment.filename)
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500


@tickets_bp.route('', methods=['GET'])
@jwt_required()
@handle_errors
def list_tickets():
    """List tickets with filtering"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Query parameters
    status = request.args.get('status')
    category = request.args.get('category')
    priority = request.args.get('priority')
    department = request.args.get('department')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    query = Ticket.query
    
    # Filter based on user role
    if user.role == UserRole.EMPLOYEE:
        query = query.filter_by(created_by=user_id)
    else:
        query = query.filter(
            (Ticket.created_by == user_id) | (Ticket.assigned_to == user_id)
        )
    
    # Apply filters
    if status:
        try:
            status_enum = TicketStatus[status.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            pass
    
    if category:
        try:
            category_enum = TicketCategory[category.upper()]
            query = query.filter_by(category=category_enum)
        except KeyError:
            pass
    
    if priority:
        try:
            priority_enum = TicketPriority[priority.upper()]
            query = query.filter_by(priority=priority_enum)
        except KeyError:
            pass
    
    if department:
        query = query.filter_by(department=department)
    
    total = query.count()
    tickets = query.order_by(Ticket.created_at.desc()).paginate(page=page, per_page=limit)
    
    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit,
        'tickets': [
            {
                'id': t.id,
                'ticket_number': t.ticket_number,
                'title': t.title,
                'category': t.category.value,
                'priority': t.priority.value,
                'status': t.status.value,
                'department': t.department,
                'created_at': t.created_at.isoformat(),
                'assigned_to': t.assigned_to,
                'sla_violated': t.sla_violated
            }
            for t in tickets.items
        ]
    }), 200


@tickets_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@handle_errors
def dashboard_stats():
    """Get dashboard statistics"""
    user_id = get_jwt_identity()
    
    stats = TicketService.get_dashboard_stats(user_id)
    return jsonify(stats), 200
