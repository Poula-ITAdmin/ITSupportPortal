const { db } = require('../models/db');

async function assignTicket(category) {
  const itMember = db.prepare(`
    SELECT im.*, u.id as user_id, u.name
    FROM it_members im
    JOIN users u ON im.user_id = u.id
    WHERE im.category = ? AND im.is_backup = 0
  `).get(category);
  
  if (!itMember) {
    const backupMember = db.prepare(`
      SELECT im.*, u.id as user_id, u.name
      FROM it_members im
      JOIN users u ON im.user_id = u.id
      WHERE im.is_backup = 1
      LIMIT 1
    `).get();
    
    return backupMember || null;
  }
  
  const currentLoad = db.prepare(`
    SELECT COUNT(*) as count FROM tickets 
    WHERE assigned_to = ? AND status NOT IN ('Completed', 'Cancelled')
  `).get(itMember.user_id).count;
  
  if (currentLoad >= itMember.max_tickets) {
    const backupMember = db.prepare(`
      SELECT im.*, u.id as user_id, u.name
      FROM it_members im
      JOIN users u ON im.user_id = u.id
      WHERE im.is_backup = 1
      LIMIT 1
    `).get();
    
    return backupMember || itMember;
  }
  
  return itMember;
}

module.exports = { assignTicket };
