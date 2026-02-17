const express = require('express');
const { db } = require('../models/db');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const router = express.Router();

function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET || 'secretkey123');
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}

router.get('/stats', authenticate, (req, res) => {
  try {
    const totalTickets = db.prepare('SELECT COUNT(*) as count FROM tickets').get().count;
    const openTickets = db.prepare("SELECT COUNT(*) as count FROM tickets WHERE status = 'Open'").get().count;
    const inProgressTickets = db.prepare("SELECT COUNT(*) as count FROM tickets WHERE status = 'In Progress'").get().count;
    const completedTickets = db.prepare("SELECT COUNT(*) as count FROM tickets WHERE status = 'Completed'").get().count;
    const pendingTickets = db.prepare("SELECT COUNT(*) as count FROM tickets WHERE status = 'Pending User'").get().count;
    
    const byCategory = db.prepare(`
      SELECT category, COUNT(*) as count FROM tickets GROUP BY category
    `).all();
    
    const byPriority = db.prepare(`
      SELECT urgency, COUNT(*) as count FROM tickets GROUP BY urgency
    `).all();
    
    const byStatus = db.prepare(`
      SELECT status, COUNT(*) as count FROM tickets GROUP BY status
    `).all();
    
    const workload = db.prepare(`
      SELECT u.name, im.category as specialty, 
             COUNT(t.id) as active_tickets,
             (SELECT COUNT(*) FROM tickets WHERE assigned_to = u.id AND status = 'Completed') as resolved_tickets
      FROM users u
      LEFT JOIN it_members im ON u.id = im.user_id
      LEFT JOIN tickets t ON u.id = t.assigned_to AND t.status != 'Completed'
      WHERE u.role = 'it_staff'
      GROUP BY u.id
    `).all();
    
    const avgResolution = db.prepare(`
      SELECT AVG((julianday(resolved_at) - julianday(created_at))) as avg_days
      FROM tickets WHERE status = 'Completed' AND resolved_at IS NOT NULL
    `).get();
    
    res.json({
      totalTickets,
      openTickets,
      inProgressTickets,
      completedTickets,
      pendingTickets,
      byCategory,
      byPriority,
      byStatus,
      workload,
      avgResolutionDays: avgResolution.avg_days || 0
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/it-member', authenticate, (req, res) => {
  try {
    const { name, email, password, category, max_tickets } = req.body;
    
    const userId = uuidv4();
    const hashedPassword = bcrypt.hashSync(password, 10);
    
    db.prepare(`
      INSERT INTO users (id, name, email, password, role, department)
      VALUES (?, ?, ?, ?, 'it_staff', 'IT')
    `).run(userId, name, email, hashedPassword);
    
    db.prepare(`
      INSERT INTO it_members (id, user_id, category, max_tickets)
      VALUES (?, ?, ?, ?)
    `).run(uuidv4(), userId, category, max_tickets || 10);
    
    res.json({ message: 'IT member added successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/it-member/:id', authenticate, (req, res) => {
  try {
    const { category, max_tickets, name } = req.body;
    
    const member = db.prepare('SELECT user_id FROM it_members WHERE id = ?').get(req.params.id);
    if (!member) return res.status(404).json({ error: 'IT member not found' });
    
    if (category || max_tickets) {
      db.prepare(`
        UPDATE it_members SET category = COALESCE(?, category), max_tickets = COALESCE(?, max_tickets)
        WHERE id = ?
      `).run(category, max_tickets, req.params.id);
    }
    
    if (name) {
      db.prepare('UPDATE users SET name = ? WHERE id = ?').run(name, member.user_id);
    }
    
    res.json({ message: 'IT member updated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/settings', authenticate, (req, res) => {
  try {
    const settings = db.prepare('SELECT * FROM settings').all();
    const settingsObj = {};
    settings.forEach(s => settingsObj[s.key] = s.value);
    res.json(settingsObj);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/settings', authenticate, (req, res) => {
  try {
    const { key, value } = req.body;
    db.prepare(`
      INSERT INTO settings (key, value) VALUES (?, ?)
      ON CONFLICT(key) DO UPDATE SET value = excluded.value
    `).run(key, value);
    res.json({ message: 'Setting updated' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
