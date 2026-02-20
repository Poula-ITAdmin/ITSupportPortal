"""
Ticket Service
Handles all ticket business logic
"""

import uuid
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_, or_, desc
from app.models import (
    db, Ticket, TicketStatus, TicketPriority, TicketCategory, TicketComment,
    User, UserRole, Attachment, AuditLog, SLAPolicy, ChatChannel
)

logger = logging.getLogger(__name__)


class TicketService:
    """Service for ticket operations"""
    
    @staticmethod
    def create_ticket(
        title: str,
        description: str,
        category: str,
        priority: str,
        created_by: str,
        department: Optional[str] = None,
        **kwargs
    ) -> Ticket:
        """Create a new ticket"""
        
        # Generate ticket number
        ticket_number = f"TKT-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Validate enums
        try:
            category_enum = TicketCategory[category.upper()]
            priority_enum = TicketPriority[priority.upper()]
        except KeyError:
            raise ValueError(f"Invalid category or priority")
        
        # Create ticket
        ticket = Ticket(
            ticket_number=ticket_number,
            title=title,
            description=description,
            category=category_enum,
            priority=priority_enum,
            created_by=created_by,
            department=department or User.query.get(created_by).department,
            status=TicketStatus.OPEN
        )
        
        # Set SLA based on priority
        ticket.sla_due_date = TicketService._calculate_sla_due_date(priority_enum)
        
        # Create ticket channel
        channel = ChatChannel(
            name=f"Ticket {ticket_number}",
            channel_type='ticket',
            ticket_id=ticket.id
        )
        
        # Add creator as channel member
        creator = User.query.get(created_by)
        if creator:
            channel.members.append(creator)
        
        db.session.add(ticket)
        db.session.add(channel)
        db.session.commit()
        
        # Log action
        audit = AuditLog(
            user_id=created_by,
            action='create',
            resource_type='ticket',
            resource_id=ticket.id,
            status='success'
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"Ticket created: {ticket_number}")
        return ticket
    
    @staticmethod
    def update_ticket(
        ticket_id: str,
        updated_by: str,
        **updates
    ) -> Ticket:
        """Update ticket"""
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Verify user has permission
        user = User.query.get(updated_by)
        if user.role == UserRole.EMPLOYEE and ticket.created_by != updated_by:
            raise PermissionError("Users can only update their own tickets")
        
        # Track changes for audit log
        changes = {}
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'priority', 'category', 'status', 'assigned_to', 'internal_notes']
        
        for field, value in updates.items():
            if field not in allowed_fields:
                continue
            
            old_value = getattr(ticket, field, None)
            
            if field == 'priority':
                value = TicketPriority[value.upper()]
            elif field == 'category':
                value = TicketCategory[value.upper()]
            elif field == 'status':
                old_status = ticket.status
                value = TicketStatus[value.upper()]
                
                # Update status-related timestamps
                if value == TicketStatus.ASSIGNED:
                    ticket.assigned_at = datetime.utcnow()
                elif value == TicketStatus.RESOLVED:
                    ticket.resolved_at = datetime.utcnow()
            
            if old_value != value:
                changes[field] = {'old': str(old_value), 'new': str(value)}
                setattr(ticket, field, value)
        
        ticket.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log audit
        if changes:
            audit = AuditLog(
                user_id=updated_by,
                action='update',
                resource_type='ticket',
                resource_id=ticket_id,
                changes=changes,
                status='success'
            )
            db.session.add(audit)
            db.session.commit()
            
            logger.info(f"Ticket updated: {ticket.ticket_number}")
        
        return ticket
    
    @staticmethod
    def assign_ticket(
        ticket_id: str,
        assigned_to: str,
        assigned_by: str
    ) -> Ticket:
        """Assign ticket to user"""
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Verify assigner is IT team
        user = User.query.get(assigned_by)
        if user.role not in [UserRole.IT_LEVEL1, UserRole.IT_LEVEL2, UserRole.ADMIN]:
            raise PermissionError("Only IT team can assign tickets")
        
        ticket.assigned_to = assigned_to
        ticket.status = TicketStatus.ASSIGNED
        ticket.assigned_at = datetime.utcnow()
        ticket.updated_at = datetime.utcnow()
        
        # Add assignee to ticket channel
        assignee = User.query.get(assigned_to)
        if assignee and assignee not in ticket.chat_channel.members:
            ticket.chat_channel.members.append(assignee)
        
        db.session.commit()
        
        # Log action
        audit = AuditLog(
            user_id=assigned_by,
            action='assign',
            resource_type='ticket',
            resource_id=ticket_id,
            changes={'assigned_to': assigned_to},
            status='success'
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"Ticket assigned: {ticket.ticket_number} -> {assignee.username if assignee else 'unknown'}")
        return ticket
    
    @staticmethod
    def close_ticket(ticket_id: str, closed_by: str) -> Ticket:
        """Close resolved ticket"""
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        ticket.status = TicketStatus.CLOSED
        ticket.resolved_at = datetime.utcnow()
        ticket.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log action
        audit = AuditLog(
            user_id=closed_by,
            action='close',
            resource_type='ticket',
            resource_id=ticket_id,
            status='success'
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"Ticket closed: {ticket.ticket_number}")
        return ticket
    
    @staticmethod
    def add_comment(
        ticket_id: str,
        author_id: str,
        content: str,
        is_internal: bool = False
    ) -> TicketComment:
        """Add comment to ticket"""
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        comment = TicketComment(
            ticket_id=ticket_id,
            author_id=author_id,
            content=content,
            is_internal=is_internal
        )
        
        db.session.add(comment)
        
        # If ticket was waiting user, move back to assigned
        if ticket.status == TicketStatus.WAITING_USER:
            ticket.status = TicketStatus.IN_PROGRESS
        
        db.session.commit()
        
        logger.info(f"Comment added to ticket: {ticket.ticket_number}")
        return comment
    
    @staticmethod
    def get_user_tickets(
        user_id: str,
        status: Optional[str] = None,
        role: Optional[str] = None
    ) -> List[Ticket]:
        """Get tickets for user"""
        
        user = User.query.get(user_id)
        
        query = Ticket.query
        
        if role == UserRole.EMPLOYEE.value:
            # Employees see their own tickets
            query = query.filter_by(created_by=user_id)
        else:
            # IT team sees assigned tickets
            query = query.filter_by(assigned_to=user_id)
        
        if status:
            try:
                status_enum = TicketStatus[status.upper()]
                query = query.filter_by(status=status_enum)
            except KeyError:
                pass
        
        return query.order_by(desc(Ticket.created_at)).all()
    
    @staticmethod
    def get_dashboard_stats(user_id: str) -> Dict:
        """Get dashboard statistics for user"""
        
        user = User.query.get(user_id)
        
        total = Ticket.query.count()
        open_tickets = Ticket.query.filter_by(status=TicketStatus.OPEN).count()
        assigned = Ticket.query.filter_by(status=TicketStatus.ASSIGNED).count()
        in_progress = Ticket.query.filter_by(status=TicketStatus.IN_PROGRESS).count()
        closed = Ticket.query.filter_by(status=TicketStatus.CLOSED).count()
        
        # SLA violations
        sla_violated = Ticket.query.filter_by(sla_violated=True).count()
        
        # User-specific stats
        if user.role == UserRole.EMPLOYEE.value:
            my_tickets = Ticket.query.filter_by(created_by=user_id).count()
            return {
                'my_tickets': my_tickets,
                'total_tickets': total,
                'open': open_tickets,
                'assigned': assigned,
                'in_progress': in_progress,
                'closed': closed,
                'sla_violated': sla_violated,
            }
        else:
            assigned_to_me = Ticket.query.filter_by(assigned_to=user_id).count()
            return {
                'assigned_to_me': assigned_to_me,
                'total_tickets': total,
                'open': open_tickets,
                'assigned': assigned,
                'in_progress': in_progress,
                'closed': closed,
                'sla_violated': sla_violated,
            }
    
    @staticmethod
    def _calculate_sla_due_date(priority: TicketPriority) -> datetime:
        """Calculate SLA due date based on priority"""
        
        sla_hours = {
            TicketPriority.CRITICAL: 2,
            TicketPriority.HIGH: 4,
            TicketPriority.MEDIUM: 8,
            TicketPriority.LOW: 24,
        }
        
        hours = sla_hours.get(priority, 8)
        return datetime.utcnow() + timedelta(hours=hours)
    
    @staticmethod
    def check_sla_violations() -> int:
        """Check for SLA violations and update tickets"""
        
        now = datetime.utcnow()
        violated = Ticket.query.filter(
            and_(
                Ticket.sla_due_date < now,
                Ticket.status != TicketStatus.CLOSED,
                Ticket.sla_violated == False
            )
        ).all()
        
        for ticket in violated:
            ticket.sla_violated = True
            if ticket.status != TicketStatus.ESCALATED:
                ticket.status = TicketStatus.ESCALATED
        
        db.session.commit()
        logger.info(f"SLA violations checked: {len(violated)} tickets escalated")
        return len(violated)
