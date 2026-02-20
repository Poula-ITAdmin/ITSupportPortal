from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import enum

db = SQLAlchemy()


class UserRole(enum.Enum):
    """User role enumeration"""
    EMPLOYEE = 'employee'
    IT_LEVEL1 = 'it_level1'
    IT_LEVEL2 = 'it_level2'
    ADMIN = 'admin'
    MANAGER = 'manager'


class TicketStatus(enum.Enum):
    """Ticket status enumeration"""
    OPEN = 'open'
    ASSIGNED = 'assigned'
    IN_PROGRESS = 'in_progress'
    WAITING_USER = 'waiting_user'
    ESCALATED = 'escalated'
    RESOLVED = 'resolved'
    CLOSED = 'closed'


class TicketPriority(enum.Enum):
    """Ticket priority enumeration"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class TicketCategory(enum.Enum):
    """Ticket category enumeration"""
    HARDWARE = 'hardware'
    SOFTWARE = 'software'
    NETWORK = 'network'
    ACCOUNT = 'account'
    EMAIL = 'email'
    PRINTER = 'printer'
    ACCESS = 'access'
    OTHER = 'other'


class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # NULL for LDAP users
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255), nullable=True)
    job_title = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Role and permissions
    role = db.Column(db.Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_ldap_user = db.Column(db.Boolean, default=False, nullable=False)
    
    # AD Groups (stored as JSON for flexibility)
    ad_groups = db.Column(db.JSON, default=list, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    tickets_created = db.relationship('Ticket', backref='creator', foreign_keys='Ticket.created_by', lazy=True)
    tickets_assigned = db.relationship('Ticket', backref='assigned_to_user', foreign_keys='Ticket.assigned_to', lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='author', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='assigned_user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Ticket(db.Model):
    """Ticket model"""
    __tablename__ = 'tickets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Category and priority
    category = db.Column(db.Enum(TicketCategory), default=TicketCategory.OTHER, nullable=False)
    priority = db.Column(db.Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    status = db.Column(db.Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False, index=True)
    
    # Assignment
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    department = db.Column(db.String(255), nullable=True)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # SLA tracking
    sla_due_date = db.Column(db.DateTime, nullable=True)
    sla_violated = db.Column(db.Boolean, default=False, nullable=False)
    
    # Internal notes (IT team only)
    internal_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    attachments = db.relationship('Attachment', backref='ticket', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('TicketComment', backref='ticket', lazy=True, cascade='all, delete-orphan')
    chat_channel = db.relationship('ChatChannel', backref='ticket', lazy=True, uselist=False, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ticket {self.ticket_number}>'


class TicketComment(db.Model):
    """Ticket comment/reply model"""
    __tablename__ = 'ticket_comments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = db.Column(db.String(36), db.ForeignKey('tickets.id'), nullable=False)
    author_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False, nullable=False)  # Visible only to IT
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    author = db.relationship('User', backref='ticket_comments')
    
    def __repr__(self):
        return f'<TicketComment {self.id}>'


class Attachment(db.Model):
    """File attachment model"""
    __tablename__ = 'attachments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = db.Column(db.String(36), db.ForeignKey('tickets.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    uploader = db.relationship('User', backref='attachments')
    
    def __repr__(self):
        return f'<Attachment {self.filename}>'


class ChatChannel(db.Model):
    """Chat channel model"""
    __tablename__ = 'chat_channels'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    channel_type = db.Column(db.String(20), nullable=False)  # 'department', 'ticket', 'direct'
    ticket_id = db.Column(db.String(36), db.ForeignKey('tickets.id'), nullable=True)
    department = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    members = db.relationship('User', lazy=True, secondary='chat_channel_members')
    messages = db.relationship('ChatMessage', backref='channel', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChatChannel {self.name}>'


# Association table for chat channel members
chat_channel_members = db.Table(
    'chat_channel_members',
    db.Column('channel_id', db.String(36), db.ForeignKey('chat_channels.id'), primary_key=True),
    db.Column('user_id', db.String(36), db.ForeignKey('users.id'), primary_key=True)
)


class ChatMessage(db.Model):
    """Chat message model"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = db.Column(db.String(36), db.ForeignKey('chat_channels.id'), nullable=False)
    author_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text', nullable=False)  # 'text', 'file', 'system'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_edited = db.Column(db.Boolean, default=False, nullable=False)
    
    reactions = db.Column(db.JSON, default=dict, nullable=False)  # {'emoji': ['user_id1', 'user_id2']}
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>'


class Task(db.Model):
    """Calendar task/planner model"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ticket_id = db.Column(db.String(36), db.ForeignKey('tickets.id'), nullable=True)
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    department = db.Column(db.String(255), nullable=True)
    
    # Scheduling
    start_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'in_progress', 'completed'
    priority = db.Column(db.Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    
    # Appearance
    category = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(7), default='#3498db', nullable=False)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Task {self.title}>'


class AuditLog(db.Model):
    """Audit log for compliance and tracking"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # 'ticket', 'user', 'channel', etc.
    resource_id = db.Column(db.String(36), nullable=False)
    changes = db.Column(db.JSON, nullable=True)  # What changed
    ip_address = db.Column(db.String(15), nullable=True)
    status = db.Column(db.String(20), default='success', nullable=False)  # 'success', 'failure'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'


class SLAPolicy(db.Model):
    """SLA Policy configuration"""
    __tablename__ = 'sla_policies'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    target_response_time = db.Column(db.Integer, nullable=False)  # in hours
    target_resolution_time = db.Column(db.Integer, nullable=False)  # in hours
    priority_level = db.Column(db.Enum(TicketPriority), nullable=False)
    category = db.Column(db.Enum(TicketCategory), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<SLAPolicy {self.name}>'
