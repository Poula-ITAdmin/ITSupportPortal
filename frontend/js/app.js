const API_URL = '/api';

const SUB_DEPARTMENTS = {
  'Hospital': ['Accounting', 'Nursing', 'Pharmacy', 'Medical Records', 'Treasury', 'Management', 'Radiology', 'Laboratory', 'Emergency', 'Surgery', 'Pediatrics', 'ICU', 'Cardiology', 'Orthopedics', 'Gynecology', 'Physiotherapy', 'Dietary', 'Housekeeping', 'Maintenance', 'IT'],
  'Mission': ['Administration', 'Finance', 'HR', 'Programs', 'Outreach', 'Community Health', 'Training', 'Logistics', 'Procurement', 'Monitoring & Evaluation']
};

const SUB_DEPARTMENTS_AR = {
  'Hospital': ['المحاسبة', 'التمريض', 'الصيدلة', 'السجلات الطبية', 'الخزينة', 'الإدارة', 'الأشعة', 'المختبر', 'الطوارئ', 'الجراحة', 'طب الأطفال', 'العناية المركزة', 'أمراض القلب', 'العظام', 'النساء والتوليد', 'الفيزيotherapy', 'التغذية', 'النظافة', 'الصيانة', 'تكنولوجيا المعلومات'],
  'Mission': ['الإدارة', 'المالية', 'الموارد البشرية', 'البرامج', 'التواصل المجتمعي', 'الصحة المجتمعية', 'التدريب', 'اللوجستيات', 'المشتريات', 'المتابعة والتقييم']
};

let currentLanguage = localStorage.getItem('language') || 'en';

