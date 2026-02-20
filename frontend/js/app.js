const API_URL = '/api';

const SUB_DEPARTMENTS = {
  'Hospital': ['Accounting', 'Nursing', 'Pharmacy', 'Medical Records', 'Treasury', 'Management', 'Radiology', 'Laboratory', 'Emergency', 'Surgery', 'Pediatrics', 'ICU', 'Cardiology', 'Orthopedics', 'Gynecology', 'Physiotherapy', 'Dietary', 'Housekeeping', 'Maintenance', 'IT'],
  'Mission': ['Administration', 'Finance', 'HR', 'Programs', 'Outreach', 'Community Health', 'Training', 'Logistics', 'Procurement', 'Monitoring & Evaluation']
};

const SUB_DEPARTMENTS_AR = {
  'Hospital': ['المحاسبة', 'التمريض', 'الصيدلة', 'السجلات الطبية', 'الخزينة', 'الإدارة', 'الأشعة', 'المختبر', 'الطوارئ', 'الجراحة', 'طب الأطفال', 'العناية المركزة', 'أمراض القلب', 'العظام', 'النساء والتوليد', 'الفيزيotherapy', 'التغذية', 'النظافة', 'الصيانة', 'تكنولوجيا المعلومات'],
  'Mission': ['الإدارة', 'المالية', 'الموارد البشرية', 'البرامج', 'التواصل المجتمعي', 'الصحة المجتمعية', 'التدريب', 'اللوجستيات', 'المشتريات', 'المتابعة والتقييم']
};

const CATEGORY_FIELDS = {
  'Devices': [
    { key: 'device_type', type: 'select', label: 'Device Type', options: ['Laptop','Desktop','Printer','Monitor','Network','Other'] },
    { key: 'asset_number', type: 'text', label: 'Asset Number', placeholder: 'e.g., LAP-001' },
    { key: 'device_working', type: 'select', label: 'Is the device working?', options: ['','Yes','No'] }
  ],
  'Personal Device': [
    { key: 'device_type', type: 'select', label: 'Device Type', options: ['Personal Laptop','Personal Desktop','Mobile Phone','Tablet','Other'] },
    { key: 'device_owner', type: 'text', label: 'Device Owner', placeholder: 'Employee name' },
    { key: 'personal_issue', type: 'textarea', label: 'Issue Description' }
  ],
  'Medical Device': [
    { key: 'medical_device_name', type: 'text', label: 'Device Name', placeholder: 'e.g., MRI Scanner' },
    { key: 'medical_device_id', type: 'text', label: 'Device ID / Serial Number' },
    { key: 'medical_department', type: 'text', label: 'Department', placeholder: 'e.g., ICU' },
    { key: 'medical_urgency', type: 'select', label: 'Urgency Level', options: ['','Critical','High','Medium','Low'] },
    { key: 'medical_issue', type: 'textarea', label: 'Issue Description' }
  ],
  'Software': [
    { key: 'software_name', type: 'text', label: 'Software Name' },
    { key: 'error_message', type: 'text', label: 'Error Message (if any)' }
  ],
  'Access': [
    { key: 'application_access', type: 'text', label: 'Application/System' },
    { key: 'current_role', type: 'text', label: 'Current Role' },
    { key: 'required_permissions', type: 'text', label: 'Required Permissions' }
  ],
  'Maintenance & Repairs': [
    { key: 'equipment_name', type: 'text', label: 'Equipment/System Name' },
    { key: 'equipment_location', type: 'text', label: 'Location' },
    { key: 'maintenance_type', type: 'select', label: 'Maintenance Type', options: ['','Preventive','Corrective','Inspection','Installation','Upgrade'] },
    { key: 'scheduled_date', type: 'date', label: 'Scheduled Date (if applicable)' },
    { key: 'maintenance_description', type: 'textarea', label: 'Issue Description' }
  ]
};

function fieldId(category, key) {
  const categoryKey = category.toLowerCase().replace(/[^a-z0-9]+/g, '_');
  return `${categoryKey}_${key}`;
}

