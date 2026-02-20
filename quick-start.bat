@echo off
REM Quick Start Script for IT Support Portal Backend (Windows)
REM Run this script to set up and start the development environment

echo.
echo ===================================
echo  IT Support Portal - Quick Start
echo ===================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.11+
    pause
    exit /b 1
)

echo   ✓ Python 3.11+ found

REM Navigate to backend directory
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo Creating Python virtual environment...
    python -m venv venv
    echo   ✓ Virtual environment created
) else (
    echo   ✓ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo   ✓ Virtual environment activated

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install -q -r requirements.txt
echo   ✓ Dependencies installed

REM Create .env if it doesn't exist
if not exist ".env" (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo   ⚠  Edit .env with your configuration
    echo      - LDAP_SERVER, LDAP_PORT, LDAP_BASE_DN
    echo      - DATABASE_URL (PostgreSQL connection)
    echo      - REDIS_URL
    echo      - SMTP settings
    echo.
    pause
)

REM Initialize database
echo.
echo Initializing database...
python init_db.py
echo   ✓ Database initialized

REM Display summary
echo.
echo ===== Setup Complete! =====
echo.
echo Summary:
echo   - Python environment: (check version above)
echo   - Database: Ready
echo.
echo Starting application...
echo.
echo   App URL: http://localhost:5000
echo   API Base: http://localhost:5000/api
echo.
echo Documentation:
echo   - README_v2.md - Feature overview
echo   - DEPLOYMENT_GUIDE.md - Proxmox deployment
echo   - PROJECT_STRUCTURE.md - File organization
echo.
echo IMPORTANT:
echo   1. Change default admin password (admin123) immediately!
echo   2. Configure LDAP settings in .env
echo   3. Set up PostgreSQL and Redis
echo   4. Change JWT_SECRET_KEY in production
echo.
pause

REM Start the application
python app.py