const translations = {
  en: {
    portalTitle: 'IT Support Portal',
    navHome: 'Home',
    navMyTickets: 'My Tickets',
    navDashboard: 'Dashboard',
    navLogin: 'Login',
    navLogout: 'Logout',
    heroTitle: 'How can we help you today?',
    heroSubtitle: 'Select a category below to report your issue',
    categories: {
      'Devices': 'Devices',
      'Personal Device': 'Personal Device',
      'Medical Device': 'Medical Device',
      'Software': 'Software Issue',
      'Access': 'Access / Accounts',
      'Maintenance & Repairs': 'Maintenance & Repairs'
    },
    categoryDesc: {
      'Devices': 'Laptop, printer, monitor, network issues',
      'Personal Device': 'BYOD issues, personal laptop, mobile devices',
      'Medical Device': 'Medical equipment, diagnostic devices, patient monitors',
      'Software': 'ERP problems, Windows, application errors',
      'Access': 'Password reset, permissions, access request',
      'Maintenance & Repairs': 'Scheduled maintenance, repairs, equipment servicing'
    },
    formTitle: 'Issue',
    yourName: 'Your Name',
    mainDepartment: 'Main Department',
    subDepartment: 'Sub-Department',
    selectDepartment: 'Select department',
    selectSubDepartment: 'Select sub-department',
    email: 'Email',
    phone: 'Phone Extension',
    issueTitle: 'Issue Title',
    issueTitlePlaceholder: 'Brief description of the issue',
    description: 'Description',
    descriptionPlaceholder: 'Please describe your issue in detail',
    urgency: 'Urgency Level',
    urgencyLow: 'Low - Can wait',
    urgencyMedium: 'Medium - Needs attention',
    urgencyHigh: 'High - Urgent',
    submit: 'Submit Ticket',
    cancel: 'Cancel',
    myTickets: 'My Tickets',
    dashboard: 'IT Dashboard',
    admin: 'Admin Panel',
    open: 'Open',
    inProgress: 'In Progress',
    completed: 'Completed',
    total: 'Total',
    filterCategory: 'All Categories',
    filterStatus: 'All Statuses',
    filterUrgency: 'All Priorities',
    backToDashboard: '← Back to Dashboard',
    updateStatus: 'Update Status',
    status: 'Status',
    reassignTo: 'Reassign To',
    unassigned: 'Unassigned',
    notes: 'Notes',
    notesPlaceholder: 'Add notes about this update...',
    updateTicket: 'Update Ticket',
    activityHistory: 'Activity History',
    loginTitle: 'Login',
    registerTitle: 'Register',
    loginBtn: 'Login',
    registerBtn: 'Register',
    noAccount: "Don't have an account? Register",
    hasAccount: 'Already have an account? Login',
    password: 'Password',
    registerFields: 'Full Name',
    noTickets: 'No tickets yet',
    noTicketsDesc: 'Submit your first ticket from the home page',
    noTicketsFound: 'No tickets found',
    assignedTo: 'Assigned To',
    submittedBy: 'Submitted By',
    category: 'Category',
    created: 'Created',
    deviceType: 'Device Type',
    assetNumber: 'Asset Number',
    deviceWorking: 'Device Working',
    software: 'Software',
    errorMessage: 'Error Message',
    application: 'Application/System',
    currentRole: 'Current Role',
    requiredPermissions: 'Required Permissions',
    equipmentName: 'Equipment/System Name',
    equipmentLocation: 'Location',
    maintenanceType: 'Maintenance Type',
    scheduledDate: 'Scheduled Date',
    deviceOwner: 'Device Owner',
    deviceName: 'Device Name',
    deviceSerial: 'Device ID / Serial Number',
    medicalDept: 'Department',
    issueDesc: 'Issue Description',
    teamWorkload: 'IT Team Workload',
    thName: 'Name',
    thSpecialty: 'Specialty',
    thActive: 'Active Tickets',
    thResolved: 'Resolved',
    allTickets: 'All Tickets',
    filterStatus: 'All Statuses',
    totalTickets: 'Total Tickets',
    inProgress: 'In Progress'
  },
  ar: {
    portalTitle: 'بوابة الدعم الفني',
    navHome: 'الرئيسية',
    navMyTickets: 'تذاكري',
    navDashboard: 'لوحة التحكم',
    navLogin: 'تسجيل الدخول',
    navLogout: 'تسجيل الخروج',
    heroTitle: 'كيف يمكننا مساعدتك اليوم؟',
    heroSubtitle: 'اختر فئة أدناه للإبلاغ عن مشكلتك',
    categories: {
      'Devices': 'الأجهزة',
      'Personal Device': 'الجهاز الشخصي',
      'Medical Device': 'الجهاز الطبي',
      'Software': 'مشكلة برمجية',
      'Access': 'الحصول على / حسابات',
      'Maintenance & Repairs': 'الصيانة والإصلاح'
    },
    categoryDesc: {
      'Devices': 'مشاكل الكمبيوتر المحمول والطابعة والشاشة والشبكة',
      'Personal Device': 'مشاكل الأجهزة الشخصية والمحمولة',
      'Medical Device': 'المعدات الطبية وأجهزة التشخيص',
      'Software': 'مشاكل نظام ERP والتطبيقات',
      'Access': 'إعادة تعيين كلمة المرور والصلاحيات',
      'Maintenance & Repairs': 'الصيانة المجدولة وإصلاح المعدات'
    },
    formTitle: 'مشكلة',
    yourName: 'اسمك',
    mainDepartment: 'القسم الرئيسي',
    subDepartment: 'القسم الفرعي',
    selectDepartment: 'اختر القسم',
    selectSubDepartment: 'اختر القسم الفرعي',
    email: 'البريد الإلكتروني',
    phone: 'رقم الهاتف الداخلي',
    issueTitle: 'عنوان المشكلة',
    issueTitlePlaceholder: 'وصف موجز للمشكلة',
    description: 'الوصف',
    descriptionPlaceholder: 'يرجى وصف مشكلتك بالتفصيل',
    urgency: 'مستوى الأولوية',
    urgencyLow: 'منخفض - يمكن الانتظار',
    urgencyMedium: 'متوسط - يحتاج اهتمام',
    urgencyHigh: 'عالي - مستعجل',
    submit: 'إرسال التذكرة',
    cancel: 'إلغاء',
    myTickets: 'تذاكري',
    dashboard: 'لوحة التحكم',
    admin: 'لوحة الإدارة',
    open: 'مفتوح',
    inProgress: 'قيد التنفيذ',
    completed: 'مكتمل',
    total: 'الإجمالي',
    filterCategory: 'جميع الفئات',
    filterStatus: 'جميع الحالات',
    filterUrgency: 'جميع الأولويات',
    backToDashboard: '← العودة للوحة التحكم',
    updateStatus: 'تحديث الحالة',
    status: 'الحالة',
    reassignTo: 'إعادة التعيين إلى',
    unassigned: 'غير معين',
    notes: 'ملاحظات',
    notesPlaceholder: 'أضف ملاحظات حول هذا التحديث...',
    updateTicket: 'تحديث التذكرة',
    activityHistory: 'سجل النشاط',
    loginTitle: 'تسجيل الدخول',
    registerTitle: 'تسجيل',
    loginBtn: 'تسجيل الدخول',
    registerBtn: 'تسجيل',
    noAccount: 'ليس لديك حساب؟ سجل الآن',
    hasAccount: 'لديك حساب بالفعل؟ تسجيل الدخول',
    password: 'كلمة المرور',
    registerFields: 'الاسم الكامل',
    noTickets: 'لا توجد تذاكر بعد',
    noTicketsDesc: 'أرسل أول تذكرة من الصفحة الرئيسية',
    noTicketsFound: 'لم يتم العثور على تذاكر',
    assignedTo: 'مكلف إلى',
    submittedBy: 'مقدم من',
    category: 'الفئة',
    created: 'تاريخ الإنشاء',
    deviceType: 'نوع الجهاز',
    assetNumber: 'رقم الأصل',
    deviceWorking: 'هل الجهاز يعمل',
    software: 'البرنامج',
    errorMessage: 'رسالة الخطأ',
    application: 'التطبيق/النظام',
    currentRole: 'الدور الحالي',
    requiredPermissions: 'الصلاحيات المطلوبة',
    equipmentName: 'اسم المعدات/النظام',
    equipmentLocation: 'الموقع',
    maintenanceType: 'نوع الصيانة',
    scheduledDate: 'التاريخ المجدول',
    deviceOwner: 'مالك الجهاز',
    deviceName: 'اسم الجهاز',
    deviceSerial: 'رقم الجهاز/الرقم التسلسلي',
    medicalDept: 'القسم',
    issueDesc: 'وصف المشكلة',
    teamWorkload: 'عبء عمل فريق تقنية المعلومات',
    thName: 'الاسم',
    thSpecialty: 'التخصص',
    thActive: 'التذاكر النشطة',
    thResolved: 'تم الحل',
    allTickets: 'جميع التذاكر',
    filterStatus: 'جميع الحالات',
    totalTickets: 'إجمالي التذاكر',
    inProgress: 'قيد التنفيذ'
  }
};

