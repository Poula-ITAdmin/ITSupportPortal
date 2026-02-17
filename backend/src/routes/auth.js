const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { db } = require('../models/db');

const router = express.Router();

router.post('/register', (req, res) => {
  try {
    const { name, email, password, department, phone } = req.body;
    const { v4: uuidv4 } = require('uuid');
    
    const existing = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
    if (existing) {
      return res.status(400).json({ error: 'Email already registered' });
    }
    
    const hashedPassword = bcrypt.hashSync(password, 10);
    const userId = uuidv4();
    
    db.prepare(`
      INSERT INTO users (id, name, email, password, department, phone, role)
      VALUES (?, ?, ?, ?, ?, ?, 'employee')
    `).run(userId, name, email, hashedPassword, department, phone);
    
    res.json({ message: 'Registration successful', userId });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/login', (req, res) => {
  try {
    const { email, password } = req.body;
    
    const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
    if (!user || !bcrypt.compareSync(password, user.password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const token = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      process.env.JWT_SECRET || 'secretkey123',
      { expiresIn: '24h' }
    );
    
    res.json({
      token,
      user: { id: user.id, name: user.name, email: user.email, role: user.role, department: user.department }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/me', (req, res) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'No token provided' });
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secretkey123');
    const user = db.prepare('SELECT id, name, email, role, department, phone FROM users WHERE id = ?').get(decoded.id);
    
    if (!user) return res.status(404).json({ error: 'User not found' });
    
    res.json(user);
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
});

module.exports = router;
