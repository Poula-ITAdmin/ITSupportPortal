#!/bin/bash
# Quick Start Script for IT Support Portal Backend
# Run this script to set up and start the development environment

set -e

echo "🚀 IT Support Portal - Quick Start Setup"
echo "========================================"
echo ""

# Select Python interpreter (prefer python3.11 when available)
echo "✓ Locating Python interpreter..."
if command -v python3.11 >/dev/null 2>&1; then
    PYTHON_BIN=python3.11
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
else
    echo "  ❌ No python3 interpreter found on PATH"
    exit 1
fi
PYTHON_VERSION=$($PYTHON_BIN -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if $PYTHON_BIN -c 'import sys; exit(0 if sys.version_info >= (3,11) else 1)'; then
    echo "  ✅ Python $PYTHON_VERSION found (3.11+) using $PYTHON_BIN"
else
    echo "  ❌ Python 3.11+ required (found $PYTHON_VERSION)"
    exit 1
fi

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist (use `env` to match existing conventions)
if [ ! -d "env" ]; then
    echo ""
    echo "✓ Creating Python virtual environment (backend/env) using $PYTHON_BIN..."
    $PYTHON_BIN -m venv env
    echo "  ✅ Virtual environment created"
else
    echo "  ✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source env/bin/activate
echo "  ✅ Virtual environment activated"

# Install dependencies
echo ""
echo "✓ Upgrading packaging tools and installing Python dependencies..."
python -m pip install --upgrade pip setuptools wheel
if python -m pip install -q -r requirements.txt; then
    echo "  ✅ Dependencies installed"
else
    echo "  ❌ pip failed to install some packages."
    echo "  Common causes:"
    echo "    - Building 'psycopg2' requires system package 'libpq-dev' (Debian/Ubuntu)."
    echo "    - Some wheels may not yet be available for newer Python versions (e.g. Python 3.13)."
    echo "  Fix options:" 
    echo "    1) Install system build deps (Debian/Ubuntu):"
    echo "       sudo apt update && sudo apt install -y libpq-dev build-essential python3-dev"
    echo "    2) Install or use Python 3.11 for the virtualenv if available."
    echo "       sudo apt install -y python3.11 python3.11-venv && re-run this script"
    echo "    3) Use Docker: docker-compose up -d to avoid local build issues."
    echo "  After fixing, re-run this script to retry."
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "✓ Creating .env file from template..."
    cp .env.example .env
    echo "  ⚠️  Edit .env with your configuration:"
    echo "     - LDAP_SERVER, LDAP_PORT, LDAP_BASE_DN"
    echo "     - DATABASE_URL (PostgreSQL connection)"
    echo "     - REDIS_URL"
    echo "     - SMTP settings"
    echo ""
    read -p "Press Enter to continue (or Ctrl+C to edit .env first)..."
fi

# Initialize database
echo ""
echo "✓ Initializing database..."
python init_db.py
echo "  ✅ Database initialized"

# Display summary
echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Summary:"
echo "   - Python environment: $(python --version)"
echo "   - Package count: $(pip list | wc -l) packages installed"
echo "   - Database: Ready"
echo ""
echo "🚀 Starting application..."
echo ""
echo "   App URL: http://localhost:5000"
echo "   API Base: http://localhost:5000/api"
echo ""
echo "📋 Quick API Test Commands:"
echo ""
echo "   # Login (default admin user)"
echo "   curl -X POST http://localhost:5000/api/auth/login \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"username\":\"admin\",\"password\":\"admin123\"}'"
echo ""
echo "   # Get current user"
echo "   curl http://localhost:5000/api/auth/me \\"
echo "     -H 'Authorization: Bearer <your-jwt-token>'"
echo ""
echo "   # Health check"
echo "   curl http://localhost:5000/api/health"
echo ""
echo "📚 Documentation:"
echo "   - README_v2.md - Feature overview"
echo "   - DEPLOYMENT_GUIDE.md - Proxmox deployment"
echo "   - PROJECT_STRUCTURE.md - File organization"
echo "   - IMPLEMENTATION_SUMMARY.md - What's built"
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Change default admin password (admin123) immediately!"
echo "   2. Configure LDAP settings in .env"
echo "   3. Set up PostgreSQL and Redis"
echo "   4. Change JWT_SECRET_KEY in production"
echo ""

# Start the application
python app.py
