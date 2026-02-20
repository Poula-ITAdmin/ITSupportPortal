"""
Chat system routes
Real-time messaging, channels, and communication
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

from app.models import db, ChatChannel, ChatMessage, User, chat_channel_members
from app.utils.decorators import handle_errors

logger = logging.getLogger(__name__)
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@chat_bp.route('/channels', methods=['GET'])
@jwt_required()
@handle_errors
def list_channels():
    """List available chat channels"""
    user_id = get_jwt_identity()
    
    # Get user's channels and department channels
    user = User.query.get(user_id)
    
    channels = ChatChannel.query.filter(
        (ChatChannel.members.any(User.id == user_id)) |
        (ChatChannel.channel_type == 'department') |
        (ChatChannel.ticket_id.isnot(None))
    ).all()
    
    return jsonify({
        'channels': [
            {
                'id': c.id,
                'name': c.name,
                'channel_type': c.channel_type,
                'department': c.department,
                'ticket_id': c.ticket_id,
                'member_count': len(c.members),
                'created_at': c.created_at.isoformat(),
                'unread': 0  # TODO: Implement unread count
            }
            for c in channels if c.is_active
        ]
    }), 200


@chat_bp.route('/channels', methods=['POST'])
@jwt_required()
@handle_errors
def create_channel():
    """Create a new chat channel"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('name') or not data.get('channel_type'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    channel = ChatChannel(
        name=data['name'],
        channel_type=data['channel_type'],
        department=data.get('department')
    )
    
    # Add creator as member
    creator = User.query.get(user_id)
    if creator:
        channel.members.append(creator)
    
    db.session.add(channel)
    db.session.commit()
    
    logger.info(f"Channel created: {channel.name}")
    
    return jsonify({
        'id': channel.id,
        'name': channel.name,
        'channel_type': channel.channel_type,
        'created_at': channel.created_at.isoformat()
    }), 201


@chat_bp.route('/channels/<channel_id>/messages', methods=['GET'])
@jwt_required()
@handle_errors
def get_channel_messages(channel_id):
    """Get messages in a channel"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    channel = ChatChannel.query.get(channel_id)
    if not channel:
        return jsonify({'error': 'Channel not found'}), 404
    
    # Check membership
    if not User.query.get(user_id) in channel.members and channel.channel_type != 'department':
        return jsonify({'error': 'Not a member of this channel'}), 403
    
    messages = ChatMessage.query.filter_by(channel_id=channel_id).paginate(page=page, per_page=limit)
    
    return jsonify({
        'total': messages.total,
        'page': page,
        'messages': [
            {
                'id': m.id,
                'author': {
                    'id': m.author.id,
                    'username': m.author.username,
                    'full_name': m.author.get_full_name()
                },
                'content': m.content,
                'message_type': m.message_type,
                'created_at': m.created_at.isoformat(),
                'updated_at': m.updated_at.isoformat(),
                'is_edited': m.is_edited,
                'reactions': m.reactions
            }
            for m in messages.items
        ]
    }), 200


@chat_bp.route('/channels/<channel_id>/join', methods=['POST'])
@jwt_required()
@handle_errors
def join_channel(channel_id):
    """Join a chat channel"""
    user_id = get_jwt_identity()
    
    channel = ChatChannel.query.get(channel_id)
    if not channel:
        return jsonify({'error': 'Channel not found'}), 404
    
    user = User.query.get(user_id)
    if user in channel.members:
        return jsonify({'error': 'Already a member'}), 400
    
    channel.members.append(user)
    db.session.commit()
    
    logger.info(f"User joined channel: {user.username} -> {channel.name}")
    
    return jsonify({'message': 'Joined channel'}), 200


@chat_bp.route('/channels/<channel_id>/leave', methods=['POST'])
@jwt_required()
@handle_errors
def leave_channel(channel_id):
    """Leave a chat channel"""
    user_id = get_jwt_identity()
    
    channel = ChatChannel.query.get(channel_id)
    if not channel:
        return jsonify({'error': 'Channel not found'}), 404
    
    user = User.query.get(user_id)
    if user not in channel.members:
        return jsonify({'error': 'Not a member'}), 400
    
    channel.members.remove(user)
    db.session.commit()
    
    logger.info(f"User left channel: {user.username} -> {channel.name}")
    
    return jsonify({'message': 'Left channel'}), 200


@chat_bp.route('/channels/<channel_id>/members', methods=['GET'])
@jwt_required()
@handle_errors
def get_channel_members(channel_id):
    """Get channel members"""
    channel = ChatChannel.query.get(channel_id)
    
    if not channel:
        return jsonify({'error': 'Channel not found'}), 404
    
    return jsonify({
        'members': [
            {
                'id': m.id,
                'username': m.username,
                'email': m.email,
                'full_name': m.get_full_name(),
                'department': m.department,
                'is_online': False  # TODO: Implement presence tracking
            }
            for m in channel.members
        ]
    }), 200
