const Database = require('better-sqlite3');
const path = require('path');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const db = new Database(path.join(__dirname, '../../data/itsupport.db'));

function initializeDatabase() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      phone TEXT,
      department TEXT,
      role TEXT DEFAULT 'employee',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS it_members (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      category TEXT NOT NULL,
      max_tickets INTEGER DEFAULT 10,
      is_backup INTEGER DEFAULT 0,
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS tickets (
      id TEXT PRIMARY KEY,
      ticket_number INTEGER UNIQUE AUTOINCREMENT,
      user_id TEXT NOT NULL,
      category TEXT NOT NULL,
      title TEXT NOT NULL,
      description TEXT,
      urgency TEXT DEFAULT 'Medium',
      status TEXT DEFAULT 'Open',
      assigned_to TEXT,
      device_type TEXT,
      asset_number TEXT,
      device_working TEXT,
      software_name TEXT,
      error_message TEXT,
      application_access TEXT,
      current_role TEXT,
      required_permissions TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      resolved_at DATETIME,
      planner_task_id TEXT,
      FOREIGN KEY (user_id) REFERENCES users(id),
      FOREIGN KEY (assigned_to) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS ticket_attachments (
      id TEXT PRIMARY KEY,
      ticket_id TEXT NOT NULL,
      filename TEXT NOT NULL,
      filepath TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (ticket_id) REFERENCES tickets(id)
    );

    CREATE TABLE IF NOT EXISTS ticket_logs (
      id TEXT PRIMARY KEY,
      ticket_id TEXT NOT NULL,
      user_id TEXT,
      action TEXT NOT NULL,
      description TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (ticket_id) REFERENCES tickets(id),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT
    );
  `);

  const adminExists = db.prepare('SELECT id FROM users WHERE email = ?').get('admin@company.com');
  if (!adminExists) {
    const adminId = uuidv4();
    const hashedPassword = bcrypt.hashSync('admin123', 10);
    
    db.prepare(`
      INSERT INTO users (id, name, email, password, role, department)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(adminId, 'Admin', 'admin@company.com', hashedPassword, 'admin', 'IT');

    const itMembers = [
      { name: 'John Smith', email: 'john@company.com', category: 'Hardware', max: 15 },
      { name: 'Poula Khan', email: 'poula@company.com', category: 'Software', max: 15 },
      { name: 'Maria Garcia', email: 'maria@company.com', category: 'Access', max: 15 }
    ];

    itMembers.forEach(member => {
      const memberId = uuidv4();
      const memberPassword = bcrypt.hashSync('it123456', 10);
      
      db.prepare(`
        INSERT INTO users (id, name, email, password, role, department)
        VALUES (?, ?, ?, ?, ?, ?)
      `).run(memberId, member.name, member.email, memberPassword, 'it_staff', 'IT');

      db.prepare(`
        INSERT INTO it_members (id, user_id, category, max_tickets)
        VALUES (?, ?, ?, ?)
      `).run(uuidv4(), memberId, member.category, member.max);
    });

    console.log('Database initialized with default users');
  }
}

module.exports = { db, initializeDatabase };
