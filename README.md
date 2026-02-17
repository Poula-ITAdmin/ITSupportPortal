# IT Support Portal

A simple, clean, bilingual (English/Arabic) IT ticketing system for employees to report IT issues, with automatic task assignment to team members, management dashboard, and Microsoft Teams Planner integration.

---

## 📁 Project Structure

```
ITSupportPortal/
├── frontend/                    # Web User Interface
│   ├── index.html              # Main HTML page (Single Page App)
│   ├── css/styles.css          # Responsive styling with RTL support
│   └── js/app.js              # Frontend JavaScript logic
│
├── backend/                    # Server-side API (Python Flask)
│   ├── app.py                  # Main Flask application
│   ├── .env                   # Environment configuration
│   ├── env/                   # Python virtual environment
│   └── src/                   # Node.js version (alternative)
│
└── data/
    └── itsupport.db           # SQLite database
```

---

## 🛠 Technologies Used

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | HTML5, CSS3, JavaScript | User interface |
| **Backend** | Python Flask | REST API server |
| **Database** | SQLite | Local data storage |
| **Authentication** | JWT (JSON Web Tokens) | Secure user sessions |
| **Password Security** | bcrypt | Encrypted passwords |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+

### Installation

```bash
# Navigate to project
cd ITSupportPortal/backend

# Create virtual environment
python3 -m venv env

# Activate environment
source env/bin/activate  # Linux/Mac
# OR: env\Scripts\activate  # Windows

# Install dependencies
pip install flask flask-cors pyjwt bcrypt
```

### Run the Server

```bash
python app.py
```

The application will be available at: **http://localhost:3000**

---

## 👥 User Roles & Access

| Role | Email | Access |
|------|-------|--------|
| **Admin** | admin@company.com | Full access + Admin Panel |
| **IT Staff** | john@company.com | Dashboard (Devices) |
| **IT Staff** | poula@company.com | Dashboard (Personal Device) |
| **IT Staff** | maria@company.com | Dashboard (Medical Device) |
| **IT Staff** | software@company.com | Dashboard (Software) |
| **IT Staff** | access@company.com | Dashboard (Access) |
| **IT Staff** | maintenance@company.com | Dashboard (Maintenance) |
| **Employee** | employee@company.com | My Tickets only |

**Default Password:** `admin123` for admin, `it123456` for IT staff, `emp123456` for employees

---

## 📋 Features

### For Employees
- Simple 6-category ticket submission
- Dynamic forms based on category
- Department & sub-department selection
- Track own tickets
- Email notifications (placeholder)

### For IT Staff
- Category-specific dashboard
- Update ticket status
- Add notes
- View assignment history

### For Admin
- Full ticket management
- Reassign tickets to any IT staff
- View statistics & workload
- Filter all tickets

### Categories
1. **Devices** - Laptop, printer, monitor, network issues
2. **Personal Device** - BYOD issues
3. **Medical Device** - Medical equipment
4. **Software Issue** - ERP, Windows, application errors
5. **Access / Accounts** - Password reset, permissions
6. **Maintenance & Repairs** - Equipment servicing

### Departments
- **Hospital**: Accounting, Nursing, Pharmacy, Medical Records, Radiology, Laboratory, Emergency, Surgery, Pediatrics, ICU, Cardiology, Orthopedics, Gynecology, Physiotherapy, Dietary, Housekeeping, Maintenance, IT
- **Mission**: Administration, Finance, HR, Programs, Outreach, Community Health, Training, Logistics, Procurement, Monitoring & Evaluation

---

## 🌐 Bilingual Support

The portal supports **English** and **Arabic** with:
- Full UI translation
- RTL (right-to-left) layout for Arabic
- Dynamic sub-department lists in both languages

Toggle language using the button in the header.

---

## 🔄 How It Works

```
User Browser (Frontend)
        ↓ HTTP Requests
Flask Server (app.py)
        ↓
SQLite Database
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | User login |
| POST | /api/auth/register | User registration |
| GET | /api/tickets | Get tickets |
| POST | /api/tickets | Create ticket |
| PUT | /api/tickets/:id | Update ticket |
| GET | /api/tickets/stats/dashboard | Dashboard stats |
| GET | /api/users/it-members | IT staff list |
| GET | /api/admin/stats | Admin statistics |

---

## 📊 Database Schema

### users
- id, name, email, password, phone, department, role, created_at

### it_members
- id, user_id, category, max_tickets, is_backup

### tickets
- id, ticket_number, user_id, category, title, description, urgency, status, department, sub_department, phone, assigned_to, and category-specific fields

### ticket_logs
- id, ticket_id, user_id, action, description, created_at

---

## 🔧 Configuration

Edit `.env` file:
```env
PORT=3000
JWT_SECRET=your-secret-key
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASS=your-password
```

---

## 📝 License

MIT License