function t(key) {
  return translations[currentLanguage][key] || key;
}

function toggleLanguage() {
  currentLanguage = currentLanguage === 'en' ? 'ar' : 'en';
  localStorage.setItem('language', currentLanguage);
  applyLanguage();
}

function applyLanguage() {
  document.documentElement.dir = currentLanguage === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.lang = currentLanguage;
  
  document.getElementById('lang-toggle').textContent = currentLanguage === 'en' ? 'العربية' : 'English';
  
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[currentLanguage][key]) {
      el.textContent = translations[currentLanguage][key];
    }
  });
  
  // Translate hero section
  const heroTitle = document.querySelector('#home-page h1');
  if (heroTitle) heroTitle.textContent = currentLanguage === 'en' ? 'How can we help you today?' : 'كيف يمكننا مساعدتك اليوم؟';
  
  const heroSubtitle = document.querySelector('#home-page > div > p');
  if (heroSubtitle) heroSubtitle.textContent = currentLanguage === 'en' ? 'Select a category below to report your issue' : 'اختر فئة أدناه للإبلاغ عن مشكلتك';
  
  // Translate category cards
  document.querySelectorAll('.category-card h3').forEach((el, idx) => {
    const cats = currentLanguage === 'en' 
      ? ['Devices', 'Personal Device', 'Medical Device', 'Software', 'Access', 'Maintenance & Repairs']
      : ['الأجهزة', 'الجهاز الشخصي', 'الجهاز الطبي', 'مشكلة برمجية', 'الحصول على / حسابات', 'الصيانة والإصلاح'];
    if (cats[idx]) el.textContent = cats[idx];
  });
  
  document.querySelectorAll('.category-card p').forEach((el, idx) => {
    const descs = currentLanguage === 'en'
      ? ['Laptop, printer, monitor, network issues', 'BYOD issues, personal laptop, mobile devices', 'Medical equipment, diagnostic devices, patient monitors', 'ERP problems, Windows, application errors', 'Password reset, permissions, access request', 'Scheduled maintenance, repairs, equipment servicing']
      : ['مشاكل الكمبيوتر المحمول والطابعة والشاشة والشبكة', 'مشاكل الأجهزة الشخصية والمحمولة', 'المعدات الطبية وأجهزة التشخيص', 'مشاكل نظام ERP والتطبيقات', 'إعادة تعيين كلمة المرور والصلاحيات', 'الصيانة المجدولة وإصلاح المعدات'];
    if (descs[idx]) el.textContent = descs[idx];
  });
  
  // Translate form labels
  const labels = {
    'yourName': currentLanguage === 'en' ? 'Your Name' : 'اسمك',
    'mainDepartment': currentLanguage === 'en' ? 'Main Department' : 'القسم الرئيسي',
    'subDepartment': currentLanguage === 'en' ? 'Sub-Department' : 'القسم الفرعي',
    'email': currentLanguage === 'en' ? 'Email' : 'البريد الإلكتروني',
    'phone': currentLanguage === 'en' ? 'Phone Extension' : 'رقم الهاتف',
    'issueTitle': currentLanguage === 'en' ? 'Issue Title' : 'عنوان المشكلة',
    'description': currentLanguage === 'en' ? 'Description' : 'الوصف',
    'urgency': currentLanguage === 'en' ? 'Urgency Level' : 'مستوى الأولوية',
    'submit': currentLanguage === 'en' ? 'Submit Ticket' : 'إرسال التذكرة',
    'cancel': currentLanguage === 'en' ? 'Cancel' : 'إلغاء'
  };
  
  document.querySelectorAll('.form-label').forEach(el => {
    const text = el.textContent.trim();
    for (const [key, val] of Object.entries(labels)) {
      if (text === labels[key] || text === translations.en[key] || text === translations.ar[key]) {
        el.textContent = labels[key];
        break;
      }
    }
  });
  
  // Translate urgency options
  const urgencySelect = document.getElementById('urgency');
  if (urgencySelect) {
    urgencySelect.options[0].text = currentLanguage === 'en' ? 'Low - Can wait' : 'منخفض - يمكن الانتظار';
    urgencySelect.options[1].text = currentLanguage === 'en' ? 'Medium - Needs attention' : 'متوسط - يحتاج اهتمام';
    urgencySelect.options[2].text = currentLanguage === 'en' ? 'High - Urgent' : 'عالي - مستعجل';
  }
  
  // Translate auth page
  if (document.getElementById('auth-title')) {
    updateAuthUI();
  }
  
  if (document.getElementById('main-department')) {
    const deptSelect = document.getElementById('main-department');
    deptSelect.options[0].text = currentLanguage === 'en' ? 'Select department' : 'اختر القسم';
    updateSubDepartments();
  }
}

