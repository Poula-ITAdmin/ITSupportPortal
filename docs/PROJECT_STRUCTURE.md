# Project Structure

```
ITSupportPortal/
├── README.md                          # Main README (v2)
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
├── docs/                             # Documentation (this folder)
│   ├── index.md                      # Documentation index
│   └── (other docs)
│
└── data/                             # Data directory
    └── uploads/                      # File uploads
```

## Key Files

- `.env` - Environment variables (database, LDAP, SMTP, JWT secrets)
- `config.py` - Flask configuration classes
- `requirements.txt` - Python package dependencies

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
