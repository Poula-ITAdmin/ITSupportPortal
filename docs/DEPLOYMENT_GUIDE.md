# IT Support Portal - Deployment Guide

This guide explains common deployment options (Proxmox, Docker, and manual VM deployment). It is a copy of the deployment instructions prepared for documentation publication.

## Prerequisites

- Debian 12 / Ubuntu 22.04 recommended
- Python 3.11
- PostgreSQL 15
- Redis 6+
- Docker & Docker Compose (optional)

## Backend VM (manual)

1. Create VM (Debian 12)
2. Install system packages:

```bash
apt-get update && apt-get upgrade -y
apt-get install -y python3.11 python3-pip python3-venv git curl supervisor postgresql-client ldap-utils build-essential libpq-dev
```

3. Clone repository and install Python dependencies inside a virtualenv.

```bash
git clone <repo-url> /opt/itsupport
cd /opt/itsupport
python3.11 -m venv env
source env/bin/activate
pip install -r backend/requirements.txt
```

4. Configure `backend/.env` and set `DATABASE_URL` and `REDIS_URL`.

5. Start backend using Supervisor or systemd (example systemd unit files should be adapted per site).

## Docker Compose

Use `docker-compose.yml` to run the full stack with PostgreSQL and Redis.

```bash
docker-compose up -d
docker-compose exec backend python backend/init_db.py
```

## Proxmox Notes

For Proxmox deployments we recommend separate containers/VMs for PostgreSQL and Redis and a dedicated VM for the Flask backend.