let currentUser = null;
let currentPage = 'home';
let selectedTicketId = null;
let isLoginMode = true;

function updateSubDepartments() {
  const mainDeptSelect = document.getElementById('main-department');
  const subDeptSelect = document.getElementById('sub-department');
  
  if (!mainDeptSelect || !subDeptSelect) return;
  
  const mainDept = mainDeptSelect.value;
  const depts = currentLanguage === 'en' ? SUB_DEPARTMENTS : SUB_DEPARTMENTS_AR;
  const placeholder = currentLanguage === 'en' ? 'Select sub-department' : 'اختر القسم الفرعي';
  subDeptSelect.innerHTML = `<option value="">${placeholder}</option>`;
  
  if (mainDept && depts[mainDept]) {
    const enDepts = SUB_DEPARTMENTS[mainDept];
    depts[mainDept].forEach((sub, index) => {
      const option = document.createElement('option');
      option.value = enDepts[index];
      option.textContent = sub;
      subDeptSelect.appendChild(option);
    });
  }
}

async function api(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers
  };
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.error || 'Something went wrong');
  }
  
  return data;
}

function navigate(page) {
  const user = localStorage.getItem('user');
  const userObj = user ? JSON.parse(user) : null;
  
  if (page === 'admin' && userObj?.role !== 'admin') {
    if (userObj?.role === 'it_staff') {
      page = 'dashboard';
    } else if (!userObj) {
      page = 'auth';
    } else {
      page = 'my-tickets';
    }
  }
  
  if ((page === 'dashboard' || page === 'my-tickets') && !userObj) {
    page = 'auth';
  }
  
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(`${page}-page`).classList.add('active');
  currentPage = page;
  
  if (page === 'my-tickets') loadMyTickets();
  if (page === 'dashboard') loadDashboard();
  if (page === 'admin') loadAdmin();
  
  applyLanguage();
  window.scrollTo(0, 0);
}

