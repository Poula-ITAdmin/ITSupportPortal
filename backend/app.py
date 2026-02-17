from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import os
import uuid
from pathlib import Path
from functools import wraps
from datetime import datetime
from email.mime.text import MIMEText

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(BASE_DIR / 'data' / 'itsupport.db')

app = Flask(__name__, static_folder='../frontend')
CORS(app)
app.config['SECRET_KEY'] = 'itsupportportal2024secret'

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        department TEXT,
        role TEXT DEFAULT 'employee',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS it_members (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        category TEXT NOT NULL,
        max_tickets INTEGER DEFAULT 10,
        is_backup INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id TEXT PRIMARY KEY,
        ticket_number INTEGER UNIQUE,
        user_id TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        urgency TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Open',
        department TEXT,
        phone TEXT,
        assigned_to TEXT,
        device_type TEXT,
        asset_number TEXT,
        device_working TEXT,
        software_name TEXT,
        error_message TEXT,
        application_access TEXT,
        current_role TEXT,
        required_permissions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        planner_task_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (assigned_to) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ticket_logs (
        id TEXT PRIMARY KEY,
        ticket_id TEXT NOT NULL,
        user_id TEXT,
        action TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    c.execute("SELECT id FROM users WHERE email = 'admin@company.com'")
    if not c.fetchone():
        admin_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users (id, name, email, password, role, department) VALUES (?, ?, ?, ?, ?, ?)",
                  (admin_id, 'Admin', 'admin@company.com', hashed, 'admin', 'IT'))
        
        it_members = [
            ('John Smith', 'john@company.com', 'Hardware'),
            ('Poula Khan', 'poula@company.com', 'Software'),
            ('Maria Garcia', 'maria@company.com', 'Access')
        ]
        
        for name, email, category in it_members:
            member_id = str(uuid.uuid4())
            user_id = str(uuid.uuid4())
            hashed = bcrypt.hashpw('it123456'.encode(), bcrypt.gensalt())
            c.execute("INSERT INTO users (id, name, email, password, role, department) VALUES (?, ?, ?, ?, ?, ?)",
                      (user_id, name, email, hashed, 'it_staff', 'IT'))
            c.execute("INSERT INTO it_members (id, user_id, category, max_tickets) VALUES (?, ?, ?, ?)",
                      (member_id, user_id, category, 15))
    
    conn.commit()
    conn.close()
    print("Database initialized!")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user = data
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def assign_ticket(category):
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT im.*, u.id as user_id, u.name
                FROM it_members im
                JOIN users u ON im.user_id = u.id
                WHERE im.category = ? AND im.is_backup = 0''', (category,))
    member = c.fetchone()
    
    if not member:
        c.execute('''SELECT im.*, u.id as user_id, u.name
                     FROM it_members im
                     JOIN users u ON im.user_id = u.id
                     WHERE im.is_backup = 1 LIMIT 1''')
        member = c.fetchone()
    
    if member:
        c.execute('''SELECT COUNT(*) as count FROM tickets 
                     WHERE assigned_to = ? AND status NOT IN ('Completed', 'Cancelled')''', (member['user_id'],))
        load = c.fetchone()['count']
        
        if load >= member['max_tickets']:
            c.execute('''SELECT im.*, u.id as user_id, u.name
                         FROM it_members im
                         JOIN users u ON im.user_id = u.id
                         WHERE im.is_backup = 1 LIMIT 1''')
            backup = c.fetchone()
            if backup:
                member = backup
    conn.close()
    return {'id': member['user_id'], 'name': member['name']} if member else None

def send_email(to, subject, html):
    try:
        msg = MIMEText(html, 'html')
        msg['Subject'] = subject
        msg['From'] = 'IT Support <itsupport@company.com>'
        msg['To'] = to
        print(f"Email would be sent to {to}: {subject}")
    except Exception as e:
        print(f"Email skipped: {e}")

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    try:
        user_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users (id, name, email, password, department, phone, role) VALUES (?, ?, ?, ?, ?, ?, 'employee')",
                  (user_id, data['name'], data['email'], hashed, data.get('department'), data.get('phone')))
        conn.commit()
        return jsonify({'message': 'Registration successful', 'userId': user_id})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE email = ?", (data['email'],))
    user = c.fetchone()
    conn.close()
    
    if not user or not bcrypt.checkpw(data['password'].encode(), user['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({'id': user['id'], 'email': user['email'], 'role': user['role']}, 
                       app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email'], 'role': user['role'], 'department': user['department']}
    })

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_me():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, email, role, department, phone FROM users WHERE id = ?", (request.user['id'],))
    user = c.fetchone()
    conn.close()
    return jsonify(dict(user)) if user else jsonify({'error': 'User not found'}), 404

@app.route('/api/tickets', methods=['GET'])
@token_required
def get_tickets():
    conn = get_db()
    c = conn.cursor()
    
    if request.user['role'] == 'employee':
        c.execute('''SELECT t.*, u.name as user_name, u.email as user_email, u.department as user_department,
                     a.name as assigned_to_name
                     FROM tickets t
                     JOIN users u ON t.user_id = u.id
                     LEFT JOIN users a ON t.assigned_to = a.id
                     WHERE t.user_id = ?
                     ORDER BY t.created_at DESC''', (request.user['id'],))
    elif request.user['role'] == 'it_staff':
        c.execute("SELECT category FROM it_members WHERE user_id = ?", (request.user['id'],))
        member = c.fetchone()
        if member:
            c.execute('''SELECT t.*, u.name as user_name, u.email as user_email, u.department as user_department,
                         a.name as assigned_to_name
                         FROM tickets t
                         JOIN users u ON t.user_id = u.id
                         LEFT JOIN users a ON t.assigned_to = a.id
                         WHERE t.category = ? OR t.assigned_to = ?
                         ORDER BY CASE t.urgency WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END, t.created_at DESC''',
                         (member['category'], request.user['id']))
        else:
            return jsonify([])
    else:
        c.execute('''SELECT t.*, u.name as user_name, u.email as user_email, u.department as user_department,
                     a.name as assigned_to_name
                     FROM tickets t
                     JOIN users u ON t.user_id = u.id
                     LEFT JOIN users a ON t.assigned_to = a.id
                     ORDER BY t.created_at DESC''')
    
    tickets = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(tickets)

@app.route('/api/tickets/<ticket_id>', methods=['GET'])
@token_required
def get_ticket(ticket_id):
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT t.*, u.name as user_name, u.email as user_email, u.department as user_department,
                 a.name as assigned_to_name
                 FROM tickets t
                 JOIN users u ON t.user_id = u.id
                 LEFT JOIN users a ON t.assigned_to = a.id
                 WHERE t.id = ?''', (ticket_id,))
    ticket = dict(c.fetchone()) if c.fetchone() else None
    
    if not ticket:
        conn.close()
        return jsonify({'error': 'Ticket not found'}), 404
    
    c.execute("SELECT * FROM ticket_logs WHERE ticket_id = ? ORDER BY created_at ASC", (ticket_id,))
    logs = [dict(row) for row in c.fetchall()]
    
    for log in logs:
        if log['user_id']:
            c.execute("SELECT name FROM users WHERE id = ?", (log['user_id'],))
            u = c.fetchone()
            log['user_name'] = u['name'] if u else None
    
    ticket['logs'] = logs
    ticket['attachments'] = []
    conn.close()
    return jsonify(ticket)

