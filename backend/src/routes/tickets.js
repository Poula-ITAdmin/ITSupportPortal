const express = require('express');
const { db } = require('../models/db');
const { v4: uuidv4 } = require('uuid');
const jwt = require('jsonwebtoken');
const { assignTicket } = require('../services/assignment');
const { createPlannerTask, updatePlannerTask } = require('../services/planner');
const { sendEmail } = require('../services/email');

const router = express.Router();

function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET || 'secretkey123');
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}

router.get('/', authenticate, (req, res) => {
  try {
    let tickets;
    if (req.user.role === 'employee') {
      tickets = db.prepare(`
        SELECT t.*, u.name as user_name, u.email as user_email, u.department as user_department,
               a.name as assigned_to_name
        FROM tickets t
        JOIN users u ON t.user_id = u.id
        LEFT JOIN users a ON t.assigned_to = a.id
        WHERE t.user_id = ?
        ORDER BY t.created_at DESC
      `).all(req.user.id);
    } else if (req.user.role === 'it_staff') {
      const member = db.prepare('SELECT category FROM it_members WHERE user_id = ?').get(req.user.id);
      if (member) {
        tickets = db.prepare(`
          SELECT t.*, u.name as user_name, u.email as user_email, u.department as user_department,
                 a.name as assigned_to_name
          FROM tickets t
          JOIN users u ON t.user_id = u.id
          LEFT JOIN users a ON t.assigned_to = a.id
          WHERE t.category = ? OR t.assigned_to = ?
          ORDER BY 
            CASE t.urgency 
              WHEN 'High' THEN 1 
              WHEN 'Medium' THEN 2 
              WHEN 'Low' THEN 3 
            END,
            t.created_at DESC
        `).all(member.category, req.user.id);
      } else {
        tickets = [];
      }
    } else {
      tickets = db.prepare(`
        SELECT t.*, u.name as user_name, u.email as user_email, u.department as user_department,
               a.name as assigned_to_name
        FROM tickets t
        JOIN users u ON t.user_id = u.id
        LEFT JOIN users a ON t.assigned_to = a.id
        ORDER BY t.created_at DESC
      `).all();
    }
    res.json(tickets);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', authenticate, (req, res) => {
  try {
    const ticket = db.prepare(`
      SELECT t.*, u.name as user_name, u.email as user_email, u.department as user_department,
             a.name as assigned_to_name
      FROM tickets t
      JOIN users u ON t.user_id = u.id
      LEFT JOIN users a ON t.assigned_to = a.id
      WHERE t.id = ?
    `).get(req.params.id);
    
    if (!ticket) return res.status(404).json({ error: 'Ticket not found' });
    
    const attachments = db.prepare('SELECT * FROM ticket_attachments WHERE ticket_id = ?').all(req.params.id);
    const logs = db.prepare(`
      SELECT l.*, u.name as user_name
      FROM ticket_logs l
      LEFT JOIN users u ON l.user_id = u.id
      WHERE l.ticket_id = ?
      ORDER BY l.created_at ASC
    `).all(req.params.id);
    
    res.json({ ...ticket, attachments, logs });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', authenticate, async (req, res) => {
  try {
    const { category, title, description, urgency, department, phone,
            device_type, asset_number, device_working,
            software_name, error_message,
            application_access, current_role, required_permissions } = req.body;
    
    const ticketId = uuidv4();
    
    const assignedTo = await assignTicket(category);
    
    db.prepare(`
      INSERT INTO tickets (id, user_id, category, title, description, urgency, department, phone,
                           device_type, asset_number, device_working, software_name, error_message,
                           application_access, current_role, required_permissions, assigned_to)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(ticketId, req.user.id, category, title, description, urgency, department, phone,
           device_type, asset_number, device_working, software_name, error_message,
           application_access, current_role, required_permissions, assignedTo?.id || null);
    
    db.prepare(`
      INSERT INTO ticket_logs (id, ticket_id, user_id, action, description)
      VALUES (?, ?, ?, ?, ?)
    `).run(uuidv4(), ticketId, req.user.id, 'created', 'Ticket created');
    
    const ticket = db.prepare('SELECT * FROM tickets WHERE id = ?').get(ticketId);
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.user.id);
    
    try {
      const plannerTask = await createPlannerTask(ticket, assignedTo);
      if (plannerTask) {
        db.prepare('UPDATE tickets SET planner_task_id = ? WHERE id = ?').run(plannerTask.id, ticketId);
      }
    } catch (e) {
      console.log('Planner integration skipped:', e.message);
    }
    
    try {
      await sendEmail({
        to: user.email,
        subject: `IT Support Ticket #${ticket.ticket_number} Created`,
        html: `
          <h2>Your IT Support Request</h2>
          <p>Dear ${user.name},</p>
          <p>Your ticket has been created and assigned to our IT team.</p>
          <p><strong>Ticket #${ticket.ticket_number}</strong></p>
          <p><strong>Category:</strong> ${category}</p>
          <p><strong>Issue:</strong> ${title}</p>
          <p><strong>Status:</strong> Open</p>
          <p>Our IT team will review your request shortly.</p>
        `
      });
    } catch (e) {
      console.log('Email skipped:', e.message);
    }
    
    res.json({ message: 'Ticket created successfully', ticketId, ticket_number: ticket.ticket_number });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', authenticate, async (req, res) => {
  try {
    const { status, assigned_to, notes } = req.body;
    const ticket = db.prepare('SELECT * FROM tickets WHERE id = ?').get(req.params.id);
    
    if (!ticket) return res.status(404).json({ error: 'Ticket not found' });
    
    const updates = [];
    const params = [];
    
    if (status) {
      updates.push('status = ?');
      params.push(status);
      if (status === 'Completed') {
        updates.push('resolved_at = CURRENT_TIMESTAMP');
      }
    }
    
    if (assigned_to) {
      updates.push('assigned_to = ?');
      params.push(assigned_to);
    }
    
    if (updates.length > 0) {
      params.push(req.params.id);
      db.prepare(`UPDATE tickets SET ${updates.join(', ')}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`).run(...params);
    }
    
    db.prepare(`
      INSERT INTO ticket_logs (id, ticket_id, user_id, action, description)
      VALUES (?, ?, ?, ?, ?)
    `).run(uuidv4(), req.params.id, req.user.id, notes ? 'note_added' : 'status_updated', notes || `Status changed to ${status}`);
    
    const updatedTicket = db.prepare('SELECT * FROM tickets WHERE id = ?').get(req.params.id);
    
    try {
      await updatePlannerTask(updatedTicket);
    } catch (e) {
      console.log('Planner update skipped:', e.message);
    }
    
    if (status === 'Completed') {
      const user = db.prepare('SELECT * FROM users WHERE id = ?').get(ticket.user_id);
      try {
        await sendEmail({
          to: user.email,
          subject: `IT Support Ticket #${ticket.ticket_number} Resolved`,
          html: `
            <h2>Your IT Support Request - Resolved</h2>
            <p>Dear ${user.name},</p>
            <p>Your ticket has been resolved.</p>
            <p><strong>Ticket #${ticket.ticket_number}</strong></p>
            <p><strong>Issue:</strong> ${ticket.title}</p>
            <p>If you have any issues, please submit a new ticket.</p>
          `
        });
      } catch (e) {
        console.log('Email skipped:', e.message);
      }
    }
    
    res.json({ message: 'Ticket updated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/stats/dashboard', authenticate, (req, res) => {
  try {
    const total = db.prepare('SELECT COUNT(*) as count FROM tickets').get().count;
    const open = db.prepare("SELECT COUNT(*) as count FROM tickets WHERE status = 'Open'").get().count;
    const inProgress = db.prepare("SELECT COUNT(*) as count FROM tickets WHERE status = 'In Progress'").get().count;
    const completed = db.prepare("SELECT COUNT(*) as count FROM tickets WHERE status = 'Completed'").get().count;
    
    const byCategory = db.prepare(`
      SELECT category, COUNT(*) as count FROM tickets GROUP BY category
    `).all();
    
    const byPriority = db.prepare(`
      SELECT urgency, COUNT(*) as count FROM tickets GROUP BY urgency
    `).all();
    
    const workload = db.prepare(`
      SELECT u.name, COUNT(t.id) as ticket_count
      FROM users u
      LEFT JOIN tickets t ON u.id = t.assigned_to AND t.status != 'Completed'
      WHERE u.role = 'it_staff'
      GROUP BY u.id
    `).all();
    
    res.json({ total, open, inProgress, completed, byCategory, byPriority, workload });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