function selectCategory(category) {
  document.getElementById('category').value = category;
  document.getElementById('form-title').textContent = `${category} Issue`;
  
  document.querySelectorAll('.dynamic-fields').forEach(f => f.classList.remove('active'));
  
  if (category === 'Devices') {
    document.getElementById('devices-fields').classList.add('active');
  } else if (category === 'Personal Device') {
    document.getElementById('personal-device-fields').classList.add('active');
  } else if (category === 'Medical Device') {
    document.getElementById('medical-device-fields').classList.add('active');
  } else if (category === 'Software') {
    document.getElementById('software-fields').classList.add('active');
  } else if (category === 'Access') {
    document.getElementById('access-fields').classList.add('active');
  } else if (category === 'Maintenance & Repairs') {
    document.getElementById('maintenance-fields').classList.add('active');
  }
  
  navigate('ticket-form');
}

async function submitTicket(e) {
  e.preventDefault();
  
  const formData = {
    category: document.getElementById('category').value,
    title: document.getElementById('title').value,
    description: document.getElementById('description').value,
    urgency: document.getElementById('urgency').value,
    department: document.getElementById('main-department').value,
    sub_department: document.getElementById('sub-department').value,
    phone: document.getElementById('phone').value
  };
  
  if (formData.category === 'Devices') {
    formData.device_type = document.getElementById('device_type').value;
    formData.asset_number = document.getElementById('asset_number').value;
    formData.device_working = document.getElementById('device_working').value;
  } else if (formData.category === 'Personal Device') {
    formData.device_type = document.getElementById('device_type').value;
    formData.device_owner = document.getElementById('device_owner').value;
    formData.description = document.getElementById('personal_issue').value || formData.description;
  } else if (formData.category === 'Medical Device') {
    formData.medical_device_name = document.getElementById('medical_device_name').value;
    formData.medical_device_id = document.getElementById('medical_device_id').value;
    formData.medical_department = document.getElementById('medical_department').value;
    formData.urgency = document.getElementById('medical_urgency').value || formData.urgency;
    formData.description = document.getElementById('medical_issue').value || formData.description;
  } else if (formData.category === 'Software') {
    formData.software_name = document.getElementById('software_name').value;
    formData.error_message = document.getElementById('error_message').value;
  } else if (formData.category === 'Access') {
    formData.application_access = document.getElementById('application_access').value;
    formData.current_role = document.getElementById('current_role').value;
    formData.required_permissions = document.getElementById('required_permissions').value;
  } else if (formData.category === 'Maintenance & Repairs') {
    formData.equipment_name = document.getElementById('equipment_name').value;
    formData.equipment_location = document.getElementById('equipment_location').value;
    formData.maintenance_type = document.getElementById('maintenance_type').value;
    formData.scheduled_date = document.getElementById('scheduled_date').value;
    formData.description = document.getElementById('maintenance_description').value || formData.description;
  }
  
  try {
    const result = await api('/tickets', { method: 'POST', body: JSON.stringify(formData) });
    alert(`Ticket #${result.ticket_number} created successfully! You will receive a confirmation email shortly.`);
    document.getElementById('ticket-form').reset();
    navigate('home');
  } catch (error) {
    alert(error.message);
  }
}

async function loadMyTickets() {
  try {
    const tickets = await api('/tickets');
    const container = document.getElementById('my-tickets-list');
    
    if (tickets.length === 0) {
      container.innerHTML = '<div class="empty-state"><h3>No tickets yet</h3><p>Submit your first ticket from the home page</p></div>';
      return;
    }
    
    container.innerHTML = tickets.map(t => `
      <div class="ticket-item">
        <div class="ticket-id">#${t.ticket_number}</div>
        <div class="ticket-info">
          <h4>${t.title}</h4>
          <div class="ticket-meta">
            <span class="badge badge-${t.category.toLowerCase()}">${t.category}</span>
            <span>${new Date(t.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        <span class="badge badge-${t.status.toLowerCase().replace(' ', '-')}">${t.status}</span>
      </div>
    `).join('');
  } catch (error) {
    console.error(error);
  }
}