function renderCategoryFields(category) {
  const container = document.getElementById('category-dynamic-container');
  if (!container) return;
  container.innerHTML = '';
  if (!category || !CATEGORY_FIELDS[category]) return;

  const fields = CATEGORY_FIELDS[category];
  const categoryKey = category.toLowerCase().replace(/[^a-z0-9]+/g, '_');

  fields.forEach(f => {
    const id = fieldId(category, f.key);
    let html = '';
    if (f.type === 'select') {
      html += `<div class="form-group"><label class="form-label">${f.label}</label>`;
      html += `<select class="form-select" id="${id}">`;
      (f.options || []).forEach(opt => {
        const val = opt === '' ? '' : opt;
        html += `<option value="${val}">${opt || ''}</option>`;
      });
      html += `</select></div>`;
    } else if (f.type === 'textarea') {
      html += `<div class="form-group"><label class="form-label">${f.label}</label>`;
      html += `<textarea class="form-textarea" id="${id}" placeholder="${f.placeholder || ''}"></textarea></div>`;
    } else {
      html += `<div class="form-group"><label class="form-label">${f.label}</label>`;
      html += `<input type="${f.type || 'text'}" class="form-input" id="${id}" placeholder="${f.placeholder || ''}"></div>`;
    }

    container.insertAdjacentHTML('beforeend', html);
  });
}

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
  
  const text = await response.text();
  
  let data;
  try {
    data = JSON.parse(text);
  } catch (e) {
    throw new Error(`Server error: ${text.substring(0, 100)}`);
  }
  
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
  
  if ((page === 'dashboard' || page === 'my-tickets' || page === 'admin-users' || page === 'admin-tickets' || page === 'chat' || page === 'calendar') && !userObj) {
    page = 'auth';
  }
  
  if (page === 'admin' && userObj?.role === 'admin') {
    page = 'admin';
  }
  
  if ((page === 'admin-users' || page === 'admin-tickets') && userObj?.role !== 'admin') {
    page = 'admin';
  }
  
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(`${page}-page`).classList.add('active');
  currentPage = page;
  
  if (page === 'my-tickets') loadMyTickets();
  if (page === 'dashboard') loadDashboard();
  if (page === 'admin') loadAdmin();
  if (page === 'admin-users') loadAdminUsers();
  if (page === 'admin-tickets') loadAdminTickets();
  if (page === 'chat') {
    loadChatChannels();
  }
  if (page === 'calendar') {
    loadCalendar();
  }
  
  applyLanguage();
  window.scrollTo(0, 0);
}

function selectCategory(category) {
  document.getElementById('category').value = category;
  document.getElementById('form-title').textContent = `${category} Issue`;
  renderCategoryFields(category);
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
  
  // collect category-specific fields from dynamically rendered inputs
  const category = formData.category;
  if (category && CATEGORY_FIELDS[category]) {
    CATEGORY_FIELDS[category].forEach(f => {
      const id = fieldId(category, f.key);
      const el = document.getElementById(id);
      if (!el) return;

      const val = el.value;
      // map textarea personal_issue to description if empty
      if (f.key === 'personal_issue' || f.key === 'medical_issue' || f.key === 'maintenance_description') {
        if (val) formData.description = val;
      }

      // for urgency overrides
      if (f.key === 'medical_urgency' && val) {
        formData.urgency = val;
      }

      // assign value to payload using the field key
      formData[f.key] = val;
    });
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
    console.error('loadAdmin error:', error);
    alert('Error loading admin: ' + error.message);
  }
}

