# 🚀 IT Support Portal v2.0

A complete enterprise-grade IT support ticketing system with real-time chat, calendar planning, LDAP integration, and comprehensive reporting.

> **Status:** Production Ready | **Version:** 2.0.0 | **License:** Proprietary

---

## ✨ Features

### 🎫 **Ticketing System**
- Create, assign, and track support tickets
- Dynamic forms based on ticket category
- Full ticket lifecycle: Open → Assigned → In-Progress → Waiting → Escalated → Resolved → Closed
- SLA tracking with automatic escalation
- Internal and external comments
- File attachments support
- Priority-based routing

### 🔐 **Active Directory Integration**
- Full LDAP/LDAPS authentication
- Automatic user synchronization from Active Directory
- Group-based role assignment
- Support for multiple user classes:
  - **Employees** - Create and manage tickets
  - **IT Level 1** - First-line support
  - **IT Level 2** - Advanced support
  - **Admins** - Full system access
  - **Managers** - Oversight and reporting

### 💬 **Real-Time Chat System**
- Department-based channels
- Ticket-based discussion channels
- WebSocket-powered real-time messaging
- Typing indicators and presence awareness
- File sharing capabilities
- Message reactions and threading
- Chat history and searchable logs

### 📅 **Calendar & Task Planner**
- Drag-and-drop task scheduling
- Team workload visualization
- Link tasks to tickets
- Daily, weekly, monthly views
- Color-coded categories
- Deadline reminders and alerts
- Export to PDF/CSV
- Integration with Google Calendar (optional)

### 📊 **Analytics & Reporting**
- Real-time dashboard with KPIs
- Ticket metrics by category, priority, status
- SLA compliance tracking
- Team performance analytics
- Department-wise statistics
- Custom report generation
- Export to CSV, PDF, Excel

### 🔒 **Security & Compliance**
- JWT-based authentication
- Role-based access control (RBAC)
- Comprehensive audit logging
- End-to-end encryption support
- Session management
- Password policies
- Failed login tracking

---

## 🏗 Architecture

### **Technology Stack**

```
Frontend:
├── Vue.js 3 / React (web)
├── PySide6 (desktop app)
└── WebSocket (real-time)

Backend:
├── Flask 3.1.2
├── Flask-SQLAlchemy (ORM)
├── Flask-JWT-Extended (auth)
├── Flask-SocketIO (WebSocket)
└── python-ldap (LDAP/AD)

Database:
├── PostgreSQL 15 (primary)
└── Redis 7 (caching & queue)

Deployment:
├── Docker & Docker Compose
├── Nginx (reverse proxy)
└── Supervisor (process management)
```

### **Database Schema**

**Key Models:**
- `User` - User accounts with roles and permissions
- `Ticket` - Support tickets with full lifecycle
- `ChatChannel` - Communication channels
- `ChatMessage` - Real-time messages
- `Task` - Calendar tasks and planning
- `AuditLog` - Compliance and action tracking
- `SLAPolicy` - Service level agreements

---

## 📦 Installation

### **Prerequisites**

- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- Active Directory (for LDAP integration)
- Docker & Docker Compose (optional)

### **Local Development Setup**

```bash
# Clone repository
git clone https://github.com/yourorg/itsupport-portal.git
cd ITSupportPortal

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Create .env file
cp backend/.env.example backend/.env
# Edit .env with your configuration

# Initialize database
export FLASK_APP=backend/app.py
flask db upgrade

# Run development server
python backend/app.py
```

The application will start on `http://localhost:5000`

### **Docker Deployment**

```bash
# Build and start all services
docker-compose up -d

# Initialize database
docker-compose exec backend flask db upgrade

# View logs
docker-compose logs -f backend
```

---

## 🔧 Configuration

### **Environment Variables** (`.env`)

```env
# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/itsupport_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret

# LDAP/Active Directory
LDAP_SERVER=ldap://ad.company.com
LDAP_PORT=389
LDAP_USE_SSL=false
LDAP_BASE_DN=dc=company,dc=com
LDAP_BIND_DN=CN=service_account,OU=Accounts,DC=company,DC=com
LDAP_BIND_PASSWORD=password

# Email (SMTP)
SMTP_HOST=mail.company.com
SMTP_PORT=587
SMTP_USER=itsupport@company.com
SMTP_PASSWORD=password

# Upload limits
MAX_UPLOAD_SIZE=52428800  # 50MB

# CORS
CORS_ORIGINS=http://localhost:3000,https://itsupport.company.com
```

---

## 📚 API Documentation

### **Authentication**

```bash
# Login
POST /api/auth/login
Content-Type: application/json

{
  "username": "user@company.com",
  "password": "password"
}

# Response
{
  "access_token": "eyJ0eX...",
  "refresh_token": "eyJ0eX...",
  "user": { ... }
}
```

### **Tickets**