async function loadDashboard() {
  try {
    const stats = await api('/tickets/stats/dashboard');
    
    document.getElementById('dashboard-stats').innerHTML = `
      <div class="stat-card">
        <h3>Open</h3>
        <div class="value">${stats.open}</div>
      </div>
      <div class="stat-card">
        <h3>In Progress</h3>
        <div class="value">${stats.inProgress}</div>
      </div>
      <div class="stat-card">
        <h3>Completed</h3>
        <div class="value">${stats.completed}</div>
      </div>
      <div class="stat-card">
        <h3>Total</h3>
        <div class="value">${stats.total}</div>
      </div>
    `;
    
    const tickets = await api('/tickets');
    const categoryFilter = document.getElementById('filter-category').value;
    const statusFilter = document.getElementById('filter-status').value;
    const urgencyFilter = document.getElementById('filter-urgency').value;
    
    let filtered = tickets;
    if (categoryFilter) filtered = filtered.filter(t => t.category === categoryFilter);
    if (statusFilter) filtered = filtered.filter(t => t.status === statusFilter);
    if (urgencyFilter) filtered = filtered.filter(t => t.urgency === urgencyFilter);
    
    const container = document.getElementById('dashboard-tickets');
    
    if (filtered.length === 0) {
      container.innerHTML = '<div class="empty-state"><h3>No tickets found</h3></div>';
      return;
    }
    
    container.innerHTML = filtered.map(t => `
      <div class="ticket-item" onclick="viewTicket('${t.id}')" style="cursor: pointer;">
        <div class="ticket-id">#${t.ticket_number}</div>
        <div class="ticket-info">
          <h4>${t.title}</h4>
          <div class="ticket-meta">
            <span class="badge badge-${t.category.toLowerCase()}">${t.category}</span>
            <span>${t.user_name || 'Unknown'} - ${t.user_department || 'N/A'}</span>
            <span>Assigned: ${t.assigned_to_name || 'Unassigned'}</span>
          </div>
        </div>
        <div style="text-align: right;">
          <span class="badge badge-${t.urgency.toLowerCase()}">${t.urgency}</span>
          <span class="badge badge-${t.status.toLowerCase().replace(' ', '-')}" style="margin-left: 8px;">${t.status}</span>
        </div>
      </div>
    `).join('');
  } catch (error) {
    console.error(error);
  }
}

async function viewTicket(id) {
  selectedTicketId = id;
  
  try {
    const ticket = await api(`/tickets/${id}`);
    
    document.getElementById('update-status').value = ticket.status;
    document.getElementById('ticket-detail-content').innerHTML = `
      <div class="card">
        <div class="ticket-detail-header">
          <div>
            <h2>Ticket #${ticket.ticket_number}</h2>
            <p style="color: var(--text-light);">Created ${new Date(ticket.created_at).toLocaleString()}</p>
          </div>
          <div>
            <span class="badge badge-${ticket.urgency.toLowerCase()}" style="font-size: 14px; padding: 8px 16px;">${ticket.urgency}</span>
          </div>
        </div>
        
        <div class="ticket-detail-grid">
          <div class="detail-item">
            <label>Category</label>
            <span class="badge badge-${ticket.category.toLowerCase()}">${ticket.category}</span>
          </div>
          <div class="detail-item">
            <label>Status</label>
            <span class="badge badge-${ticket.status.toLowerCase().replace(' ', '-')}">${ticket.status}</span>
          </div>
          <div class="detail-item">
            <label>Assigned To</label>
            <span>${ticket.assigned_to_name || 'Unassigned'}</span>
          </div>
          <div class="detail-item">
            <label>Submitted By</label>
            <span>${ticket.user_name || 'Unknown'}</span>
          </div>
        </div>
        
        <div class="ticket-description">
          <h4 style="margin-bottom: 12px;">Description</h4>
          <p>${ticket.description || 'No description'}</p>
        </div>
        
        ${ticket.device_type ? `<div class="ticket-detail-grid">
          <div class="detail-item"><label>Device Type</label><span>${ticket.device_type}</span></div>
          <div class="detail-item"><label>Asset Number</label><span>${ticket.asset_number || 'N/A'}</span></div>
          <div class="detail-item"><label>Device Working</label><span>${ticket.device_working || 'N/A'}</span></div>
        </div>` : ''}
        
        ${ticket.software_name ? `<div class="ticket-detail-grid">
          <div class="detail-item"><label>Software</label><span>${ticket.software_name}</span></div>
          <div class="detail-item"><label>Error Message</label><span>${ticket.error_message || 'N/A'}</span></div>
        </div>` : ''}
        
        ${ticket.application_access ? `<div class="ticket-detail-grid">
          <div class="detail-item"><label>Application</label><span>${ticket.application_access}</span></div>
          <div class="detail-item"><label>Required Permissions</label><span>${ticket.required_permissions || 'N/A'}</span></div>
        </div>` : ''}
      </div>
    `;
    
    const timeline = document.getElementById('ticket-timeline');
    timeline.innerHTML = (ticket.logs || []).map(log => `
      <div class="timeline-item">
        <strong>${log.action}</strong>
        ${log.description ? `<p>${log.description}</p>` : ''}
        <small>${log.user_name || 'System'} - ${new Date(log.created_at).toLocaleString()}</small>
      </div>
    `).join('');
    
    const members = await api('/users/it-members');
    const assignSelect = document.getElementById('update-assign');
    assignSelect.innerHTML = '<option value="">Unassigned</option>' + 
      members.map(m => `<option value="${m.id}" ${ticket.assigned_to === m.id ? 'selected' : ''}>${m.name} (${m.category})</option>`).join('');
    
    navigate('ticket-detail');
  } catch (error) {
    alert(error.message);
  }
}

