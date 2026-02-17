const nodemailer = require('nodemailer');

let transporter = null;

function getTransporter() {
  if (transporter) return transporter;
  
  transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST || 'smtp.ethereal.email',
    port: process.env.SMTP_PORT || 587,
    secure: false,
    auth: {
      user: process.env.SMTP_USER || 'test@ethereal.email',
      pass: process.env.SMTP_PASS || 'testpass'
    }
  });
  
  return transporter;
}

async function sendEmail({ to, subject, html, text }) {
  const t = getTransporter();
  
  try {
    const info = await t.sendMail({
      from: process.env.SMTP_FROM || '"IT Support" <itsupport@company.com>',
      to,
      subject,
      html,
      text: text || html.replace(/<[^>]*>/g, '')
    });
    
    console.log('Email sent:', info.messageId);
    return info;
  } catch (error) {
    console.error('Email error:', error.message);
    throw error;
  }
}

module.exports = { sendEmail };