@app.route('/api/tickets', methods=['POST'])
@token_required
def create_ticket():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    ticket_id = str(uuid.uuid4())
    assigned = assign_ticket(data['category'])
    
    c.execute("SELECT COALESCE(MAX(ticket_number), 1000) as max_num FROM tickets")
    ticket_num = c.fetchone()['max_num'] + 1
    
    c.execute('''INSERT INTO tickets (id, ticket_number, user_id, category, title, description, urgency, department, sub_department, phone,
                 device_type, asset_number, device_working, software_name, error_message,
                 application_access, current_role, required_permissions, assigned_to)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (ticket_id, ticket_num, request.user['id'], data['category'], data['title'], data['description'],
               data.get('urgency', 'Medium'), data.get('department'), data.get('sub_department'), data.get('phone'), data.get('device_type'),
               data.get('asset_number'), data.get('device_working'), data.get('software_name'),
               data.get('error_message'), data.get('application_access'), data.get('current_role'),
               data.get('required_permissions'), assigned['id'] if assigned else None))
    
    c.execute("INSERT INTO ticket_logs (id, ticket_id, user_id, action, description) VALUES (?, ?, ?, ?, ?)",
              (str(uuid.uuid4()), ticket_id, request.user['id'], 'created', 'Ticket created'))
    
    c.execute("SELECT ticket_number FROM tickets WHERE id = ?", (ticket_id,))
    ticket_num = c.fetchone()['ticket_number']
    
    c.execute("SELECT name, email FROM users WHERE id = ?", (request.user['id'],))
    user = c.fetchone()
    
    conn.commit()
    conn.close()
    
    send_email(user['email'], f"IT Support Ticket #{ticket_num} Created",
                f"<h2>Your IT Support Request</h2><p>Ticket #{ticket_num} has been created and assigned to our IT team.</p>")
    
    return jsonify({'message': 'Ticket created successfully', 'ticketId': ticket_id, 'ticket_number': ticket_num})

@app.route('/api/tickets/<ticket_id>', methods=['PUT'])
@token_required
def update_ticket(ticket_id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket = c.fetchone()
    
    if not ticket:
        conn.close()
        return jsonify({'error': 'Ticket not found'}), 404
    
    updates = []
    params = []
    
    if 'status' in data:
        updates.append('status = ?')
        params.append(data['status'])
        if data['status'] == 'Completed':
            updates.append('resolved_at = CURRENT_TIMESTAMP')
    
    if 'assigned_to' in data:
        updates.append('assigned_to = ?')
        params.append(data['assigned_to'] if data['assigned_to'] else None)
    
    if updates:
        params.append(ticket_id)
        c.execute(f"UPDATE tickets SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", params)
    
    if data.get('notes'):
        c.execute("INSERT INTO ticket_logs (id, ticket_id, user_id, action, description) VALUES (?, ?, ?, ?, ?)",
                  (str(uuid.uuid4()), ticket_id, request.user['id'], data.get('notes'), 'note_added'))
    
    c.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    updated = dict(c.fetchone())
    conn.commit()
    conn.close()
    
    if data.get('status') == 'Completed':
        c = conn.cursor()
        c.execute("SELECT email, name FROM users WHERE id = ?", (ticket['user_id'],))
        user = c.fetchone()
        if user:
            send_email(user['email'], f"IT Support Ticket #{ticket['ticket_number']} Resolved",
                      f"<h2>Your IT Support Request - Resolved</h2><p>Ticket #{ticket['ticket_number']} has been resolved.</p>")
    
    return jsonify({'message': 'Ticket updated successfully'})

@app.route('/api/tickets/stats/dashboard', methods=['GET'])
@token_required
def get_stats():
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) as count FROM tickets")
    total = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'Open'")
    open_count = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'In Progress'")
    in_progress = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'Completed'")
    completed = c.fetchone()['count']
    
    c.execute("SELECT category, COUNT(*) as count FROM tickets GROUP BY category")
    by_category = [dict(row) for row in c.fetchall()]
    
    c.execute("SELECT urgency, COUNT(*) as count FROM tickets GROUP BY urgency")
    by_priority = [dict(row) for row in c.fetchall()]
    
    c.execute('''SELECT u.name, COUNT(t.id) as ticket_count
                FROM users u
                LEFT JOIN tickets t ON u.id = t.assigned_to AND t.status != 'Completed'
                WHERE u.role = 'it_staff'
                GROUP BY u.id''')
    workload = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return jsonify({'total': total, 'open': open_count, 'inProgress': in_progress, 'completed': completed, 'byCategory': by_category, 'byPriority': by_priority, 'workload': workload})

@app.route('/api/users/it-members', methods=['GET'])
@token_required
def get_it_members():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT u.id, u.name, u.email, u.department, im.category, im.max_tickets
                FROM it_members im
                JOIN users u ON im.user_id = u.id''')
    members = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(members)

