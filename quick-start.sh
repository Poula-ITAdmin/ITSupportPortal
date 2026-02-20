#!/bin/bash
# Quick Start Script for IT Support Portal Backend
# Run this script to set up and start the development environment

set -e

echo "🚀 IT Support Portal - Quick Start Setup"
echo "========================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if python3 -c 'import sys; exit(0 if sys.version_info >= (3,11) else 1)'; then
    echo "  ✅ Python $PYTHON_VERSION found (3.11+)"
else
    echo "  ❌ Python 3.11+ required (found $PYTHON_VERSION)"
    exit 1
fi

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "✓ Creating Python virtual environment..."
    python3.11 -m venv venv
    echo "  ✅ Virtual environment created"
else
    echo "  ✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate
echo "  ✅ Virtual environment activated"

# Install dependencies
echo ""
echo "✓ Installing Python dependencies..."
pip install -q -r requirements.txt
echo "  ✅ Dependencies installed"

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
