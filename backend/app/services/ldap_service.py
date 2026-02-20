"""
LDAP Authentication Service
Handles all Active Directory LDAP operations and user provisioning
"""

import ldap
import ldap.modlist as modlist
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.models import User, UserRole, db

logger = logging.getLogger(__name__)


class LDAPService:
    """Service for LDAP/Active Directory operations"""
    
    def __init__(self):
        self.server = os.environ.get('LDAP_SERVER', 'ldap://localhost')
        self.port = int(os.environ.get('LDAP_PORT', 389))
        self.use_ssl = os.environ.get('LDAP_USE_SSL', 'false').lower() == 'true'
        self.base_dn = os.environ.get('LDAP_BASE_DN', 'dc=company,dc=com')
        self.bind_dn = os.environ.get('LDAP_BIND_DN')
        self.bind_password = os.environ.get('LDAP_BIND_PASSWORD')
        self.user_search_base = os.environ.get('LDAP_USER_SEARCH_BASE', f'ou=Users,{self.base_dn}')
        self.group_search_base = os.environ.get('LDAP_GROUP_SEARCH_BASE', f'ou=Groups,{self.base_dn}')
        
        # Role mapping from AD groups
        self.role_mapping = {
            'IT_Level1': UserRole.IT_LEVEL1,
            'IT_Level2': UserRole.IT_LEVEL2,
            'System_Admins': UserRole.ADMIN,
            'Managers': UserRole.MANAGER,
        }
        
        self.conn = None
    
    def _get_connection(self) -> ldap.ldapobject.LDAPObject:
        """Create and return LDAP connection"""
        try:
            uri = f"{'ldaps' if self.use_ssl else 'ldap'}://{self.server}:{self.port}"
            conn = ldap.initialize(uri)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            
            if self.use_ssl:
                conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            
            # Bind with service account
            conn.simple_bind_s(self.bind_dn, self.bind_password)
            logger.info("LDAP connection established")
            return conn
        except ldap.INVALID_CREDENTIALS:
            logger.error("Invalid LDAP credentials")
            raise Exception("Invalid LDAP credentials")
        except ldap.SERVER_DOWN:
            logger.error("LDAP server is down")
            raise Exception("LDAP server is down")
        except Exception as e:
            logger.error(f"LDAP connection error: {str(e)}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Authenticate user against LDAP
        
        Returns:
            Tuple[bool, Optional[Dict]]: (success, user_data)
        """
        try:
            conn = self._get_connection()
            
            # Search for user
            search_filter = f"(sAMAccountName={username})"
            attributes = [
                'uid', 'sAMAccountName', 'cn', 'givenName', 'sn', 'mail',
                'telephoneNumber', 'department', 'title', 'userAccountControl'
            ]
            
            results = conn.search_s(self.user_search_base, ldap.SCOPE_SUBTREE, search_filter, attributes)
            
            if not results:
                logger.warning(f"User not found: {username}")
                return False, None
            
            user_dn, user_attrs = results[0]
            
            # Check if account is active (userAccountControl)
            if not self._is_account_active(user_attrs):
                logger.warning(f"User account is disabled: {username}")
                return False, None
            
            # Try to bind as user
            try:
                user_conn = ldap.initialize(f"{'ldaps' if self.use_ssl else 'ldap'}://{self.server}:{self.port}")
                user_conn.simple_bind_s(user_dn, password)
                user_conn.unbind_s()
            except ldap.INVALID_CREDENTIALS:
                logger.warning(f"Invalid password for user: {username}")
                return False, None
            
            # Get user groups and data
            user_data = self._parse_user_attributes(user_attrs, user_dn)
            user_data['groups'] = self._get_user_groups(conn, user_dn)
            
            conn.unbind_s()
            return True, user_data
            
        except Exception as e:
            logger.error(f"LDAP authentication error: {str(e)}")
            return False, None
    
    def search_users(self, search_filter: str) -> List[Dict]:
        """Search users in LDAP directory"""
        try:
            conn = self._get_connection()
            attributes = [
                'uid', 'sAMAccountName', 'cn', 'givenName', 'sn', 'mail',
                'telephoneNumber', 'department', 'title'
            ]
            
            results = conn.search_s(self.user_search_base, ldap.SCOPE_SUBTREE, search_filter, attributes)
            users = [self._parse_user_attributes(attrs, dn) for dn, attrs in results]
            
            conn.unbind_s()
            return users
            
        except Exception as e:
            logger.error(f"LDAP search error: {str(e)}")
            return []
    
    def get_all_users(self) -> List[Dict]:
        """Get all users from LDAP"""
        return self.search_users("(objectClass=person)")
    
    def get_user_groups(self, username: str) -> List[str]:
        """Get all groups for a user"""
        try:
            conn = self._get_connection()
            search_filter = f"(sAMAccountName={username})"
            results = conn.search_s(self.user_search_base, ldap.SCOPE_SUBTREE, search_filter)
            
            if results:
                user_dn = results[0][0]
                groups = self._get_user_groups(conn, user_dn)
                conn.unbind_s()
                return groups
            
            return []
        except Exception as e:
            logger.error(f"Error getting user groups: {str(e)}")
            return []
    
    def _get_user_groups(self, conn: ldap.ldapobject.LDAPObject, user_dn: str) -> List[str]:
        """Get groups for a user DN"""
        try:
            groups = []
            search_filter = f"(member={user_dn})"
            attributes = ['cn']
            
            results = conn.search_s(self.group_search_base, ldap.SCOPE_SUBTREE, search_filter, attributes)
            
            for dn, attrs in results:
                if 'cn' in attrs:
                    group_name = attrs['cn'][0].decode('utf-8') if isinstance(attrs['cn'][0], bytes) else attrs['cn'][0]
                    groups.append(group_name)
            
            return groups
        except Exception as e:
            logger.error(f"Error getting groups for user: {str(e)}")
            return []
    
    def _parse_user_attributes(self, attrs: Dict, dn: str) -> Dict:
        """Parse LDAP user attributes into dict"""
        
        def get_attr(key, default=''):
            if key in attrs and attrs[key]:
                val = attrs[key][0]
                return val.decode('utf-8') if isinstance(val, bytes) else val
            return default
        
        return {
            'dn': dn,
            'username': get_attr('sAMAccountName'),
            'email': get_attr('mail'),
            'first_name': get_attr('givenName'),
            'last_name': get_attr('sn'),
            'full_name': get_attr('cn'),
            'department': get_attr('department'),
            'job_title': get_attr('title'),
            'phone': get_attr('telephoneNumber'),
        }
    
    def _is_account_active(self, attrs: Dict) -> bool:
        """Check if AD account is active"""
        try:
            if 'userAccountControl' not in attrs:
                return True
            
            control = int(attrs['userAccountControl'][0])
            # Bit 1 (0x0002) = ACCOUNTDISABLE
            return not (control & 0x0002)
        except Exception as e:
            logger.warning(f"Error checking account active status: {str(e)}")
            return True
    
    def sync_user(self, ldap_user_data: Dict) -> User:
        """
        Sync or create user from LDAP data
        
        Args:
            ldap_user_data: User data from LDAP
            
        Returns:
            User: Created or updated user object
        """
        username = ldap_user_data['username']
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Update existing user
            user.email = ldap_user_data['email']
            user.first_name = ldap_user_data['first_name']
            user.last_name = ldap_user_data['last_name']
            user.department = ldap_user_data['department']
            user.job_title = ldap_user_data['job_title']
            user.phone = ldap_user_data['phone']
            user.ad_groups = ldap_user_data.get('groups', [])
            user.is_ldap_user = True
            user.is_active = True
            user.updated_at = datetime.utcnow()
        else:
            # Create new user
            user = User(
                username=username,
                email=ldap_user_data['email'],
                first_name=ldap_user_data['first_name'],
                last_name=ldap_user_data['last_name'],
                department=ldap_user_data['department'],
                job_title=ldap_user_data['job_title'],
                phone=ldap_user_data['phone'],
                ad_groups=ldap_user_data.get('groups', []),
                is_ldap_user=True,
                role=self._determine_role(ldap_user_data.get('groups', []))
            )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User synced: {username}")
        return user
    
    def _determine_role(self, groups: List[str]) -> UserRole:
        """Determine user role based on AD groups"""
        for group in groups:
            if group in self.role_mapping:
                return self.role_mapping[group]
        
        return UserRole.EMPLOYEE
    
    def sync_all_users(self) -> Tuple[int, int]:
        """
        Sync all users from LDAP to database
        
        Returns:
            Tuple[int, int]: (created_count, updated_count)
        """
        try:
            all_users = self.get_all_users()
            created = 0
            updated = 0
            
            for ldap_user in all_users:
                if not ldap_user['email']:  # Skip users without email
                    continue
                
                user = User.query.filter_by(username=ldap_user['username']).first()
                
                # Get user groups
                ldap_user['groups'] = self._get_user_groups_by_dn(ldap_user['dn'])
                
                if user:
                    updated += 1
                else:
                    created += 1
                
                self.sync_user(ldap_user)
            
            logger.info(f"LDAP sync complete: {created} created, {updated} updated")
            return created, updated
            
        except Exception as e:
            logger.error(f"Error syncing all users: {str(e)}")
            return 0, 0
    
    def _get_user_groups_by_dn(self, user_dn: str) -> List[str]:
        """Get groups for user using DN (helper method)"""
        try:
            conn = self._get_connection()
            groups = self._get_user_groups(conn, user_dn)
            conn.unbind_s()
            return groups
        except Exception as e:
            logger.error(f"Error getting groups by DN: {str(e)}")
            return []


# Singleton instance
ldap_service = LDAPService()
