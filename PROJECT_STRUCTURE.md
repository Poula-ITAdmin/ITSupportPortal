# Project Structure

```
ITSupportPortal/
├── README.md                          # Old README (v1)
├── README_v2.md                       # New comprehensive README (v2)
├── DEPLOYMENT_GUIDE.md               # Proxmox deployment documentation
├── .env                              # Environment variables (not in git)
├── .env.example                      # Example environment file
├── .gitignore                        # Git ignore rules
├── docker-compose.yml                # Docker Compose configuration
├── Dockerfile                        # Docker build file
├── nginx.conf                        # Nginx reverse proxy configuration
│
├── backend/                          # Python Flask backend
│   ├── app.py                        # Entry point
│   ├── config.py                     # Configuration management
│   ├── requirements.txt              # Python dependencies
│   ├── init_db.py                    # Database initialization
│   │
│   └── app/
│       ├── __init__.py               # Flask app factory
│       │
│       ├── models/
│       │   └── __init__.py           # SQLAlchemy models
│       │                            # - User, Ticket, ChatChannel, Task, etc.
│       │
│       ├── routes/                   # API endpoints
│       │   ├── __init__.py
│       │   ├── auth.py               # Authentication (login, register, refresh)
│       │   ├── tickets.py            # Ticket CRUD and management
│       │   ├── users.py              # User management and LDAP sync
│       │   ├── chat.py               # Chat channels and messaging
│       │   └── tasks.py              # Calendar tasks and planning
│       │
│       ├── services/                 # Business logic
│       │   ├── __init__.py
│       │   ├── ldap_service.py       # LDAP/AD integration
│       │   ├── ticket_service.py     # Ticket business logic
│       │   └── email_service.py      # Email notifications (stub)
│       │
│       ├── middleware/               # Flask middleware
│       │   └── __init__.py           # Request/response handlers
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   └── decorators.py         # @handle_errors, @require_role, etc.
│       │
│       └── websocket/                # Real-time WebSocket
│           ├── __init__.py
│           └── events.py             # SocketIO event handlers
│
├── frontend/                         # Web frontend (Vue.js/React)
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   └── pages/                        # Page components
│
├── tests/                            # Test suite
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── conftest.py                   # Pytest configuration
│
├── docs/                             # Documentation
│   ├── API_REFERENCE.md              # Complete API documentation
│   ├── ARCHITECTURE.md               # System architecture
│   ├── SECURITY.md                   # Security policies
│   ├── DATABASE_SCHEMA.md             # Database design
│   └── TROUBLESHOOTING.md            # Common issues
│
└── data/                             # Data directory
    └── uploads/                      # File uploads
```

## Key Files

### Configuration
- `.env` - Environment variables (database, LDAP, SMTP, JWT secrets)
- `config.py` - Flask configuration classes
- `requirements.txt` - Python package dependencies

### Entry Points
- `backend/app.py` - Main Flask application entry point
- `backend/init_db.py` - Database initialization script

### Models (`app/models/__init__.py`)
- `User` - User accounts with roles (Employee, IT_LEVEL1, IT_LEVEL2, ADMIN, MANAGER)
- `Ticket` - Support tickets with full lifecycle
- `TicketComment` - Comments on tickets
- `TicketCategory` - Ticket categories (HARDWARE, SOFTWARE, NETWORK, etc.)
- `TicketPriority` - Priority levels (LOW, MEDIUM, HIGH, CRITICAL)
- `TicketStatus` - Status tracking (OPEN, ASSIGNED, IN_PROGRESS, etc.)
- `Attachment` - File attachments to tickets
- `ChatChannel` - Communication channels (department, ticket, direct)
- `ChatMessage` - Real-time chat messages
- `Task` - Calendar task planning
- `AuditLog` - Compliance and action tracking
- `SLAPolicy` - Service level agreement rules

### Services
- `ldap_service.py` - Complete LDAP/Active Directory integration
  - User authentication
  - User synchronization
  - Group mapping to roles
  - Account status checking

