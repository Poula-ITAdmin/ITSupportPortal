const axios = require('axios');

const PLANNER_API = 'https://graph.microsoft.com/v1.0/planner/tasks';
const GRAPH_API = 'https://graph.microsoft.com/v1.0';

async function createPlannerTask(ticket, assignedTo) {
  const accessToken = process.env.MS_GRAPH_TOKEN;
  
  if (!accessToken) {
    throw new Error('MS Graph token not configured');
  }
  
  const planId = process.env.PLANNER_PLAN_ID;
  const bucketId = process.env.PLANNER_BUCKET_ID;
  
  if (!planId || !bucketId) {
    throw new Error('Planner plan or bucket not configured');
  }
  
  const task = {
    title: `[Ticket #${ticket.ticket_number}] ${ticket.title}`,
    bucketId: bucketId,
    planId: planId,
    assignments: {}
  };
  
  if (assignedTo) {
    const itMemberEmail = `${assignedTo.name.toLowerCase().replace(' ', '.')}@company.com`;
    task.assignments[process.env.MS_USER_ID] = {
      '@odata.type': '#microsoft.graph.plannerAssignment',
      assignedBy: process.env.MS_USER_ID
    };
  }
  
  try {
    const response = await axios.post(PLANNER_API, task, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Planner API error:', error.response?.data || error.message);
    throw error;
  }
}

async function updatePlannerTask(ticket) {
  if (!ticket.planner_task_id) return;
  
  const accessToken = process.env.MS_GRAPH_TOKEN;
  
  if (!accessToken) {
    throw new Error('MS Graph token not configured');
  }
  
  const statusMap = {
    'Open': 'notStarted',
    'In Progress': 'inProgress',
    'Pending User': 'pendingInput',
    'Escalated': 'inProgress',
    'Completed': 'completed'
  };
  
  try {
    await axios.patch(
      `${PLANNER_API}/${ticket.planner_task_id}`,
      { percentComplete: ticket.status === 'Completed' ? 100 : 0 },
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
  } catch (error) {
    console.error('Planner update error:', error.response?.data || error.message);
    throw error;
  }
}

async function getPlannerTasks() {
  const accessToken = process.env.MS_GRAPH_TOKEN;
  
  if (!accessToken) {
    throw new Error('MS Graph token not configured');
  }
  
  try {
    const response = await axios.get(PLANNER_API, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.data.value;
  } catch (error) {
    console.error('Planner get error:', error.response?.data || error.message);
    throw error;
  }
}

module.exports = { createPlannerTask, updatePlannerTask, getPlannerTasks };