async function loadAdminTickets() {
  try {
    const container = document.getElementById('admin-tickets-list');
    if (!container) return;
    
    const tickets = await api('/tickets');
    const members = await api('/users/it-members');
    
    const categoryFilterEl = document.getElementById('admin-filter-category');
    const statusFilterEl = document.getElementById('admin-filter-status');
    const categoryFilter = categoryFilterEl?.value || '';
    const statusFilter = statusFilterEl?.value || '';
    
    let filtered = tickets;
    if (categoryFilter) filtered = filtered.filter(t => t.category === categoryFilter);
    if (statusFilter) filtered = filtered.filter(t => t.status === statusFilter);
    
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
            <span class="badge badge-${t.category ? t.category.toLowerCase().replace(' ', '-') : 'low'}">${t.category || 'N/A'}</span>
            <span>${t.user_name || 'Unknown'} - ${t.sub_department || t.department || 'N/A'}</span>
          </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">
          <select class="form-select" style="width: 180px; padding: 6px;" onchange="reassignTicket('${t.id}', this.value)">
            <option value="">${currentLanguage === 'ar' ? 'إعادة التعيين' : 'Reassign'}</option>
            ${members.map(m => `<option value="${m.id}" ${t.assigned_to === m.id ? 'selected' : ''}>${m.name} (${m.category})</option>`).join('')}
          </select>
          <span class="badge badge-${t.status ? t.status.toLowerCase().replace(' ', '-') : 'low'}">${t.status || 'N/A'}</span>
        </div>
      </div>
    `).join('');
  } catch (error) {
    console.error('loadAdminTickets error:', error);
    const container = document.getElementById('admin-tickets-list');
    if (container) {
      container.innerHTML = `<div class="empty-state"><h3>Error: ${error.message}</h3></div>`;
    }
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
  
  const emailEl = document.getElementById('auth-email');
  const passwordEl = document.getElementById('auth-password');
  const nameEl = document.getElementById('auth-name');
  const deptEl = document.getElementById('auth-dept');
  
  if (!emailEl || !passwordEl) return;
  
  const email = emailEl.value;
  const password = passwordEl.value;
  const name = nameEl ? nameEl.value : '';
  const department = deptEl ? deptEl.value : '';
  
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
  
  const loginLink = document.getElementById('login-link');
  const userDropdown = document.getElementById('user-dropdown');
  
  if (loginLink) loginLink.style.display = isLoggedIn ? 'none' : 'inline-flex';
  if (userDropdown) userDropdown.style.display = isLoggedIn ? 'inline-block' : 'none';
  
  if (userObj) {
    const userNameEl = document.getElementById('user-name');
    const userNameInput = document.getElementById('user-name-input');
    const emailEl = document.getElementById('email');
    const deptEl = document.getElementById('main-department');
    const dropdownUserInfo = document.getElementById('dropdown-user-info');
    const navMyTickets = document.getElementById('nav-my-tickets');
    const navDashboard = document.getElementById('nav-dashboard');
    const adminMenuItems = document.getElementById('admin-menu-items');
    
    if (userNameEl) userNameEl.textContent = userObj.name;
    if (userNameInput) userNameInput.value = userObj.name;
    if (emailEl) emailEl.value = userObj.email;
    if (deptEl && userObj.department) deptEl.value = userObj.department;
    
    if (dropdownUserInfo) {
      const roleLabel = userObj.role === 'admin' ? 'Administrator' : 
                        userObj.role === 'it_staff' ? 'IT Staff' : 'Employee';
      dropdownUserInfo.innerHTML = `<strong>${userObj.name}</strong><br><small>${roleLabel}</small>`;
    }
    
    if (navMyTickets) navMyTickets.style.display = 'inline-block';
    const navChat = document.getElementById('nav-chat');
    if (navChat) navChat.style.display = 'inline-block';
    const navCalendar = document.getElementById('nav-calendar');
    if (navCalendar) navCalendar.style.display = 'inline-block';
    if (navDashboard) navDashboard.style.display = (isITStaff || isAdmin) ? 'inline-block' : 'none';
    if (adminMenuItems) adminMenuItems.style.display = isAdmin ? 'block' : 'none';
  } else {
    const userNameEl = document.getElementById('user-name');
    if (userNameEl) userNameEl.textContent = '';
  }
}

function toggleUserDropdown() {
  const menu = document.getElementById('user-menu');
  if (menu) {
    menu.classList.toggle('show');
  }
}

document.addEventListener('click', (e) => {
  const userDropdown = document.getElementById('user-dropdown');
  const menu = document.getElementById('user-menu');
  if (userDropdown && menu && !userDropdown.contains(e.target)) {
    menu.classList.remove('show');
  }
});

document.addEventListener('DOMContentLoaded', () => {
  updateUI();
  applyLanguage();
  
  const hash = window.location.hash;
  if (hash.includes('reset-password')) {
    const params = new URLSearchParams(hash.split('?')[1]);
    const token = params.get('token');
    if (token) {
      localStorage.setItem('reset_token', token);
      navigate('reset-password');
    }
  }
});

function showForgotPassword() {
  navigate('forgot-password-page');
}

async function handleForgotPassword(e) {
  e.preventDefault();
  const email = document.getElementById('fp-email').value;
  const alertEl = document.getElementById('fp-alert');
  
  try {
    const result = await api('/auth/forgot-password', { method: 'POST', body: JSON.stringify({ email }) });
    alertEl.innerHTML = `<div class="alert alert-success">${result.message}</div>`;
  } catch (error) {
    alertEl.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
  }
}

async function handleResetPassword(e) {
  e.preventDefault();
  const password = document.getElementById('rp-password').value;
  const confirm = document.getElementById('rp-confirm').value;
  const alertEl = document.getElementById('rp-alert');
  const token = localStorage.getItem('reset_token');
  
  if (password !== confirm) {
    alertEl.innerHTML = `<div class="alert alert-error">Passwords do not match</div>`;
    return;
  }
  
  try {
    await api('/auth/reset-password', { method: 'POST', body: JSON.stringify({ token, new_password: password }) });
    alert('Password reset successfully! Please login.');
    localStorage.removeItem('reset_token');
    navigate('auth');
  } catch (error) {
    alertEl.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
  }
}

function showAddUserForm() {
  document.getElementById('add-user-form').style.display = 'block';
}

function hideAddUserForm() {
  document.getElementById('add-user-form').style.display = 'none';
  document.getElementById('user-form').reset();
}

function toggleCategoryField() {
  const role = document.getElementById('new-user-role').value;
  const categoryField = document.getElementById('category-field');
  categoryField.style.display = role === 'it_staff' ? 'block' : 'none';
}

async function loadAdminUsers() {
  try {
    const users = await api('/admin/users');
    const members = await api('/users/it-members');
    
    const container = document.getElementById('users-list');
    
    container.innerHTML = `
      <table class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Department</th>
            <th>Category</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${users.map(u => {
            const member = members.find(m => m.id === u.id);
            return `
              <tr>
                <td>${u.name}</td>
                <td>${u.email}</td>
                <td><span class="badge badge-${u.role === 'admin' ? 'high' : u.role === 'it_staff' ? 'medium' : 'low'}">${u.role}</span></td>
                <td>${u.department || '-'}</td>
                <td>${member?.category || '-'}</td>
                <td>
                  <button class="btn btn-sm" onclick="editUser('${u.id}')">Edit</button>
                  <button class="btn btn-sm btn-danger" onclick="deleteUser('${u.id}')">Delete</button>
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    `;
  } catch (error) {
    console.error('loadAdminUsers error:', error);
  }
}

async function handleUserSubmit(e) {
  e.preventDefault();
  
  const userData = {
    name: document.getElementById('new-user-name').value,
    email: document.getElementById('new-user-email').value,
    password: document.getElementById('new-user-password').value,
    role: document.getElementById('new-user-role').value,
    department: document.getElementById('new-user-dept').value
  };
  
  if (userData.role === 'it_staff') {
    userData.category = document.getElementById('new-user-category').value;
  }
  
  try {
    await api('/admin/users', { method: 'POST', body: JSON.stringify(userData) });
    alert('User created successfully!');
    hideAddUserForm();
    loadAdminUsers();
  } catch (error) {
    alert(error.message);
  }
}

async function deleteUser(userId) {
  if (!confirm('Are you sure you want to delete this user?')) return;
  
  try {
    await api(`/admin/users/${userId}`, { method: 'DELETE' });
    loadAdminUsers();
  } catch (error) {
    alert(error.message);
  }
}

let allUsersData = [];
let allMembersData = [];

async function editUser(userId) {
  try {
    const users = await api('/admin/users');
    const members = await api('/users/it-members');
    allUsersData = users;
    allMembersData = members;
    
    const user = users.find(u => u.id === userId);
    const member = members.find(m => m.id === userId);
    
    if (!user) {
      alert('User not found');
      return;
    }
    
    document.getElementById('edit-user-id').value = userId;
    document.getElementById('edit-user-name').value = user.name;
    document.getElementById('edit-user-email').value = user.email;
    document.getElementById('edit-user-role').value = user.role;
    document.getElementById('edit-user-dept').value = user.department || '';
    document.getElementById('edit-user-password').value = '';
    
    toggleEditCategoryField();
    
    if (member) {
      document.getElementById('edit-user-category').value = member.category;
    }
    
    document.getElementById('edit-user-form').style.display = 'block';
    document.getElementById('add-user-form').style.display = 'none';
  } catch (error) {
    alert(error.message);
  }
}

function hideEditUserForm() {
  document.getElementById('edit-user-form').style.display = 'none';
  document.getElementById('edit-user-form-submit').reset();
}

function toggleEditCategoryField() {
  const role = document.getElementById('edit-user-role').value;
  const categoryField = document.getElementById('edit-category-field');
  categoryField.style.display = role === 'it_staff' ? 'block' : 'none';
}

async function handleUserEdit(e) {
  e.preventDefault();
  
  const userId = document.getElementById('edit-user-id').value;
  const userData = {
    name: document.getElementById('edit-user-name').value,
    email: document.getElementById('edit-user-email').value,
    role: document.getElementById('edit-user-role').value,
    department: document.getElementById('edit-user-dept').value
  };
  
  const password = document.getElementById('edit-user-password').value;
  if (password) {
    userData.password = password;
  }
  
  if (userData.role === 'it_staff') {
    userData.category = document.getElementById('edit-user-category').value;
  }
  
  try {
    await api(`/admin/users/${userId}`, { 
      method: 'PUT', 
      body: JSON.stringify(userData) 
    });
    alert('User updated successfully!');
    hideEditUserForm();
    loadAdminUsers();
  } catch (error) {
    alert(error.message);
  }
}

let chatChannels = [];
let currentChatChannel = null;
let chatPollInterval = null;

async function loadChatChannels() {
  try {
    chatChannels = await api('/chat/channels');
    renderChatChannels();
  } catch (error) {
    console.error('Error loading chat channels:', error);
  }
}

function renderChatChannels() {
  const container = document.getElementById('chat-channels-list');
  if (!container) return;
  
  const generalChannels = chatChannels.filter(c => c.channel_type === 'general');
  const teamChannels = chatChannels.filter(c => c.channel_type === 'team');
  const deptChannels = chatChannels.filter(c => c.channel_type === 'department');
  
  let html = '';
  
  if (generalChannels.length) {
    html += `<div class="chat-section-title">General</div>`;
    generalChannels.forEach(ch => {
      html += renderChannelItem(ch);
    });
  }
  
  if (teamChannels.length) {
    html += `<div class="chat-section-title">IT Teams</div>`;
    teamChannels.forEach(ch => {
      html += renderChannelItem(ch);
    });
  }
  
  if (deptChannels.length) {
    html += `<div class="chat-section-title">Departments</div>`;
    deptChannels.forEach(ch => {
      html += renderChannelItem(ch);
    });
  }
  
  container.innerHTML = html;
}

function renderChannelItem(ch) {
  const active = currentChatChannel === ch.id ? 'active' : '';
  const unread = ch.unread_count > 0 ? `<span class="unread-badge">${ch.unread_count}</span>` : '';
  return `<div class="chat-channel-item ${active}" onclick="selectChatChannel('${ch.id}')">
    <span>${ch.name}</span>
    ${unread}
  </div>`;
}

async function selectChatChannel(channelId) {
  currentChatChannel = channelId;
  const channel = chatChannels.find(c => c.id === channelId);
  
  document.getElementById('chat-channel-name').textContent = channel ? channel.name : 'Channel';
  renderChatChannels();
  await loadChatMessages(channelId);
  
  if (chatPollInterval) clearInterval(chatPollInterval);
  chatPollInterval = setInterval(() => {
    if (currentChatChannel) loadChatMessages(currentChatChannel, true);
  }, 5000);
}

async function loadChatMessages(channelId, silent = false) {
  try {
    const messages = await api(`/chat/channels/${channelId}/messages`);
    renderChatMessages(messages);
    if (!silent) loadChatChannels();
  } catch (error) {
    console.error('Error loading messages:', error);
  }
}

function renderChatMessages(messages) {
  const container = document.getElementById('chat-messages');
  if (!container) return;
  
  if (!messages.length) {
    container.innerHTML = '<div class="chat-empty">No messages yet. Start the conversation!</div>';
    return;
  }
  
  const currentUserId = JSON.parse(localStorage.getItem('user') || '{}').id;
  
  container.innerHTML = messages.map(msg => {
    const isOwn = msg.user_id === currentUserId;
    const time = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const roleBadge = msg.user_role === 'admin' ? ' <span style="background:#ef4444;color:white;padding:1px 4px;border-radius:3px;font-size:9px;">ADMIN</span>' : 
                     msg.user_role === 'it_staff' ? ' <span style="background:#2563eb;color:white;padding:1px 4px;border-radius:3px;font-size:9px;">IT</span>' : '';
    
    return `<div class="chat-message ${isOwn ? 'own' : 'other'}">
      <div class="chat-message-header">
        <span class="chat-message-name">${msg.user_name}${roleBadge}</span>
        <span class="chat-message-time">${time}</span>
      </div>
      <div class="chat-message-text">${escapeHtml(msg.message)}</div>
    </div>`;
  }).join('');
  
  container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function sendChatMessage() {
  if (!currentChatChannel) return;
  
  const input = document.getElementById('chat-message-input');
  const message = input.value.trim();
  if (!message) return;
  
  try {
    await api(`/chat/channels/${currentChatChannel}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message })
    });
    input.value = '';
    await loadChatMessages(currentChatChannel);
    await loadChatChannels();
  } catch (error) {
    alert(error.message);
  }
}

function handleChatKeyPress(e) {
  if (e.key === 'Enter') {
    sendChatMessage();
  }
}

let currentDate = new Date();
let calendarView = 'month';
let calendarEvents = [];
let selectedCategories = ['meeting', 'maintenance', 'training', 'deadline', 'vacation', 'ticket', 'other'];
let calendarCategories = [];

const categoryColors = {
  'meeting': '#2563eb',
  'maintenance': '#f59e0b',
  'training': '#10b981',
  'deadline': '#ef4444',
  'vacation': '#8b5cf6',
  'ticket': '#06b6d4',
  'other': '#64748b'
};

async function loadCalendar() {
  try {
    const events = await api('/calendar/events');
    calendarEvents = events;
    calendarCategories = await api('/calendar/categories');
    renderCalendar();
    renderCalendarCategories();
    renderUpcomingEvents();
  } catch (error) {
    console.error('Error loading calendar:', error);
  }
}

function renderCalendar() {
  const title = document.getElementById('calendar-title');
  const grid = document.getElementById('calendar-grid');
  
  if (calendarView === 'month') {
    renderMonthView(title, grid);
  } else if (calendarView === 'week') {
    renderWeekView(title, grid);
  } else {
    renderDayView(title, grid);
  }
}

function renderMonthView(title, grid) {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  
  title.textContent = new Date(year, month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const startDate = new Date(firstDay);
  startDate.setDate(startDate.getDate() - firstDay.getDay());
  
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  
  let html = dayNames.map(d => `<div class="calendar-day-header">${d}</div>`).join('');
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    
    const dateStr = date.toISOString().split('T')[0];
    const isOtherMonth = date.getMonth() !== month;
    const isToday = date.getTime() === today.getTime();
    
    const dayEvents = calendarEvents.filter(e => {
      const eventDate = new Date(e.start_time).toISOString().split('T')[0];
      return eventDate === dateStr && selectedCategories.includes(e.category);
    }).slice(0, 3);
    
    const moreCount = calendarEvents.filter(e => {
      const eventDate = new Date(e.start_time).toISOString().split('T')[0];
      return eventDate === dateStr && selectedCategories.includes(e.category);
    }).length - 3;
    
    let eventsHtml = dayEvents.map(e => `
      <div class="calendar-event" style="background: ${e.color || categoryColors[e.category] || '#2563eb'}" 
           onclick="openEvent('${e.id}'); event.stopPropagation();">
        ${e.title}
      </div>
    `).join('');
    
    if (moreCount > 0) {
      eventsHtml += `<div class="calendar-more">+${moreCount} more</div>`;
    }
    
    html += `<div class="calendar-day ${isOtherMonth ? 'other-month' : ''} ${isToday ? 'today' : ''}" 
                  onclick="openNewEvent('${dateStr}')">
      <div class="calendar-day-number">${date.getDate()}</div>
      ${eventsHtml}
    </div>`;
  }
  
  grid.innerHTML = html;
}

function renderWeekView(title, grid) {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const day = currentDate.getDate();
  const startOfWeek = new Date(year, month, day - currentDate.getDay());
  
  title.textContent = `Week of ${startOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
  
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  let headerHtml = dayNames.map((d, i) => {
    const date = new Date(startOfWeek);
    date.setDate(startOfWeek.getDate() + i);
    const isToday = date.getTime() === today.getTime();
    return `<div class="week-header-day ${isToday ? 'today' : ''}">
      <div>${d}</div>
      <div style="font-size: 18px;">${date.getDate()}</div>
    </div>`;
  }).join('');
  
  let bodyHtml = '';
  for (let i = 0; i < 7; i++) {
    const date = new Date(startOfWeek);
    date.setDate(startOfWeek.getDate() + i);
    const dateStr = date.toISOString().split('T')[0];
    
    const dayEvents = calendarEvents.filter(e => {
      const eventDate = new Date(e.start_time).toISOString().split('T')[0];
      return eventDate === dateStr && selectedCategories.includes(e.category);
    });
    
    let eventsHtml = dayEvents.map(e => `
      <div class="week-event" style="background: ${e.color || categoryColors[e.category] || '#2563eb'}"
           onclick="openEvent('${e.id}'); event.stopPropagation();">
        <strong>${e.title}</strong><br>
        ${formatEventTime(e)}
      </div>
    `).join('');
    
    bodyHtml += `<div class="week-column">${eventsHtml}</div>`;
  }
  
  grid.className = 'week-view';
  grid.innerHTML = `<div class="week-header">${headerHtml}</div><div class="week-body">${bodyHtml}</div>`;
}

function renderDayView(title, grid) {
  const dateStr = currentDate.toISOString().split('T')[0];
  title.textContent = currentDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  
  let html = '';
  for (let hour = 0; hour < 24; hour++) {
    const timeStr = `${hour.toString().padStart(2, '0')}:00`;
    const hourDate = new Date(currentDate);
    hourDate.setHours(hour, 0, 0, 0);
    const hourStr = hourDate.toISOString().slice(0, 13);
    
    const hourEvents = calendarEvents.filter(e => {
      const eventHour = new Date(e.start_time).getHours();
      return eventHour === hour && selectedCategories.includes(e.category);
    });
    
    let eventsHtml = hourEvents.map(e => `
      <div class="week-event" style="background: ${e.color || categoryColors[e.category] || '#2563eb'}"
           onclick="openEvent('${e.id}'); event.stopPropagation();">
        <strong>${e.title}</strong> - ${formatEventTime(e)}
      </div>
    `).join('');
    
    html += `<div class="time-slot">
      <div class="time-label">${timeStr}</div>
      <div class="time-events" onclick="openNewEvent('${dateStr}T${timeStr}:00')">${eventsHtml}</div>
    </div>`;
  }
  
  grid.className = 'day-view';
  grid.innerHTML = `<div class="day-schedule">${html}</div>`;
}

function formatEventTime(event) {
  const start = new Date(event.start_time);
  const end = event.end_time ? new Date(event.end_time) : null;
  
  if (event.all_day) return 'All Day';
  
  const timeStr = start.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  if (!end) return timeStr;
  
  const endStr = end.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  return `${timeStr} - ${endStr}`;
}

function renderCalendarCategories() {
  const container = document.getElementById('calendar-categories');
  if (!container) return;
  
  container.innerHTML = calendarCategories.map(cat => `
    <label class="calendar-category-item">
      <input type="checkbox" value="${cat.id}" ${selectedCategories.includes(cat.id) ? 'checked' : ''} 
             onchange="toggleCategory('${cat.id}')">
      <span class="calendar-category-dot" style="background: ${cat.color}"></span>
      <span>${cat.name}</span>
    </label>
  `).join('');
}

function renderUpcomingEvents() {
  const container = document.getElementById('calendar-upcoming');
  if (!container) return;
  
  const now = new Date();
  const upcoming = calendarEvents
    .filter(e => new Date(e.start_time) >= now && selectedCategories.includes(e.category))
    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
    .slice(0, 5);
  
  if (!upcoming.length) {
    container.innerHTML = '<p style="color: var(--text-light); font-size: 12px;">No upcoming events</p>';
    return;
  }
  
  container.innerHTML = upcoming.map(e => {
    const date = new Date(e.start_time);
    return `<div class="upcoming-event" style="background: ${e.color || categoryColors[e.category] || '#2563eb'}"
                   onclick="openEvent('${e.id}')">
      <div class="upcoming-event-time">${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</div>
      <div>${e.title}</div>
    </div>`;
  }).join('');
}

function changeMonth(delta) {
  currentDate.setMonth(currentDate.getMonth() + delta);
  renderCalendar();
}

function goToToday() {
  currentDate = new Date();
  renderCalendar();
}

function setCalendarView(view) {
  calendarView = view;
  document.querySelectorAll('.calendar-views .btn').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`view-${view}`).classList.add('active');
  renderCalendar();
}

function toggleCategory(cat) {
  if (selectedCategories.includes(cat)) {
    selectedCategories = selectedCategories.filter(c => c !== cat);
  } else {
    selectedCategories.push(cat);
  }
  renderCalendar();
  renderUpcomingEvents();
}

function openNewEvent(dateStr) {
  document.getElementById('event-modal').classList.add('show');
  document.getElementById('event-modal-title').textContent = 'New Event';
  document.getElementById('event-form').reset();
  document.getElementById('event-id').value = '';
  document.getElementById('delete-event-btn').style.display = 'none';
  
  const defaultStart = dateStr.includes('T') ? dateStr : `${dateStr}T09:00`;
  document.getElementById('event-start').value = defaultStart.slice(0, 16);
  
  const defaultEnd = dateStr.includes('T') ? dateStr : `${dateStr}T10:00`;
  document.getElementById('event-end').value = defaultEnd.slice(0, 16);
}

async function openEvent(eventId) {
  const event = calendarEvents.find(e => e.id === eventId);
  if (!event) return;
  
  document.getElementById('event-modal').classList.add('show');
  document.getElementById('event-modal-title').textContent = 'Edit Event';
  document.getElementById('event-id').value = event.id;
  document.getElementById('event-title').value = event.title;
  document.getElementById('event-category').value = event.category || 'other';
  document.getElementById('event-all-day').checked = event.all_day;
  document.getElementById('event-start').value = event.start_time.slice(0, 16);
  document.getElementById('event-end').value = event.end_time ? event.end_time.slice(0, 16) : '';
  document.getElementById('event-location').value = event.location || '';
  document.getElementById('event-description').value = event.description || '';
  document.getElementById('event-color').value = event.color || '#2563eb';
  document.getElementById('delete-event-btn').style.display = event.created_by === JSON.parse(localStorage.getItem('user') || '{}').id ? 'block' : 'none';
}

function closeEventModal() {
  document.getElementById('event-modal').classList.remove('show');
}

async function saveEvent(e) {
  e.preventDefault();
  
  const eventData = {
    title: document.getElementById('event-title').value,
    category: document.getElementById('event-category').value,
    allDay: document.getElementById('event-all-day').checked,
    start: document.getElementById('event-start').value,
    end: document.getElementById('event-end').value,
    location: document.getElementById('event-location').value,
    description: document.getElementById('event-description').value,
    color: document.getElementById('event-color').value
  };
  
  const eventId = document.getElementById('event-id').value;
  
  try {
    if (eventId) {
      await api(`/calendar/events/${eventId}`, {
        method: 'PUT',
        body: JSON.stringify(eventData)
      });
    } else {
      await api('/calendar/events', {
        method: 'POST',
        body: JSON.stringify(eventData)
      });
    }
    
    closeEventModal();
    loadCalendar();
  } catch (error) {
    alert(error.message);
  }
}

async function deleteEvent() {
  const eventId = document.getElementById('event-id').value;
  if (!eventId) return;
  
  if (!confirm('Are you sure you want to delete this event?')) return;
  
  try {
    await api(`/calendar/events/${eventId}`, { method: 'DELETE' });
    closeEventModal();
    loadCalendar();
  } catch (error) {
    alert(error.message);
  }
}
