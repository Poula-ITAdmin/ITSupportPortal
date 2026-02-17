const express = require('express');
const { db } = require('../models/db');
const jwt = require('jsonwebtoken');

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

router.get('/it-members', authenticate, (req, res) => {
  try {
    const members = db.prepare(`
      SELECT u.id, u.name, u.email, u.department, im.category, im.max_tickets
      FROM it_members im
      JOIN users u ON im.user_id = u.id
    `).all();
    res.json(members);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/employees', authenticate, (req, res) => {
  try {
    const employees = db.prepare(`
      SELECT id, name, email, department, phone FROM users WHERE role = 'employee'
    `).all();
    res.json(employees);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