async function updateTicket() {
  const status = document.getElementById('update-status').value;
  const assigned_to = document.getElementById('update-assign').value;
  const notes = document.getElementById('update-notes').value;
  
  try {
    await api(`/tickets/${selectedTicketId}`, {
      method: 'PUT',
      body: JSON.stringify({ status, assigned_to: assigned_to || null, notes })
    });
    alert('Ticket updated successfully!');
    document.getElementById('update-notes').value = '';
    viewTicket(selectedTicketId);
  } catch (error) {
    alert(error.message);
  }
}

async function loadAdmin() {
  try {
    const stats = await api('/admin/stats');
    
    document.getElementById('admin-stats').innerHTML = `
      <div class="stat-card">
        <h3 data-i18n="totalTickets">Total Tickets</h3>
        <div class="value">${stats.totalTickets}</div>
      </div>
      <div class="stat-card">
        <h3 data-i18n="open">Open</h3>
        <div class="value">${stats.openTickets}</div>
      </div>
      <div class="stat-card">
        <h3 data-i18n="inProgress">In Progress</h3>
        <div class="value">${stats.inProgressTickets}</div>
      </div>
      <div class="stat-card">
        <h3 data-i18n="completed">Completed</h3>
        <div class="value">${stats.completedTickets}</div>
      </div>
    `;
    
    document.getElementById('workload-table').innerHTML = stats.workload.map(w => `
      <tr>
        <td>${w.name}</td>
        <td><span class="badge badge-${w.specialty ? w.specialty.toLowerCase().replace(' ', '-') : 'low'}">${w.specialty || 'General'}</span></td>
        <td>${w.active_tickets || 0}</td>
        <td>${w.resolved_tickets || 0}</td>
      </tr>
    `).join('');
    
    loadAdminTickets();
  } catch (error) {
    console.error(error);
  }
}

async function loadAdminTickets() {
  try {
    const tickets = await api('/tickets');
    const members = await api('/users/it-members');
    
    const categoryFilter = document.getElementById('admin-filter-category')?.value || '';
    const statusFilter = document.getElementById('admin-filter-status')?.value || '';
    
    let filtered = tickets;
    if (categoryFilter) filtered = filtered.filter(t => t.category === categoryFilter);
    if (statusFilter) filtered = filtered.filter(t => t.status === statusFilter);
    
    const container = document.getElementById('admin-tickets-list');
    
    if (filtered.length === 0) {
      container.innerHTML = '<div class="empty-state"><h3 data-i18n="noTicketsFound">No tickets found</h3></div>';
      return;
    }
    
    container.innerHTML = filtered.map(t => `
      <div class="ticket-item">
        <div class="ticket-id">#${t.ticket_number}</div>
        <div class="ticket-info">
          <h4>${t.title}</h4>
          <div class="ticket-meta">
            <span class="badge badge-${t.category.toLowerCase().replace(' ', '-')}">${t.category}</span>
            <span>${t.user_name || 'Unknown'} - ${t.sub_department || t.department || 'N/A'}</span>
          </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">
          <select class="form-select" style="width: 180px; padding: 6px;" onchange="reassignTicket('${t.id}', this.value)">
            <option value="">${currentLanguage === 'ar' ? 'إعادة التعيين' : 'Reassign'}</option>
            ${members.map(m => `<option value="${m.id}" ${t.assigned_to === m.id ? 'selected' : ''}>${m.name} (${m.category})</option>`).join('')}
          </select>
          <span class="badge badge-${t.status.toLowerCase().replace(' ', '-')}">${t.status}</span>
        </div>
      </div>
    `).join('');
  } catch (error) {
    console.error(error);
  }
}

