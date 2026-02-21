# IT Support Portal - Proxmox Deployment Guide

## 📋 Architecture Overview

The ITSupportPortal is designed for deployment on Proxmox with the following infrastructure:

```
┌─────────────────────────────────────────────────────────┐
│                    Proxmox Hypervisor                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │   LXC Container  │  │   LXC Container  │           │
│  │  PostgreSQL DB   │  │    Redis Cache   │           │
│  │  8GB RAM, 4 CPU  │  │  4GB RAM, 2 CPU  │           │
│  └──────────────────┘  └──────────────────┘           │
│                                                         │
│  ┌──────────────────────────────┐                      │
│  │         VM Instance          │                      │
│  │   Flask Backend + Celery     │                      │
│  │   8GB RAM, 4 CPU, 20GB SSD   │                      │
│  │   Debian 12                  │                      │
│  │   Python 3.11                │                      │
│  └──────────────────────────────┘                      │
│                                                         │
│  ┌──────────────────┐                                  │
│  │  LXC Container   │                                  │
│  │  Nginx Reverse   │                                  │
│  │     Proxy        │                                  │
│  │  4GB RAM, 2 CPU  │                                  │
│  └──────────────────┘                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
        │                          ↕
        │                 Active Directory
        │                 (LDAP/LDAPS)
```

---

## 1️⃣ Prerequisites