```bash
# Create ticket
POST /api/tickets
Authorization: Bearer <token>

# Get all tickets
GET /api/tickets?page=1&limit=20&status=open

# Get ticket details
GET /api/tickets/<ticket_id>

# Update ticket
PUT /api/tickets/<ticket_id>

# Assign ticket
POST /api/tickets/<ticket_id>/assign
{ "assigned_to": "user_id" }

# Add comment
POST /api/tickets/<ticket_id>/comment
{ "content": "...", "is_internal": false }

# Upload attachment
POST /api/tickets/<ticket_id>/upload (multipart/form-data)
```

### **Chat**

```bash
# List channels
GET /api/chat/channels

# Create channel
POST /api/chat/channels
{ "name": "...", "channel_type": "department" }

# Get messages
GET /api/chat/channels/<channel_id>/messages

# Join channel
POST /api/chat/channels/<channel_id>/join

# Leave channel
POST /api/chat/channels/<channel_id>/leave
```

### **Tasks**

```bash
# Create task
POST /api/tasks
{ "title": "...", "start_date": "...", "due_date": "..." }

# Get tasks
GET /api/tasks?assigned_to=user_id&status=pending

# Update task
PUT /api/tasks/<task_id>

# Delete task
DELETE /api/tasks/<task_id>

# Calendar view
GET /api/tasks/calendar/month
```

### **Users**

```bash
# List users
GET /api/users?role=it_level1&page=1

# Get user details
GET /api/users/<user_id>

# Update user
PUT /api/users/<user_id>
{ "role": "it_level2", "department": "..." }

# Sync LDAP users
POST /api/users/sync-ldap
```

**Full API documentation:** [API_REFERENCE.md](docs/API_REFERENCE.md)

---

## 🚀 Usage

### **As an IT Team Member**

1. Login with your Active Directory credentials
2. Dashboard shows assigned tickets and workload
3. Join department chat channels
4. Create and assign tasks in calendar
5. Track SLA compliance

### **As an Employee**

1. Create support ticket with description
2. Attach files if needed
3. Receive real-time updates in ticket channel
4. Chat with assigned IT team member
5. Close ticket when resolved

### **As an Administrator**

1. Manage users and roles
2. View system-wide analytics
3. Configure SLA policies
4. Sync users from Active Directory
5. Audit all system actions

---

## 📊 Dashboard & Reporting

### **Features**

- **Real-time Metrics:**
  - Open tickets count
  - Average resolution time
  - SLA compliance percentage
  - Team utilization

- **Reports:**
  - Ticket trending (daily, weekly, monthly)
  - Department performance
  - Agent productivity
  - Category breakdown
  - Custom date range filters

- **Exports:**
  - CSV for spreadsheet analysis
  - PDF for management reports
  - Excel with charts and graphs

---

## 🔌 WebSocket Events

```javascript
// Connect
const socket = io("http://localhost:5000", {
  auth: { token: "jwt_token_here" }
});

// Join channel
socket.emit('join_channel', { channel_id: 'ch_123' });

// Send message
socket.emit('send_message', {
  channel_id: 'ch_123',
  content: 'Message here'
});

// Listen for messages
socket.on('new_message', (data) => {
  console.log(data.content);
});

// Receive notifications
socket.on('notification', (data) => {
  console.log(data.type, data.content);
});
```

---

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

# Run with coverage
pytest --cov=app tests/

# Test specific module
pytest tests/unit/test_tickets.py
```

---

## 📈 Performance Optimization

- **Database:** Indexed queries, connection pooling
- **Redis:** Caching for frequently accessed data
- **Nginx:** Gzip compression, static file caching
- **WebSocket:** Message queue for scaling
- **Frontend:** Code splitting, lazy loading

---

## 🔐 Security Best Practices

✅ **Implemented:**
- LDAP/LDAPS authentication
- JWT tokens with expiration
- Role-based access control
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- CORS security headers
- Rate limiting
- Audit logging
- Password hashing (bcrypt)

⚠️ **Recommended:**
- Enable HTTPS/TLS everywhere
- Use strong JWT secrets
- Regular security audits
- Keep dependencies updated
- Monitor access logs
- Implement 2FA (optional)

---

## 📞 Support & Contributing

- **Issues:** [GitHub Issues](https://github.com/yourorg/itsupport-portal/issues)
- **Documentation:** [Full Docs](docs/)
- **Email:** support@company.com
- **Slack:** #itsupport-portal

### **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

---

## 📋 Roadmap

- [ ] Mobile app (React Native)
- [ ] AI-powered ticket categorization
- [ ] Integration with Slack/Teams
- [ ] Knowledge base integration
- [ ] Video call support
- [ ] Predictive analytics
- [ ] Multi-language support
- [ ] Custom workflows
- [ ] API rate limiting dashboard
- [ ] Advanced RBAC editor

---

## 📄 License

Proprietary - All rights reserved

---

## 🙏 Acknowledgments

Built with:
- Flask & Python community
- PostgreSQL developers
- Redis team
- The open-source community

---

## 📚 Additional Resources

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Security Policy](docs/SECURITY.md)
- [Changelog](CHANGELOG.md)

---

**Version:** 2.0.0  
**Last Updated:** February 2026  
**Maintainer:** IT Support Team