async function reassignTicket(ticketId, assignedTo) {
  if (!assignedTo) return;
  try {
    await api(`/tickets/${ticketId}`, {
      method: 'PUT',
      body: JSON.stringify({ assigned_to: assignedTo, notes: 'Reassigned by admin' })
    });
    alert(currentLanguage === 'ar' ? 'تم إعادة التعيين بنجاح' : 'Reassigned successfully');
    loadAdminTickets();
  } catch (error) {
    alert(error.message);
  }
}

function showAuth(mode) {
  isLoginMode = mode === 'login';
  updateAuthUI();
  navigate('auth');
}

function updateAuthUI() {
  const authTitle = document.getElementById('auth-title');
  const authBtn = document.getElementById('auth-btn');
  const authToggle = document.getElementById('auth-toggle');
  const registerFields = document.getElementById('register-fields');
  const deptField = document.getElementById('dept-field');
  const authAlert = document.getElementById('auth-alert');
  
  if (!authTitle || !authBtn) return;
  
  authTitle.textContent = isLoginMode ? t('loginTitle') : t('registerTitle');
  authBtn.textContent = isLoginMode ? t('loginBtn') : t('registerBtn');
  if (authToggle) authToggle.textContent = isLoginMode ? t('hasAccount') : t('noAccount');
  if (registerFields) registerFields.style.display = isLoginMode ? 'none' : 'block';
  if (deptField) deptField.style.display = isLoginMode ? 'none' : 'block';
  if (authAlert) authAlert.innerHTML = '';
}

function toggleAuth() {
  isLoginMode = !isLoginMode;
  updateAuthUI();
}

async function handleAuth(e) {
  e.preventDefault();
  
  const email = document.getElementById('auth-email').value;
  const password = document.getElementById('auth-password').value;
  const name = document.getElementById('auth-name').value;
  const department = document.getElementById('auth-dept').value;
  
  try {
    const endpoint = isLoginMode ? '/auth/login' : '/auth/register';
    const body = isLoginMode ? { email, password } : { email, password, name, department };
    
    const result = await api(endpoint, { method: 'POST', body: JSON.stringify(body) });
    
    if (isLoginMode) {
      localStorage.setItem('token', result.token);
      localStorage.setItem('user', JSON.stringify(result.user));
      currentUser = result.user;
      updateUI();
      navigate('home');
    } else {
      alert('Registration successful! Please login.');
      toggleAuth();
    }
  } catch (error) {
    document.getElementById('auth-alert').innerHTML = `<div class="alert alert-error">${error.message}</div>`;
  }
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  currentUser = null;
  updateUI();
  navigate('home');
}

function updateUI() {
  const user = localStorage.getItem('user');
  const userObj = user ? JSON.parse(user) : null;
  currentUser = userObj;
  
  const isLoggedIn = !!userObj;
  const isAdmin = userObj?.role === 'admin';
  const isITStaff = userObj?.role === 'it_staff';
  
  document.getElementById('login-link').style.display = isLoggedIn ? 'none' : 'inline-flex';
  document.getElementById('logout-link').style.display = isLoggedIn ? 'inline-flex' : 'none';
  document.getElementById('my-tickets-link').style.display = isLoggedIn ? 'inline-flex' : 'none';
  document.getElementById('dashboard-link').style.display = isLoggedIn ? 'inline-flex' : 'none';
  document.getElementById('admin-link').style.display = isAdmin ? 'inline-flex' : 'none';
  
  if (userObj) {
    document.getElementById('user-name').textContent = userObj.name;
    document.getElementById('user-name-input').value = userObj.name;
    document.getElementById('email').value = userObj.email;
    if (userObj.department) document.getElementById('department').value = userObj.department;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateUI();
  applyLanguage();
});
