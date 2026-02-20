"""
Database initialization and migration script
Run this after installing dependencies to set up the database
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.models import db, User, UserRole, TicketCategory, TicketPriority, SLAPolicy
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize the database with tables and default data"""
    
    app, _ = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("✅ Tables created successfully")
            
            # Add default SLA policies
            logger.info("Adding default SLA policies...")
            default_slas = [
                {
                    'name': 'Critical Priority',
                    'description': 'Critical issues requiring immediate attention',
                    'target_response_time': 1,  # 1 hour
                    'target_resolution_time': 4,  # 4 hours
                    'priority_level': TicketPriority.CRITICAL,
                    'category': None
                },
                {
                    'name': 'High Priority',
                    'description': 'High priority issues affecting productivity',
                    'target_response_time': 2,
                    'target_resolution_time': 8,
                    'priority_level': TicketPriority.HIGH,
                    'category': None
                },
                {
                    'name': 'Medium Priority',
                    'description': 'Standard support requests',
                    'target_response_time': 4,
                    'target_resolution_time': 24,
                    'priority_level': TicketPriority.MEDIUM,
                    'category': None
                },
                {
                    'name': 'Low Priority',
                    'description': 'Non-urgent requests',
                    'target_response_time': 8,
                    'target_resolution_time': 72,
                    'priority_level': TicketPriority.LOW,
                    'category': None
                },
            ]
            
            for sla_data in default_slas:
                existing = SLAPolicy.query.filter_by(name=sla_data['name']).first()
                if not existing:
                    sla = SLAPolicy(**sla_data)
                    db.session.add(sla)
            
            db.session.commit()
            logger.info("✅ SLA policies added")
            
            # Create default admin if none exists
            admin = User.query.filter_by(role=UserRole.ADMIN).first()
            if not admin:
                logger.info("Creating default admin user...")
                import bcrypt
                
                password_hash = bcrypt.hashpw(
                    b'admin123',  # Change this!
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                admin = User(
                    username='admin',
                    email='admin@company.com',
                    password_hash=password_hash,
                    first_name='System',
                    last_name='Administrator',
                    department='IT',
                    job_title='System Administrator',
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_ldap_user=False
                )
                
                db.session.add(admin)
                db.session.commit()
                
                logger.info("✅ Default admin user created")
                logger.warning("⚠️  Default admin password is 'admin123' - CHANGE THIS IMMEDIATELY!")
                logger.warning("   Run the change-password endpoint or database update")
            
            logger.info("✅ Database initialization complete!")
            logger.info("\n📋 Database Summary:")
            logger.info(f"   - Users: {User.query.count()}")
            logger.info(f"   - SLA Policies: {SLAPolicy.query.count()}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            return False


def reset_database():
    """Drop all tables and reinitialize"""
    
    app, _ = create_app()
    
    with app.app_context():
        try:
            logger.warning("⚠️  Dropping all tables...")
            db.drop_all()
            logger.info("✅ Tables dropped")
            
            logger.info("Reinitializing database...")
            db.create_all()
            logger.info("✅ Tables recreated")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database reset failed: {str(e)}")
            return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database initialization')
    parser.add_argument('--reset', action='store_true', help='Reset database (drop and recreate)')
    
    args = parser.parse_args()
    
    if args.reset:
        confirm = input("⚠️  This will delete all data. Are you sure? (yes/no): ")
        if confirm.lower() == 'yes':
            reset_database()
            init_database()
        else:
            logger.info("Operation cancelled")
    else:
        init_database()
