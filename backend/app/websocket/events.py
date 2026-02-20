"""
WebSocket Event Handlers
Real-time communication using Flask-SocketIO
"""

import logging
from datetime import datetime
from flask_socketio import emit, join_room, leave_room, rooms
from flask_jwt_extended import decode_token
import os

from app.models import db, ChatMessage, ChatChannel, User

logger = logging.getLogger(__name__)

# Track online users
online_users = {}


def register_websocket_events(socketio):
    """Register all WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect(data):
        """Handle client connection"""
        auth_token = data.get('token') if data else None
        
        if not auth_token:
            logger.warning("Connection attempt without token")
            return False
        
        try:
            # Decode JWT token
            secret_key = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
            payload = decode_token(auth_token)
            user_id = payload['sub']
            
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"Connection attempt with invalid user: {user_id}")
                return False
            
            # Track online user
            online_users[user_id] = {
                'username': user.username,
                'connected_at': datetime.utcnow(),
                'rooms': []
            }
            
            logger.info(f"User connected: {user.username}")
            emit('connection_established', {
                'user_id': user_id,
                'username': user.username,
                'message': 'Connected to real-time service'
            })
            
            # Notify other users
            emit('user_online', {
                'user_id': user_id,
                'username': user.username
            }, broadcast=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False
    
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        # Find disconnected user
        for user_id, data in list(online_users.items()):
            if data.get('sid') == id(online_users):
                del online_users[user_id]
                emit('user_offline', {
                    'user_id': user_id,
                    'username': data['username']
                }, broadcast=True)
                logger.info(f"User disconnected: {data['username']}")
                break
    
    
    @socketio.on('join_channel')
    def handle_join_channel(data):
        """Join a chat channel room"""
        channel_id = data.get('channel_id')
        user_id = data.get('user_id')
        
        room = f"channel_{channel_id}"
        join_room(room)
        
        # Track room
        if user_id in online_users:
            if room not in online_users[user_id]['rooms']:
                online_users[user_id]['rooms'].append(room)
        
        logger.info(f"User {user_id} joined channel {channel_id}")
        
        emit('user_joined_channel', {
            'channel_id': channel_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
    
    
    @socketio.on('leave_channel')
    def handle_leave_channel(data):
        """Leave a chat channel room"""
        channel_id = data.get('channel_id')
        user_id = data.get('user_id')
        
        room = f"channel_{channel_id}"
        leave_room(room)
        
        # Update room tracking
        if user_id in online_users and room in online_users[user_id]['rooms']:
            online_users[user_id]['rooms'].remove(room)
        
        logger.info(f"User {user_id} left channel {channel_id}")
        
        emit('user_left_channel', {
            'channel_id': channel_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
    
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle sending a message"""
        channel_id = data.get('channel_id')
        author_id = data.get('user_id')
        content = data.get('content')
        
        if not all([channel_id, author_id, content]):
            emit('error', {'message': 'Missing required fields'})
            return
        
        try:
            # Save message to database
            message = ChatMessage(
                channel_id=channel_id,
                author_id=author_id,
                content=content,
                message_type='text'
            )
            
            db.session.add(message)
            db.session.commit()
            
            # Get author info
            author = User.query.get(author_id)
            
            # Broadcast message to channel
            room = f"channel_{channel_id}"
            emit('new_message', {
                'id': message.id,
                'channel_id': channel_id,
                'author': {
                    'id': author.id,
                    'username': author.username,
                    'full_name': author.get_full_name()
                },
                'content': message.content,
                'type': 'text',
                'timestamp': message.created_at.isoformat()
            }, room=room)
            
            logger.debug(f"Message sent in channel {channel_id}")
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            emit('error', {'message': 'Failed to send message'})
    
    
    @socketio.on('typing')
    def handle_typing(data):
        """Notify others that user is typing"""
        channel_id = data.get('channel_id')
        user_id = data.get('user_id')
        username = data.get('username')
        
        room = f"channel_{channel_id}"
        emit('user_typing', {
            'user_id': user_id,
            'username': username,
            'channel_id': channel_id
        }, room=room, skip_sid=True)
    
    
    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """Notify others that user stopped typing"""
        channel_id = data.get('channel_id')
        user_id = data.get('user_id')
        
        room = f"channel_{channel_id}"
        emit('user_stop_typing', {
            'user_id': user_id,
            'channel_id': channel_id
        }, room=room, skip_sid=True)
    
    
    @socketio.on('get_online_users')
    def handle_get_online_users():
        """Get list of online users"""
        users = [
            {
                'user_id': uid,
                'username': data['username'],
                'rooms': data['rooms']
            }
            for uid, data in online_users.items()
        ]
        
        emit('online_users', {'users': users})
    
    
    @socketio.on('ticket_update')
    def handle_ticket_update(data):
        """Broadcast ticket update"""
        ticket_id = data.get('ticket_id')
        room = f"ticket_{ticket_id}"
        
        emit('ticket_updated', {
            'ticket_id': ticket_id,
            'status': data.get('status'),
            'updated_at': datetime.utcnow().isoformat()
        }, room=room)
        
        logger.debug(f"Ticket {ticket_id} update broadcast")
    
    
    @socketio.on('notification')
    def handle_notification(data):
        """Send notification to user"""
        recipient_id = data.get('recipient_id')
        notification_type = data.get('type')
        content = data.get('content')
        
        # Send to specific user's room
        room = f"user_{recipient_id}"
        emit('notification', {
            'type': notification_type,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
        
        logger.debug(f"Notification sent to user {recipient_id}")