@app.route('/api/admin/stats', methods=['GET'])
@token_required
def admin_stats():
    if request.user['role'] != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) as count FROM tickets")
    total = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'Open'")
    open_tickets = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'In Progress'")
    in_progress = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'Completed'")
    completed = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'Pending User'")
    pending = c.fetchone()['count']
    
    c.execute("SELECT category, COUNT(*) as count FROM tickets GROUP BY category")
    by_category = [dict(row) for row in c.fetchall()]
    
    c.execute("SELECT urgency, COUNT(*) as count FROM tickets GROUP BY urgency")
    by_priority = [dict(row) for row in c.fetchall()]
    
    c.execute('''SELECT u.name, im.category as specialty,
                COUNT(t.id) as active_tickets,
                (SELECT COUNT(*) FROM tickets WHERE assigned_to = u.id AND status = 'Completed') as resolved_tickets
                FROM users u
                LEFT JOIN it_members im ON u.id = im.user_id
                LEFT JOIN tickets t ON u.id = t.assigned_to AND t.status != 'Completed'
                WHERE u.role = 'it_staff'
                GROUP BY u.id''')
    workload = [dict(row) for row in c.fetchall()]
    
    c.execute("SELECT AVG((julianday(resolved_at) - julianday(created_at))) as avg_days FROM tickets WHERE status = 'Completed' AND resolved_at IS NOT NULL")
    avg_days = c.fetchone()['avg_days'] or 0
    
    conn.close()
    return jsonify({
        'totalTickets': total, 'openTickets': open_tickets, 'inProgressTickets': in_progress,
        'completedTickets': completed, 'pendingTickets': pending, 'byCategory': by_category,
        'byPriority': by_priority, 'workload': workload, 'avgResolutionDays': avg_days
    })

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3000, debug=True)