- **Proxmox VE 7.0+** with cluster configured
- **DNS** pointing to your infrastructure
- **SSL Certificate** (Let's Encrypt recommended)
- **Active Directory** with LDAP enabled
- **Network connectivity** from Proxmox to AD controllers
- **Minimum 20GB** free disk space

---

## 2️⃣ Step-by-Step Deployment

### **Step 1: Create VM for Backend**

1. In Proxmox Console → Create VM
2. **General:**
   - Name: `itsupport-backend`
   - VM ID: 200
   
3. **OS:** Debian 12 (Linux)

4. **Hardware:**
   - CPU: 4 cores
   - Memory: 8GB
   - Disk: 20GB (SSD preferred)
   - Network: Bridged to your network

5. **Start VM and Install OS**

---

### **Step 2: Create LXC for PostgreSQL**

1. Create LXC Container
2. **Configuration:**
   - Name: `itsupport-db`
   - CT ID: 100
   - OS: Debian 12

3. **Resources:**
   - CPU: 4 cores
   - Memory: 8GB
   - Storage: 30GB (fast SSD)

4. **Install PostgreSQL:**

```bash
apt-get update && apt-get upgrade -y
apt-get install -y postgresql postgresql-contrib

# Start and enable
systemctl enable postgresql
systemctl start postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE USER itsupport WITH PASSWORD 'itsupport';
CREATE DATABASE itsupport_db OWNER itsupport;
ALTER ROLE itsupport SET client_encoding TO 'utf8';
ALTER ROLE itsupport SET default_transaction_isolation TO 'read committed';
ALTER ROLE itsupport SET default_transaction_deferrable TO on;
ALTER ROLE itsupport SET default_transaction_level TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE itsupport_db TO itsupport;
\q
EOF

# Configure PostgreSQL for network access
# Edit /etc/postgresql/15/main/postgresql.conf
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/15/main/postgresql.conf

# Edit /etc/postgresql/15/main/pg_hba.conf and add:
echo "host    itsupport_db    itsupport    <BACKEND_IP>/32    md5" >> /etc/postgresql/15/main/pg_hba.conf

# Restart PostgreSQL
systemctl restart postgresql
```

---

### **Step 3: Create LXC for Redis**

1. Create LXC Container
2. **Configuration:**
   - Name: `itsupport-redis`
   - CT ID: 101
   - OS: Debian 12

3. **Resources:**
   - CPU: 2 cores
   - Memory: 4GB
   - Storage: 10GB

4. **Install Redis:**

```bash
apt-get update && apt-get upgrade -y
apt-get install -y redis-server

# Edit /etc/redis/redis.conf
sed -i 's/bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf
sed -i 's/# requirepass foobared/requirepass itsupport123/g' /etc/redis/redis.conf

# Start and enable
systemctl enable redis-server
systemctl start redis-server

# Test
redis-cli ping
```

---

### **Step 4: Setup Backend VM**

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Python and dependencies
apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    supervisor \
    postgresql-client \
    ldap-utils

# Create app directory
mkdir -p /opt/itsupport
cd /opt/itsupport

# Clone or copy your repository
git clone <your-repo-url> .
# OR copy files from your development machine

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r backend/requirements.txt

# Create .env file with production settings
cat > backend/.env << EOF
FLASK_ENV=production
DATABASE_URL=postgresql://itsupport:itsupport@<DB_IP>:5432/itsupport_db
REDIS_URL=redis://<REDIS_IP>:6379/0
JWT_SECRET_KEY=$(openssl rand -hex 32)
LDAP_SERVER=ldap://<AD_CONTROLLER>.company.com
LDAP_PORT=389
LDAP_BASE_DN=dc=company,dc=com
LDAP_BIND_DN=CN=itsupport_service,OU=Service Accounts,DC=company,DC=com
LDAP_BIND_PASSWORD=your-service-account-password
LDAP_USER_SEARCH_BASE=OU=Users,DC=company,DC=com
LDAP_GROUP_SEARCH_BASE=OU=Groups,DC=company,DC=com
SMTP_HOST=mail.company.com
SMTP_PORT=587
SMTP_USER=itsupport@company.com
SMTP_PASSWORD=your-password
SMTP_FROM="IT Support <itsupport@company.com>"
EOF

# Initialize database
source venv/bin/activate
export FLASK_APP=backend/app.py
flask db upgrade  # Or run init script if using sqlalchemy-migration

# Test the app
python backend/app.py  # Should start on port 5000
```

---

### **Step 5: Create Supervisor Config**

Create `/etc/supervisor/conf.d/itsupport.conf`:

```ini
[program:itsupport-flask]
directory=/opt/itsupport
command=/opt/itsupport/venv/bin/python /opt/itsupport/backend/app.py
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/itsupport/flask.log
environment=PATH="/opt/itsupport/venv/bin"

[program:itsupport-celery]
directory=/opt/itsupport
command=/opt/itsupport/venv/bin/celery -A backend.celery worker --loglevel=info
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/itsupport/celery.log
environment=PATH="/opt/itsupport/venv/bin"
```

```bash
mkdir -p /var/log/itsupport
chown www-data:www-data /var/log/itsupport

supervisorctl reread
supervisorctl update
supervisorctl start all
```

---

### **Step 6: Create LXC for Nginx**

1. Create LXC Container
2. **Name:** `itsupport-nginx`
3. **Resources:** 2 CPU, 4GB RAM, 10GB storage

4. **Install and Configure:**

```bash
apt-get update && apt-get upgrade -y
apt-get install -y nginx certbot python3-certbot-nginx

# Copy nginx.conf from project
cp nginx.conf /etc/nginx/nginx.conf

# Get SSL certificate
certbot certonly --standalone -d itsupport.company.com

# Enable nginx
systemctl enable nginx
systemctl start nginx

# Auto-renew certificates
systemctl enable certbot.timer
```

---

## 3️⃣ Network Configuration

### **Internal Networking (on Proxmox bridge)**

```
Backend VM (200):     192.168.1.200
PostgreSQL (100):     192.168.1.100
Redis (101):          192.168.1.101
Nginx (102):          192.168.1.102
```

### **Firewall Rules**

Allow these connections:

- **Backend → PostgreSQL:** TCP 5432
- **Backend → Redis:** TCP 6379
- **Nginx → Backend:** TCP 5000
- **Nginx → External:** TCP 80, 443
- **Backend → AD/LDAP:** TCP 389 (or 636 for LDAPS)

---

## 4️⃣ Active Directory Integration

### **Create Service Account in AD:**

```powershell
# PowerShell on Domain Controller
New-ADUser -Name "itsupport_service" `
    -UserPrincipalName "itsupport_service@company.com" `
    -Path "OU=Service Accounts,DC=company,DC=com" `
    -AccountPassword (ConvertTo-SecureString -AsPlainText "ComplexPassword123!" -Force) `
    -Enabled $true `
    -PasswordNeverExpires $false
```

### **Configure LDAP Groups:**

Create these AD groups for role mapping:

- `IT_Level1` → IT Support Staff
- `IT_Level2` → Advanced IT Support
- `System_Admins` → System Administrators
- `Managers` → Managers/Supervisors

---

## 5️⃣ Initial Configuration

### **Create Admin User**

```bash
python3 << EOF
from backend.app import create_app
from backend.app.models import db, User, UserRole
import bcrypt

app, _ = create_app()
with app.app_context():
    # Create admin user
    password_hash = bcrypt.hashpw(b'initial-password', bcrypt.gensalt()).decode()
    admin = User(
        username='admin',
        email='admin@company.com',
        password_hash=password_hash,
        first_name='Admin',
        last_name='User',
        role=UserRole.ADMIN,
        is_active=True
    )
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user created with ID: {admin.id}")
EOF
```

### **Sync Users from LDAP**

```bash
curl -X POST http://localhost:5000/api/users/sync-ldap \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

---

## 6️⃣ Backup & Recovery

### **PostgreSQL Backup**

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/var/backups/itsupport"
mkdir -p $BACKUP_DIR

pg_dump -h <DB_IP> -U itsupport itsupport_db | \
  gzip > $BACKUP_DIR/itsupport_db_$(date +%Y%m%d_%H%M%S).sql.gz

# Keep only 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

### **Proxmox LXC Snapshot**

```bash
# Snapshot PostgreSQL container
pvesh create /nodes/pve/lxc/100/snapshots -snapname backup-$(date +%Y%m%d)
```

---

## 7️⃣ Monitoring & Logging

### **Install Monitoring**

```bash
apt-get install -y prometheus node-exporter grafana-server
```

### **Logs**

- **Flask:** `/var/log/itsupport/flask.log`
- **Celery:** `/var/log/itsupport/celery.log`
- **Nginx:** `/var/log/nginx/access.log`
- **PostgreSQL:** `/var/log/postgresql/postgresql.log`

### **Health Checks**

```bash
# API Health
curl http://localhost:5000/api/health

# Database
psql -h <DB_IP> -U itsupport itsupport_db -c "SELECT 1"

# Redis
redis-cli -h <REDIS_IP> ping
```

---

## 8️⃣ Scaling Considerations

**For production with 500+ users:**

1. **Horizontal Scaling:**
   - Deploy multiple backend instances
   - Use load balancer (HAProxy)
   - Scale Celery workers

2. **Database:**
   - Enable replication/failover
   - Increase connection pool

3. **Caching:**
   - Redis cluster for redundancy
   - Cache frequently accessed data

4. **Monitoring:**
   - Setup alerts for CPU, memory, disk
   - Monitor LDAP query times
   - Track API response times

---

## 🔒 Security Best Practices

- [ ] Change all default passwords
- [ ] Enable LDAPS (SSL/TLS) for LDAP connections
- [ ] Use strong JWT secret key
- [ ] Configure firewall rules
- [ ] Enable SELinux/AppArmor if needed
- [ ] Regular security updates
- [ ] Implement automated backups
- [ ] Use SSH keys for server access
- [ ] Enable audit logging
- [ ] Regular password rotation

---

## 📊 Resource Summary

| Component | Request | Allocation |
|-----------|---------|-----------|
| PostgreSQL LXC | 8GB RAM, 4 CPU | ✅ |
| Redis LXC | 4GB RAM, 2 CPU | ✅ |
| Flask VM | 8GB RAM, 4 CPU | ✅ |
| Nginx LXC | 4GB RAM, 2 CPU | ✅ |
| **TOTAL** | **24GB RAM, 12 CPU** | ✅ |

---

## 🆘 Troubleshooting

### **PostgreSQL Connection Issues**

```bash
# Test connection
psql -h <DB_IP> -U itsupport -d itsupport_db

# Check pg_hba.conf
grep <BACKEND_IP> /etc/postgresql/15/main/pg_hba.conf
```

### **LDAP Connection Issues**

```bash
# Test LDAP connection
ldapsearch -H ldap://<AD_controller>:389 \
  -D "CN=itsupport_service,OU=Service Accounts,DC=company,DC=com" \
  -w "password" \
  -b "DC=company,DC=com" \
  "(objectClass=user)" | head -20
```

### **Redis Connection Issues**

```bash
# Test Redis
redis-cli -h <REDIS_IP> ping
redis-cli -h <REDIS_IP> INFO
```

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL on Linux](https://www.postgresql.org/docs/15/sql.html)
- [Proxmox Documentation](https://pve.proxmox.com/wiki/Main_Page)
- [LDAP/Active Directory Integration](https://ldapwiki.com/)
- [Nginx Configuration](https://nginx.org/en/docs/)

---

**Deployment Date:** [Date]
**Last Updated:** [Date]
**Maintained By:** [Your Name/Team]