- `ticket_service.py` - Ticket operations
  - Create, update, assign tickets
  - Add comments
  - SLA tracking and escalation
  - Dashboard statistics

### Routes (API Endpoints)
- `/api/auth/*` - Authentication
  - POST `/login` - User login (LDAP or local)
  - POST `/refresh` - Refresh JWT token
  - POST `/register` - Local user registration
  - GET `/me` - Current user info
  - POST `/change-password` - Change password

- `/api/tickets/*` - Ticket management
  - GET/POST `/` - List/create tickets
  - GET/PUT `/<id>` - Get/update ticket
  - POST `/<id>/assign` - Assign ticket
  - POST `/<id>/close` - Close ticket
  - POST `/<id>/comment` - Add comment
  - POST `/<id>/upload` - Upload attachment
  - GET `/dashboard/stats` - Dashboard data

- `/api/users/*` - User management
  - GET `/` - List users (IT only)
  - GET `/<id>` - Get user details
  - PUT `/<id>` - Update user (Admin only)
  - POST `/<id>/disable` - Disable user
  - POST `/<id>/enable` - Enable user
  - POST `/sync-ldap` - Sync from AD

- `/api/chat/*` - Chat system
  - GET `/channels` - List channels
  - POST `/channels` - Create channel
  - GET `/channels/<id>/messages` - Get messages
  - POST `/channels/<id>/join` - Join channel
  - POST `/channels/<id>/leave` - Leave channel
  - GET `/channels/<id>/members` - Get members

- `/api/tasks/*` - Task planning
  - GET/POST `/` - List/create tasks
  - GET/PUT/DELETE `/<id>` - Task CRUD
  - GET `/calendar/<range>` - Calendar view

### WebSocket Events (`app/websocket/events.py`)
- `connect` - User connects to real-time service
- `disconnect` - User disconnects
- `join_channel` - Join chat channel
- `leave_channel` - Leave chat channel
- `send_message` - Send chat message
- `typing` - Broadcasting typing indicator
- `stop_typing` - Broadcasting stop typing
- `ticket_update` - Broadcast ticket updates
- `notification` - Send notifications to users
- `get_online_users` - Get list of online users

## Database Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts and profiles |
| `tickets` | Support tickets |
| `ticket_comments` | Comments/replies on tickets |
| `attachments` | File uploads to tickets |
| `chat_channels` | Text channels |
| `chat_channel_members` | Channel membership |
| `chat_messages` | Real-time chat messages |
| `tasks` | Calendar tasks |
| `audit_logs` | Action tracking |
| `sla_policies` | Service level agreements |

## Running the Application

### Development
```bash
python backend/app.py
# Runs on http://localhost:5000
```

### Production with Docker
```bash
docker-compose up -d
# Database: localhost:5432
# Redis: localhost:6379
# Backend: http://localhost:5000
# Nginx: http://localhost:80
```

### Database Setup
```bash
python backend/init_db.py           # Initialize database
python backend/init_db.py --reset   # Reset database (warning: deletes data)
```

## Environment Configuration

See `.env.example` for all available options. Key variables:

```
DATABASE_URL=postgresql://user:pass@host:5432/itsupport_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=<random-secret-key>
LDAP_SERVER=ldap://ad.company.com
LDAP_BASE_DN=dc=company,dc=com
SMTP_HOST=mail.company.com
```

## Next Steps

1. **Install Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your settings
   ```

3. **Initialize Database**
   ```bash
   python backend/init_db.py
   ```

4. **Run Application**
   ```bash
   python backend/app.py
   ```

5. **Build Frontend** (Vue.js/React - separate project or frontend/ folder)

6. **Deploy to Proxmox** (see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md))

## Support & Documentation

- **API Documentation**: [See API_REFERENCE.md](docs/API_REFERENCE.md)
- **Database Schema**: [See DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)
- **Security Guide**: [See SECURITY.md](docs/SECURITY.md)
- **Deployment**: [See DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Troubleshooting**: [See TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

**Project Version:** 2.0.0  
**Python Version:** 3.11+  
**Database:** PostgreSQL 12+  
**Framework:** Flask 3.1.2
