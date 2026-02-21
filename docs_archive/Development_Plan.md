Below is a **clean, complete, production-grade prompt** you can give to an **AI coding agent** to rebuild your **ITSupportPortal** with the exact features you want.
I also added an **infra plan** for how you can deploy everything on your **Proxmox** setup.

---

# ✅ **Prompt for AI Coding Agent — ITSupportPortal Remodelling**

**Goal:**
Rebuild and remodel the *ITSupportPortal* to be extremely fast, efficient, modular, secure, and easy to use.
Make all components in **Python**, with:

* **Backend:** Django (preferred) or Flask
* **Frontend / Desktop Client (optional):** PySide6
* **Database:** MariaDB or PostgreSQL
* **Real-time / WebSocket:** Django Channels or Flask-SocketIO

---

## **🔥 Functional Requirements**

### **1. User Authentication (Active Directory LDAP)**

Implement full LDAP authentication and user provisioning:

* Integrate with **Active Directory** via LDAP or LDAPS
* Import/display AD attributes: username, email, department, job title
* Two user classes:

  * **Normal Employees** → create tickets
  * **IT Team Members** → resolve tickets
* Privilege system for IT roles:

  * Assign tasks to other members
  * Change category
  * Change ticket priority
  * Add internal notes
  * Reassign departments
  * Close/resolve tickets
* Support group-based permissions (AD groups):

  * IT Level 1
  * IT Level 2
  * System Admin
  * Manager/Supervisor
* Log every action for auditing

---

### **2. Ticketing System Enhancements** (Already exists—just improve the flow)

Improve the logic and workflow:

* Cleaner UI for ticket creation
* Dynamic forms based on category
* Smart routing (department → responsible IT group)
* Support attachments
* New ticket lifecycle:

  * **Open → Assigned → In-Progress → Waiting User → Escalated → Closed**
* SLA rules:

  * Auto-escalate if overdue
  * Auto-remind
* Dashboard for:

  * Pending tickets
  * Priority alerts
  * SLA violations
  * Assigned workload per team member
* Robust reporting system:

  * Export CSV/PDF
  * Filters by department, user, category, SLA, date range

---

### **3. Real-Time Chat System With Channels**

Create a built-in communication tool similar to Slack/Teams:

* Use **WebSockets**
* Department-based channels:

  * IT
  * HR
  * Finance
  * Operations
  * Logistics
  * Custom
* Ticket-based channels (“room per ticket”)
* Features:

  * Presence (who is online)
  * Typing indicator
  * File sharing
  * Push notifications or email notifications
  * Chat logs saved per channel
  * Searchable messages

---

### **4. Calendar Planner + Scheduling System**

A powerful task calendar for IT teams:

* Drag-and-drop tasks
* Assign tasks linked to tickets
* Departments or members can plan weekly/monthly
* Color-coded categories
* Daily/weekly/monthly views
* Reminder notifications
* Export PDF and CSV
* API to sync with:

  * Google Calendar
  * Microsoft Outlook (optional)
* Dashboard for overdue tasks and deadlines

---

### **5. Architecture & Code Structure Expectations**

* Use **modular architecture** (clean, layered services)
* Use **REST API** or GraphQL
* DRF if using Django
* Use WebSockets for real-time features
* Use background jobs with:

  * Celery + Redis or
  * Dramatiq
* Use JWT or Session security
* Logging + monitoring middleware
* Unit tests + integration tests
* Fully dockerized (optional)

---

# 🏗 **Infrastructure Plan for Proxmox Deployment**

Here is how you should structure the infra using Proxmox:

---

## **1️⃣ LXC Container – Database Layer**

**LXC 1: DB Server**

* OS: Debian 12
* Software: MariaDB **or** PostgreSQL
* RAM: 8GB
* CPU: 4 cores
* Storage: SSD (fast I/O)
* Backups via Proxmox scheduled snapshots

---

## **2️⃣ VM – Application Backend**

**VM 1: Django/Flask Backend**

* OS: Debian 12
* Python 3.11
* Services:

  * Django backend
  * Celery worker
  * Redis (or put Redis in another container)
* Expose only via reverse proxy
* RAM: 8GB
* CPU: 4 cores

---

## **3️⃣ LXC Container – WebSocket + Real-Time**

Optional or combined with backend:

**LXC 2: WebSockets / Channels**

* Django Channels + Redis
  or
* Flask-SocketIO
* RAM: 4GB
* CPU: 2 cores

---

## **4️⃣ VM – Frontend / Desktop App Distribution (Optional)**

If using PySide6:

**VM 2: Frontend Build Server**

* Build PySide6 app bundles for Linux & Windows
* Optional: host an auto-updater

---

## **5️⃣ Reverse Proxy / Load Balancer**

**LXC 3: Nginx or Traefik**

* Terminate HTTPS
* Route traffic to backend + websocket
* Enable caching for static content
* Let’s Encrypt certs

---

## **6️⃣ Active Directory Integration**

Make sure your backend VM:

* Can reach domain controllers
* Uses correct DNS
* Has correct time sync (NTP)
* Uses LDAPS whenever possible

---

# 🧠 **Complete Prompt to Give the Agent**

Copy/paste this:

---

**PROMPT START**

I need you to completely rebuild and remodel my ITSupportPortal with the following features and technologies:

### **Core Requirements**

1. Implement full **Active Directory LDAP authentication** with two user classes:

   * Standard employees (create tickets)
   * IT team (resolve tickets)
     Implement granular privileges: assign tasks, change priority, reassign categories, manage deadlines, and plan tasks.

2. Enhance the existing **ticketing system workflow**:

   * Clean UI for ticket creation
   * Dynamic forms per category
   * Ticket lifecycle (Open → Assigned → In-Progress → Waiting → Escalated → Closed)
   * SLA automation, reminders, escalations
   * Reporting with exportable CSV/PDF

3. Build a **real-time chat system**:

   * Channels per department
   * Channels per ticket
   * WebSockets for real-time messaging
   * File upload, presence, and typing indication

4. Add a **calendar task planner**:

   * Drag-and-drop scheduling
   * Assignment per team member
   * Link tasks to tickets
   * Daily/weekly/monthly views
   * Exportable reports
   * Alerts & reminders

### **Technology Stack**

* Backend: Django (preferred) or Flask
* Frontend: PySide6 (optional desktop client)
* Database: MariaDB or PostgreSQL
* Realtime: Django Channels or Flask-SocketIO
* Background jobs: Celery + Redis
* REST API or GraphQL
* JWT/session authentication
* Fully modular architecture
* Logging, monitoring, analytics, audit logs
* Docker support

### **Infrastructure Requirements**

Prepare the project to run on my Proxmox environment:

* LXC for database
* VM for backend
* Dedicated container for WebSockets if required
* Nginx/Traefik reverse proxy
* LDAP integration with Active Directory
* Fast performance and clean code structure

**PROMPT END**

---


✅ Database schema
✅ Full system architecture diagram
✅ Directory structure for the entire codebase
✅ API endpoints list
✅ UI wireframes
✅ Deployment plan for Proxmox
✅ Templates for the IT policies / workflow

