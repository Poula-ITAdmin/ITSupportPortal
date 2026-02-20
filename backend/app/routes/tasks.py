"""
Calendar task/planner routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime
from sqlalchemy import and_, or_

from app.models import db, Task, TicketPriority, User
from app.utils.decorators import handle_errors

logger = logging.getLogger(__name__)
tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


@tasks_bp.route('', methods=['POST'])
@jwt_required()
@handle_errors
def create_task():
    """Create a new task"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['title', 'start_date', 'due_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description'),
        ticket_id=data.get('ticket_id'),
        assigned_to=data.get('assigned_to') or user_id,
        department=data.get('department'),
        start_date=start_date,
        due_date=due_date,
        priority=TicketPriority[data.get('priority', 'medium').upper()],
        category=data.get('category'),
        color=data.get('color', '#3498db'),
        status=data.get('status', 'pending')
    )
    
    db.session.add(task)
    db.session.commit()
    
    logger.info(f"Task created: {task.title}")
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'status': task.status,
        'start_date': task.start_date.isoformat(),
        'due_date': task.due_date.isoformat(),
        'created_at': task.created_at.isoformat()
    }), 201


@tasks_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_task(task_id):
    """Get task details"""
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    response = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'ticket_id': task.ticket_id,
        'category': task.category,
        'priority': task.priority.value,
        'status': task.status,
        'color': task.color,
        'start_date': task.start_date.isoformat(),
        'due_date': task.due_date.isoformat(),
        'completed_date': task.completed_date.isoformat() if task.completed_date else None,
        'created_at': task.created_at.isoformat(),
        'updated_at': task.updated_at.isoformat(),
        'assigned_to': None
    }
    
    if task.assigned_to:
        user = User.query.get(task.assigned_to)
        if user:
            response['assigned_to'] = {
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name()
            }
    
    return jsonify(response), 200


@tasks_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
@handle_errors
def update_task(task_id):
    """Update task"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Update allowed fields
    allowed_fields = ['title', 'description', 'priority', 'status', 'category', 'color', 'assigned_to']
    
    for field in allowed_fields:
        if field in data:
            if field == 'priority':
                setattr(task, field, TicketPriority[data[field].upper()])
            else:
                setattr(task, field, data[field])
    
    # Handle dates
    if 'start_date' in data:
        try:
            task.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if 'due_date' in data:
        try:
            task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid due_date format'}), 400
    
    # Mark as completed if status is completed
    if data.get('status') == 'completed' and not task.completed_date:
        task.completed_date = datetime.utcnow()
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    logger.info(f"Task updated: {task.title}")
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'status': task.status,
        'updated_at': task.updated_at.isoformat()
    }), 200


@tasks_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
@handle_errors
def delete_task(task_id):
    """Delete task"""
    user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    logger.info(f"Task deleted: {task.title}")
    
    return jsonify({'message': 'Task deleted'}), 200


@tasks_bp.route('', methods=['GET'])
@jwt_required()
@handle_errors
def list_tasks():
    """List tasks with filtering"""
    user_id = get_jwt_identity()
    
    # Query parameters
    assigned_to = request.args.get('assigned_to', user_id)
    status = request.args.get('status')
    priority = request.args.get('priority')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    query = Task.query
    
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)
    
    if status:
        query = query.filter_by(status=status)
    
    if priority:
        try:
            priority_enum = TicketPriority[priority.upper()]
            query = query.filter_by(priority=priority_enum)
        except KeyError:
            pass
    
    # Date range filter
    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(and_(Task.start_date >= start, Task.due_date <= end))
        except ValueError:
            pass
    
    total = query.count()
    tasks = query.order_by(Task.due_date.asc()).paginate(page=page, per_page=limit)
    
    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit,
        'tasks': [
            {
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'category': t.category,
                'priority': t.priority.value,
                'status': t.status,
                'color': t.color,
                'start_date': t.start_date.isoformat(),
                'due_date': t.due_date.isoformat(),
                'assigned_to': t.assigned_to,
                'ticket_id': t.ticket_id,
                'created_at': t.created_at.isoformat()
            }
            for t in tasks.items
        ]
    }), 200


@tasks_bp.route('/calendar/<date_range>', methods=['GET'])
@jwt_required()
@handle_errors
def calendar_view(date_range):
    """Get tasks for calendar view"""
    user_id = get_jwt_identity()
    
    # date_range: 'day', 'week', 'month'
    # TODO: Implement calendar grouping
    
    tasks = Task.query.filter_by(assigned_to=user_id).all()
    
    return jsonify({
        'range': date_range,
        'tasks': [
            {
                'id': t.id,
                'title': t.title,
                'start_date': t.start_date.isoformat(),
                'due_date': t.due_date.isoformat(),
                'color': t.color,
                'status': t.status,
                'priority': t.priority.value
            }
            for t in tasks
        ]
    }), 200
