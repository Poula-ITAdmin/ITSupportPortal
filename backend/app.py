"""
IT Support Portal Backend
Main entry point
"""

from app import create_app

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True
    )
    
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
    
    c.execute('''CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ticket_attachments (
        id TEXT PRIMARY KEY,
        ticket_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_type TEXT,
        file_size INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS chat_channels (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        channel_type TEXT DEFAULT 'general',
        department TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id TEXT PRIMARY KEY,
        channel_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        message_type TEXT DEFAULT 'text',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (channel_id) REFERENCES chat_channels(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS chat_reads (
        id TEXT PRIMARY KEY,
        channel_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        last_read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (channel_id) REFERENCES chat_channels(id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(channel_id, user_id)
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
    
    c.execute("SELECT COUNT(*) as count FROM chat_channels")
    row = c.fetchone()
    count = row[0] if row else 0
    if count == 0:
        channels = [
            ('General', 'General facility chat for everyone', 'general', None),
            ('IT Support', 'IT team discussions', 'team', 'IT'),
            ('Hospital Staff', 'Hospital department staff chat', 'department', 'Hospital'),
            ('Mission Staff', 'Mission department staff chat', 'department', 'Mission'),
        ]
        
        for name, desc, ch_type, dept in channels:
            c.execute("INSERT INTO chat_channels (id, name, description, channel_type, department) VALUES (?, ?, ?, ?, ?)",
                      (str(uuid.uuid4()), name, desc, ch_type, dept))
        
        hospital_depts = ['Accounting', 'Nursing', 'Pharmacy', 'Radiology', 'Laboratory', 'Emergency', 'Surgery', 'ICU']
        for dept in hospital_depts:
            c.execute("INSERT INTO chat_channels (id, name, description, channel_type, department) VALUES (?, ?, ?, ?, ?)",
                      (str(uuid.uuid4()), f"{dept}", f"{dept} department channel", 'department', f"Hospital:{dept}"))
        
        mission_depts = ['Administration', 'Finance', 'HR', 'Programs', 'Logistics']
        for dept in mission_depts:
            c.execute("INSERT INTO chat_channels (id, name, description, channel_type, department) VALUES (?, ?, ?, ?, ?)",
                      (str(uuid.uuid4()), f"{dept}", f"{dept} department channel", 'department', f"Mission:{dept}"))
    
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
    if not SMTP_HOST or not SMTP_USER:
        print(f"[DEMO] Email to {to}: {subject}")
        return True
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_FROM
        msg['To'] = to
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        print(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

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

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT id, name FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'message': 'If the email exists, a reset link will be sent'}), 200
    
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(hours=24)
    
    c.execute("INSERT INTO password_reset_tokens (id, user_id, token, expires_at) VALUES (?, ?, ?, ?)",
              (str(uuid.uuid4()), user['id'], token, expires))
    conn.commit()
    conn.close()
    
    reset_link = f"http://localhost:3000/#/reset-password?token={token}"
    send_email(email, "Password Reset Request",
               f"<h2>Password Reset</h2><p>Hello {user['name']},</p><p>Click the link below to reset your password:</p><p><a href='{reset_link}'>{reset_link}</a></p><p>This link expires in 24 hours.</p>")
    
    return jsonify({'message': 'If the email exists, a reset link will be sent'}), 200

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""SELECT user_id FROM password_reset_tokens 
                WHERE token = ? AND used = 0 AND expires_at > datetime('now')""", (token,))
    record = c.fetchone()
    
    if not record:
        conn.close()
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, record['user_id']))
    c.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Password reset successfully'}), 200

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

@app.route('/api/tickets/search', methods=['GET'])
@token_required
def search_tickets():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    
    if not query and not category and not status:
        return jsonify({'error': 'At least one search parameter required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    sql = '''SELECT t.*, u.name as user_name, u.email as user_email, u.department as user_department,
             a.name as assigned_to_name
             FROM tickets t
             JOIN users u ON t.user_id = u.id
             LEFT JOIN users a ON t.assigned_to = a.id
             WHERE 1=1'''
    params = []
    
    if query:
        sql += ''' AND (t.title LIKE ? OR t.description LIKE ? OR t.ticket_number LIKE ?)'''
        search_term = f'%{query}%'
        params.extend([search_term, search_term, search_term])
    
    if category:
        sql += ' AND t.category = ?'
        params.append(category)
    
    if status:
        sql += ' AND t.status = ?'
        params.append(status)
    
    if request.user['role'] == 'employee':
        sql += ' AND t.user_id = ?'
        params.append(request.user['id'])
    elif request.user['role'] == 'it_staff':
        c.execute("SELECT category FROM it_members WHERE user_id = ?", (request.user['id'],))
        member = c.fetchone()
        if member:
            sql += ' AND (t.category = ? OR t.assigned_to = ?)'
            params.extend([member['category'], request.user['id']])
    
    sql += ' ORDER BY t.created_at DESC LIMIT 50'
    
    c.execute(sql, params)
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
    row = c.fetchone()
    ticket = dict(row) if row else None
    
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
def create_ticket():
    data = request.json
    user_id = request.user.get('id') if hasattr(request, 'user') else None
    
    # Allow anonymous ticket creation
    if not user_id:
        user_id = 'anonymous_' + str(uuid.uuid4())
    
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
              (ticket_id, ticket_num, user_id, data['category'], data['title'], data['description'],
               data.get('urgency', 'Medium'), data.get('department'), data.get('sub_department'), data.get('phone'), data.get('device_type'),
               data.get('asset_number'), data.get('device_working'), data.get('software_name'),
               data.get('error_message'), data.get('application_access'), data.get('current_role'),
               data.get('required_permissions'), assigned['id'] if assigned else None))
    
    c.execute("INSERT INTO ticket_logs (id, ticket_id, user_id, action, description) VALUES (?, ?, ?, ?, ?)",
              (str(uuid.uuid4()), ticket_id, user_id, 'created', 'Ticket created'))
    
    c.execute("SELECT ticket_number FROM tickets WHERE id = ?", (ticket_id,))
    ticket_num = c.fetchone()['ticket_number']
    
    # For non-anonymous users, get email; for anonymous, use form email if provided
    user_email = None
    user_name = None
    if not user_id.startswith('anonymous_'):
        c.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if user:
            user_email = user['email']
            user_name = user['name']
    else:
        # Use email from form for anonymous submission
        user_email = data.get('email')
        user_name = data.get('user_name', 'Portal User')
    
    staff_email = None
    staff_name = None
    if assigned:
        c.execute("SELECT name, email FROM users WHERE id = ?", (assigned['id'],))
        staff = c.fetchone()
        if staff:
            staff_email = staff['email']
            staff_name = staff['name']
    
    conn.commit()
    conn.close()
    
    if user_email:
        send_email(user_email, f"IT Support Ticket #{ticket_num} Created",
                    f"<h2>Your IT Support Request</h2><p>Ticket #{ticket_num} has been created and assigned to our IT team.</p>")
    
    if staff_email:
        staff_email_html = f"""
        <h2>New Ticket Assigned</h2>
        <p><strong>Ticket #{ticket_num}</strong> has been assigned to you.</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Category</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{data['category']}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Urgency</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{data.get('urgency', 'Medium')}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Title</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{data['title']}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Description</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{data.get('description', 'N/A')}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Submitted by</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{user_name} - {user_email}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Department</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{data.get('department', 'N/A')}</td></tr>
        </table>
        <p>Please log in to the IT Support Portal to view and process this ticket.</p>
        """
        send_email(staff_email, f"New Ticket Assigned - #{ticket_num} - {data['category']}", staff_email_html)
    
    return jsonify({'message': 'Ticket created successfully', 'ticketId': ticket_id, 'ticket_number': ticket_num})

@app.route('/api/tickets/<ticket_id>/attachments', methods=['POST'])
@token_required
def upload_attachment(ticket_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT id FROM tickets WHERE id = ?", (ticket_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Ticket not found'}), 404
    
    import hashlib
    file_ext = '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() or ''
    safe_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)
    file.save(file_path)
    
    file_size = os.path.getsize(file_path)
    
    attachment_id = str(uuid.uuid4())
    c.execute("""INSERT INTO ticket_attachments 
                (id, ticket_id, user_id, filename, original_name, file_type, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (attachment_id, ticket_id, request.user['id'], safe_name, file.filename, file_ext, file_size))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'File uploaded', 'id': attachment_id, 'filename': file.filename})

@app.route('/api/tickets/<ticket_id>/attachments', methods=['GET'])
@token_required
def get_attachments(ticket_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM ticket_attachments WHERE ticket_id = ? ORDER BY created_at DESC", (ticket_id,))
    attachments = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(attachments)

@app.route('/api/attachments/<attachment_id>/download', methods=['GET'])
@token_required
def download_attachment(attachment_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM ticket_attachments WHERE id = ?", (attachment_id,))
    attachment = c.fetchone()
    conn.close()
    
    if not attachment:
        return jsonify({'error': 'Attachment not found'}), 404
    
    return send_from_directory(UPLOAD_FOLDER, attachment['filename'], as_attachment=True, download_name=attachment['original_name'])

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
    
    user_email = None
    user_name = None
    ticket_num = None
    
    old_assigned = ticket['assigned_to']
    new_assigned = data.get('assigned_to')
    
    reassigned_to_email = None
    if new_assigned and str(new_assigned) != str(old_assigned):
        c.execute("SELECT u.name, u.email, COALESCE(im.category, 'General') as category FROM users u LEFT JOIN it_members im ON u.id = im.user_id WHERE u.id = ?", (new_assigned,))
        new_staff = c.fetchone()
        if new_staff:
            reassigned_to_email = {
                'email': new_staff['email'],
                'name': new_staff['name'],
                'category': new_staff['category']
            }
    
    if data.get('status') == 'Completed':
        c.execute("SELECT email, name, ticket_number FROM users u JOIN tickets t ON u.id = t.user_id WHERE t.id = ?", (ticket_id,))
        user = c.fetchone()
        if user:
            user_email = user['email']
            user_name = user['name']
            ticket_num = user['ticket_number']
    
    conn.commit()
    conn.close()
    
    if user_email and ticket_num:
        send_email(user_email, f"IT Support Ticket #{ticket_num} Resolved",
                  f"<h2>Your IT Support Request - Resolved</h2><p>Ticket #{ticket_num} has been resolved.</p>")
    
    if reassigned_to_email:
        reassign_html = f"""
        <h2>Ticket Reassigned to You</h2>
        <p><strong>Ticket #{ticket['ticket_number']}</strong> has been reassigned to you.</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Title</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{ticket['title']}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Category</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{ticket['category']}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Status</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{data.get('status', ticket['status'])}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Description</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{ticket.get('description', 'N/A')}</td></tr>
        </table>
        <p>Please log in to the IT Support Portal to view and process this ticket.</p>
        """
        send_email(reassigned_to_email['email'], f"Ticket Reassigned - #{ticket['ticket_number']}", reassign_html)
    
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

@app.route('/api/admin/users', methods=['GET'])
@token_required
def get_all_users():
    if request.user['role'] != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, email, role, department, phone, created_at FROM users ORDER BY created_at DESC")
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/admin/users', methods=['POST'])
@token_required
def create_user():
    if request.user['role'] != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    
    data = request.json
    required = ['name', 'email', 'password', 'role']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        user_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
        c.execute("""INSERT INTO users (id, name, email, password, role, department, phone) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (user_id, data['name'], data['email'], hashed, data['role'], 
                   data.get('department', ''), data.get('phone', '')))
        
        if data['role'] == 'it_staff' and data.get('category'):
            member_id = str(uuid.uuid4())
            c.execute("""INSERT INTO it_members (id, user_id, category, max_tickets) 
                        VALUES (?, ?, ?, ?)""",
                      (member_id, user_id, data['category'], 15))
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'User created successfully', 'userId': user_id})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Email already exists'}), 400

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    if request.user['role'] != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    
    if user_id == request.user['id']:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("DELETE FROM it_members WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM ticket_logs WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM tickets WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User deleted successfully'})

@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    if request.user['role'] != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    existing = c.fetchone()
    if not existing:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    name = data.get('name', existing['name'])
    email = data.get('email', existing['email'])
    role = data.get('role', existing['role'])
    department = data.get('department', existing['department'])
    
    try:
        c.execute("""UPDATE users SET name = ?, email = ?, role = ?, department = ? WHERE id = ?""",
                  (name, email, role, department, user_id))
        
        c.execute("DELETE FROM it_members WHERE user_id = ?", (user_id,))
        
        if role == 'it_staff' and data.get('category'):
            member_id = str(uuid.uuid4())
            c.execute("""INSERT INTO it_members (id, user_id, category, max_tickets) 
                        VALUES (?, ?, ?, ?)""",
                      (member_id, user_id, data['category'], data.get('max_tickets', 15)))
        
        if data.get('password'):
            hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
            c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'User updated successfully'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Email already exists'}), 400

@app.route('/api/chat/channels', methods=['GET'])
@token_required
def get_chat_channels():
    conn = get_db()
    c = conn.cursor()
    
    user_dept = request.user.get('department', '')
    user_role = request.user.get('role', '')
    
    c.execute("""SELECT cc.*, 
                 (SELECT COUNT(*) FROM chat_messages WHERE channel_id = cc.id) as message_count,
                 (SELECT MAX(created_at) FROM chat_messages WHERE channel_id = cc.id) as last_message_at
                 FROM chat_channels cc
                 ORDER BY 
                    CASE cc.channel_type 
                        WHEN 'general' THEN 0 
                        WHEN 'team' THEN 1 
                        ELSE 2 
                    END,
                    cc.name""")
    
    channels = [dict(row) for row in c.fetchall()]
    
    for ch in channels:
        c.execute("""SELECT cr.last_read_at FROM chat_reads cr 
                    WHERE cr.channel_id = ? AND cr.user_id = ?""", 
                  (ch['id'], request.user['id']))
        read_record = c.fetchone()
        ch['unread_count'] = 0
        if read_record:
            c.execute("""SELECT COUNT(*) as count FROM chat_messages 
                        WHERE channel_id = ? AND created_at > ?""",
                      (ch['id'], read_record['last_read_at']))
            ch['unread_count'] = c.fetchone()['count']
    
    conn.close()
    return jsonify(channels)

@app.route('/api/chat/channels', methods=['POST'])
@token_required
def create_chat_channel():
    if request.user['role'] not in ['admin', 'it_staff']:
        return jsonify({'error': 'Only IT staff can create channels'}), 403
    
    data = request.json
    channel_id = str(uuid.uuid4())
    
    conn = get_db()
    c = conn.cursor()
    c.execute("""INSERT INTO chat_channels (id, name, description, channel_type, department, created_by) 
                VALUES (?, ?, ?, ?, ?, ?)""",
              (channel_id, data.get('name'), data.get('description', ''), 
               data.get('type', 'general'), data.get('department'), request.user['id']))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Channel created', 'id': channel_id})

@app.route('/api/chat/channels/<channel_id>/messages', methods=['GET'])
@token_required
def get_channel_messages(channel_id):
    conn = get_db()
    c = conn.cursor()
    
    limit = request.args.get('limit', 50, type=int)
    before = request.args.get('before', '')
    
    c.execute("""SELECT cm.*, u.name as user_name, u.role as user_role
                 FROM chat_messages cm
                 JOIN users u ON cm.user_id = u.id
                 WHERE cm.channel_id = ?""", (channel_id,))
    
    if before:
        c.execute("""SELECT cm.*, u.name as user_name, u.role as user_role
                     FROM chat_messages cm
                     JOIN users u ON cm.user_id = u.id
                     WHERE cm.channel_id = ? AND cm.created_at < ?
                     ORDER BY cm.created_at DESC LIMIT ?""", 
                  (channel_id, before, limit))
    else:
        c.execute("""SELECT cm.*, u.name as user_name, u.role as user_role
                     FROM chat_messages cm
                     JOIN users u ON cm.user_id = u.id
                     WHERE cm.channel_id = ?
                     ORDER BY cm.created_at DESC LIMIT ?""", 
                  (channel_id, limit))
    
    messages = [dict(row) for row in c.fetchall()]
    messages.reverse()
    
    c.execute("""INSERT OR REPLACE INTO chat_reads (id, channel_id, user_id, last_read_at)
                 VALUES (?, ?, ?, datetime('now'))""",
              (str(uuid.uuid4()), channel_id, request.user['id']))
    conn.commit()
    conn.close()
    
    return jsonify(messages)

@app.route('/api/chat/channels/<channel_id>/messages', methods=['POST'])
@token_required
def send_channel_message(channel_id):
    data = request.json
    message_text = data.get('message', '').strip()
    
    if not message_text:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT id FROM chat_channels WHERE id = ?", (channel_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Channel not found'}), 404
    
    message_id = str(uuid.uuid4())
    c.execute("""INSERT INTO chat_messages (id, channel_id, user_id, message) 
                 VALUES (?, ?, ?, ?)""",
              (message_id, channel_id, request.user['id'], message_text))
    
    c.execute("""INSERT OR REPLACE INTO chat_reads (id, channel_id, user_id, last_read_at)
                 VALUES (?, ?, ?, datetime('now'))""",
              (str(uuid.uuid4()), channel_id, request.user['id']))
    
    conn.commit()
    
    c.execute("""SELECT cm.*, u.name as user_name, u.role as user_role
                 FROM chat_messages cm
                 JOIN users u ON cm.user_id = u.id
                 WHERE cm.id = ?""", (message_id,))
    message = dict(c.fetchone())
    conn.close()
    
    return jsonify(message)

@app.route('/api/chat/channels/<channel_id>/unread', methods=['GET'])
@token_required
def get_unread_count(channel_id):
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""SELECT last_read_at FROM chat_reads 
                WHERE channel_id = ? AND user_id = ?""", 
              (channel_id, request.user['id']))
    read_record = c.fetchone()
    
    if not read_record:
        conn.close()
        c.execute("SELECT COUNT(*) as count FROM chat_messages WHERE channel_id = ?", (channel_id,))
        return jsonify({'unread': c.fetchone()['count']})
    
    c.execute("""SELECT COUNT(*) as count FROM chat_messages 
                WHERE channel_id = ? AND created_at > ?""",
              (channel_id, read_record['last_read_at']))
    unread = c.fetchone()['count']
    conn.close()
    
    return jsonify({'unread': unread})

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3000, debug=True)
