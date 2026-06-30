/* dashboard.js — SOC Staff Dashboard logic */

if (window.requireAuth) {
  window.requireAuth();
} else if (!sessionStorage.getItem('hau_user')) {
  window.location.replace(window.getLoginUrl ? window.getLoginUrl() : '/login');
}

const API_BASE = window.location.origin;

let sampleInquiries = [];

const views = document.querySelectorAll('.view');

const settingsStorageKey = 'hau_dashboard_settings';
const defaultSettings = {
  officeHours: 'Monday to Friday, 8:00 AM - 5:00 PM',
  officeEmail: 'guidance@hau.edu.ph',
  contactNumber: '(045) 123-4567',
  officeLocation: 'SOC Guidance Office, Holy Angel University',
  autoFlag: true,
  showSupport: false,
  escalationMessage: 'Your concern may need further attention from Guidance Office personnel. Please wait for proper assistance or contact the office directly if urgent.',
  categories: [
    'Guidance Appointment',
    'Counseling Services',
    'Office Schedule',
    'Requirements and Procedures',
    'Emotional Support Concerns',
    'General Inquiry',
    'Unknown Inquiry',
  ],
  faqs: [
    {
      title: 'Office Hours',
      question: 'What are your office hours?',
      answer: 'The SOC Guidance Office is open from Monday to Friday, 8:00 AM to 5:00 PM.',
    },
    {
      title: 'Book Appointment',
      question: 'How can I book an appointment?',
      answer: 'You may book an appointment by selecting the Book Appointment option and submitting your preferred date and reason for appointment.',
    },
    {
      title: 'Counseling Services',
      question: 'Can I speak with a counselor?',
      answer: 'Yes, you may request counseling assistance through the chatbot or visit the SOC Guidance Office during office hours.',
    },
  ],
};

function loadSettings() {
  try {
    const raw = localStorage.getItem(settingsStorageKey);
    if (!raw) return { ...defaultSettings };
    return { ...defaultSettings, ...JSON.parse(raw) };
  } catch (error) {
    console.error(error);
    return { ...defaultSettings };
  }
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Request failed');
  }
  return data;
}

function mapInquiry(row) {
  const createdAt = row.created_at ? new Date(row.created_at) : new Date();
  return {
    student: row.user_name || row.student_name || 'Unknown',
    studentId: row.student_id || row.id ? `#${row.id}` : '—',
    email: row.user_email || row.student_email || '',
    message: row.message || '',
    category: row.category || 'General Inquiry',
    status: row.escalate ? 'negative' : (row.status || (row.emotion || 'neutral')),
    time: createdAt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
    staffNotes: row.staff_notes || '',
  };
}

function mapAppointment(row) {
  return {
    id: row.id,
    date: row.preferred_date,
    time: row.preferred_time,
    student: row.student_name,
    status: row.status || 'pending',
    notes: row.reason,
  };
}

function formatAppointmentDate(dateValue) {
  if (!dateValue) return 'No date';
  const parsed = new Date(`${dateValue}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return dateValue;
  return parsed.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatAppointmentTime(timeValue) {
  if (!timeValue) return 'No time';
  const [hourStr, minuteStr] = timeValue.split(':');
  const hour = Number(hourStr);
  const minute = Number(minuteStr);
  const date = new Date();
  date.setHours(hour, minute, 0, 0);
  return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

function renderAppointmentsView() {
  const tbody = document.getElementById('appointments-tbody');
  const totalEl = document.getElementById('appointment-total');
  const availableEl = document.getElementById('appointment-available');
  const reservedEl = document.getElementById('appointment-reserved');
  if (!tbody) return;

  const appointments = window.backendAppointments || [];
  const availableCount = appointments.filter(slot => slot.status === 'available').length;
  const reservedCount = appointments.filter(slot => slot.status === 'reserved').length;

  if (totalEl) totalEl.textContent = appointments.length;
  if (availableEl) availableEl.textContent = availableCount;
  if (reservedEl) reservedEl.textContent = reservedCount;

  tbody.innerHTML = '';
  if (!appointments.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--gray-400);padding:30px">No appointment slots yet.</td></tr>';
    return;
  }

  appointments.forEach(slot => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${formatAppointmentDate(slot.date)}</td>
      <td>${formatAppointmentTime(slot.time)}</td>
      <td>${slot.student ? slot.student : '—'}</td>
      <td><span class="badge ${slot.status === 'reserved' ? 'negative' : 'neutral'}">${slot.status === 'reserved' ? 'Reserved' : 'Available'}</span></td>
      <td>${slot.notes || 'No note'}</td>
      <td>
        ${slot.status === 'reserved'
          ? '<button class="action-link" data-action="available" data-id="' + slot.id + '">Set Available</button>'
          : '<button class="action-link" data-action="reserve" data-id="' + slot.id + '">Reserve</button>'}
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll('[data-action="reserve"]').forEach(button => {
    button.addEventListener('click', () => reserveAppointment(button.dataset.id));
  });

  tbody.querySelectorAll('[data-action="available"]').forEach(button => {
    button.addEventListener('click', () => setAppointmentAvailable(button.dataset.id));
  });
}

async function addAppointmentSlotFromForm() {
  const date = document.getElementById('appointment-date')?.value;
  const time = document.getElementById('appointment-time')?.value;
  const notes = document.getElementById('appointment-notes')?.value.trim() || '';
  const available = document.getElementById('appointment-available-check')?.checked;

  if (!date || !time) {
    createToast('Please enter a date and time for the slot.', 'info');
    return;
  }

  try {
    await fetchJson(`${API_BASE}/api/appointments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_name: available ? 'Open Slot' : 'Reserved Slot',
        student_email: '',
        preferred_date: date,
        preferred_time: time,
        reason: notes || 'Added from dashboard',
        status: available ? 'available' : 'reserved'
      })
    });
    document.getElementById('appointment-date').value = '';
    document.getElementById('appointment-time').value = '';
    document.getElementById('appointment-notes').value = '';
    document.getElementById('appointment-available-check').checked = true;
    await loadBackendData();
    createToast('Appointment slot added.', 'success');
  } catch (error) {
    createToast('Unable to save appointment slot.', 'info');
  }
}

async function reserveAppointment(id) {
  const studentName = await showPrompt('Reserve Slot', 'Student name');
  if (!studentName) return;

  const appointments = window.backendAppointments || [];
  const target = appointments.find(slot => String(slot.id) === String(id));
  if (!target) return;

  target.status = 'reserved';
  target.student = studentName;
  try {
    await fetchJson(`${API_BASE}/api/appointments/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'reserved', student_name: studentName })
    });
    window.backendAppointments = appointments;
    renderAppointmentsView();
    createToast('Slot reserved.', 'success');
  } catch (error) {
    createToast('Unable to reserve slot.', 'info');
  }
}

function setAppointmentAvailable(id) {
  const appointments = window.backendAppointments || [];
  const target = appointments.find(slot => String(slot.id) === String(id));
  if (!target) return;

  target.status = 'available';
  target.student = '';
  fetchJson(`${API_BASE}/api/appointments/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: 'available', student_name: '' })
  })
    .then(() => {
      window.backendAppointments = appointments;
      renderAppointmentsView();
      createToast('Slot marked available.', 'info');
    })
    .catch(() => createToast('Unable to update slot.', 'info'));
}

function createCategoryChip(category) {
  const chip = document.createElement('button');
  chip.type = 'button';
  chip.className = 'chip';
  chip.dataset.category = category;
  chip.innerHTML = `${category}<span class="chip-remove" aria-hidden="true">×</span>`;
  return chip;
}

function createFaqBlock(title, question, answer) {
  const container = document.createElement('div');
  container.className = 'faq-block';
  container.innerHTML = `
    <div class="faq-block-header">
      <div class="faq-title">${title}</div>
      <div class="faq-q">${question}</div>
    </div>
    <div class="faq-block-body">
      <textarea>${answer || ''}</textarea>
    </div>
  `;
  return container;
}

function getFaqPanel() {
  const panel = Array.from(document.querySelectorAll('#view-settings .settings-panel')).find(panelEl => {
    const heading = panelEl.querySelector('h3');
    return heading && heading.textContent.includes('FAQ Responses');
  });
  return panel || document.querySelector('#view-settings');
}

function getFaqListContainer(panel = getFaqPanel()) {
  if (!panel) return null;
  return panel.querySelector('.faq-list') || panel;
}

function appendFaqBlock(block, panel = getFaqPanel()) {
  const list = getFaqListContainer(panel);
  if (!block || !list) return false;
  list.appendChild(block);
  return true;
}

function getSettingsSnapshot() {
  const root = document.getElementById('view-settings');
  if (!root) return { ...defaultSettings };

  const inputs = root.querySelectorAll('.field-grid-2 .field-group input');
  const toggles = root.querySelectorAll('.toggle-row input[type=checkbox]');
  const escalationPanel = Array.from(root.querySelectorAll('.settings-panel')).find(panel => {
    const heading = panel.querySelector('h3');
    return heading && heading.textContent.includes('Escalation');
  });

  return {
    officeHours: inputs[0]?.value || '',
    officeEmail: inputs[1]?.value || '',
    contactNumber: inputs[2]?.value || '',
    officeLocation: inputs[3]?.value || '',
    autoFlag: toggles[0]?.checked || false,
    showSupport: toggles[1]?.checked || false,
    escalationMessage: escalationPanel?.querySelector('textarea')?.value || defaultSettings.escalationMessage,
    categories: Array.from(root.querySelectorAll('.category-chips .chip')).map(chip => chip.dataset.category || chip.textContent.replace('×', '').trim()).filter(Boolean),
    faqs: Array.from(root.querySelectorAll('.faq-block')).map(block => ({
      title: block.querySelector('.faq-title')?.textContent?.trim() || '',
      question: block.querySelector('.faq-q')?.textContent?.trim() || '',
      answer: block.querySelector('.faq-block-body textarea')?.value || '',
    })),
  };
}

function saveSettingsToStorage(settings = getSettingsSnapshot(), toast = true) {
  try {
    localStorage.setItem(settingsStorageKey, JSON.stringify(settings));
    fetch(`${API_BASE}/api/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    }).catch(error => console.error(error));
    if (toast) createToast('Settings saved', 'success');
    return true;
  } catch (error) {
    console.error(error);
    if (toast) createToast('Unable to save settings locally', 'info');
    return false;
  }
}

function renderSettingsFromStorage() {
  const root = document.getElementById('view-settings');
  if (!root) return;

  const settings = loadSettings();
  const inputs = root.querySelectorAll('.field-grid-2 .field-group input');
  const toggles = root.querySelectorAll('.toggle-row input[type=checkbox]');
  const escalationPanel = Array.from(root.querySelectorAll('.settings-panel')).find(panel => {
    const heading = panel.querySelector('h3');
    return heading && heading.textContent.includes('Escalation');
  });

  if (inputs[0]) inputs[0].value = settings.officeHours;
  if (inputs[1]) inputs[1].value = settings.officeEmail;
  if (inputs[2]) inputs[2].value = settings.contactNumber;
  if (inputs[3]) inputs[3].value = settings.officeLocation;

  if (toggles[0]) toggles[0].checked = Boolean(settings.autoFlag);
  if (toggles[1]) toggles[1].checked = Boolean(settings.showSupport);

  if (escalationPanel) {
    const textarea = escalationPanel.querySelector('textarea');
    if (textarea) textarea.value = settings.escalationMessage;
  }

  const categories = root.querySelector('.category-chips');
  if (categories) {
    categories.innerHTML = '';
    settings.categories.forEach(category => categories.appendChild(createCategoryChip(category)));
  }

  const faqPanel = getFaqPanel();
  if (faqPanel) {
    const faqList = getFaqListContainer(faqPanel);
    if (faqList) {
      faqList.querySelectorAll('.faq-block').forEach(block => block.remove());
    }
    settings.faqs.forEach(faq => {
      appendFaqBlock(createFaqBlock(faq.title, faq.question, faq.answer), faqPanel);
    });
  }
}

function bindSettingsInteractions() {
  const root = document.getElementById('view-settings');
  if (!root) return;

  root.addEventListener('click', event => {
    const remove = event.target.closest('.chip-remove');
    if (remove) {
      const chip = remove.closest('.chip');
      chip?.remove();
      saveSettingsToStorage(undefined, false);
    }
  });

  root.addEventListener('input', event => {
    if (event.target.matches('input, textarea, select')) {
      saveSettingsToStorage(undefined, false);
    }
  });
}

// lightweight toast for feedback
function createToast(message, type = 'info', timeout = 3400) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const t = document.createElement('div');
  t.className = 'toast ' + (type || '');
  t.textContent = message;
  container.appendChild(t);
  // auto remove
  setTimeout(() => {
    t.style.animation = 'toast-out 300ms forwards';
    setTimeout(() => t.remove(), 350);
  }, timeout);
  return t;
}

// small prompt modal (returns Promise<string|null>)
function showPrompt(title, placeholder = '', multiline = false) {
  return new Promise(resolve => {
    const overlay = document.createElement('div');
    overlay.className = 'prompt-overlay';
    const prompt = document.createElement('div');
    prompt.className = 'prompt';
    const h = document.createElement('h4');
    h.textContent = title;
    prompt.appendChild(h);
    const input = document.createElement(multiline ? 'textarea' : 'input');
    input.placeholder = placeholder || '';
    prompt.appendChild(input);
    const actions = document.createElement('div');
    actions.className = 'prompt-actions';
    const cancel = document.createElement('button');
    cancel.className = 'btn btn-outline btn-sm';
    cancel.textContent = 'Cancel';
    const ok = document.createElement('button');
    ok.className = 'btn btn-primary btn-sm';
    ok.textContent = 'OK';
    actions.appendChild(cancel);
    actions.appendChild(ok);
    prompt.appendChild(actions);
    overlay.appendChild(prompt);
    document.body.appendChild(overlay);
    input.focus();

    ok.onclick = () => { resolve(input.value.trim() || null); overlay.remove(); };
    cancel.onclick = () => { resolve(null); overlay.remove(); };
    overlay.addEventListener('click', (e) => { if (e.target === overlay) { resolve(null); overlay.remove(); } });
  });
}

const navItems = document.querySelectorAll('.nav-item[data-view]');
const headerTitle = document.getElementById('header-title');
const headerSub = document.getElementById('header-sub');
const headerActions = document.getElementById('header-actions');
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const filterTabs = document.querySelectorAll('.filter-tab');
const currentLocation = window.location.pathname || '';

const viewMeta = {
  inbox: { title: 'Inquiry Dashboard', sub: 'Screen, organize, and prioritize student concerns', actions: '<button class="btn btn-primary" id="new-entry-btn">New Manual Entry</button>' },
  flagged: { title: 'Flagged Cases', sub: 'Students with detected negative emotion requiring review', actions: '' },
  appointments: { title: 'Appointments', sub: 'Review reserved and open counseling slots for the day', actions: '' },
  resolved: { title: 'Resolved Inquiries', sub: 'Cases that have been closed or marked resolved', actions: '' },
  reports: { title: 'Reports', sub: 'Monitor chatbot inquiries, flagged concerns, and response trends.', actions: '<div class="report-period-badge">This Month</div>' },
  settings: { title: 'Settings & FAQ Management', sub: 'Update chatbot responses, office details, categories, and escalation messages.', actions: '<button class="btn btn-primary" onclick="saveSettings()">Save Changes</button>' },
  'manual-entry': { title: 'New Manual Entry', sub: 'Create an inquiry record for concerns received outside the chatbot.', actions: '<button class="btn btn-outline" onclick="goBack()">Back to Dashboard</button>' },
  'case-details': { title: 'Case Details', sub: 'Review student concern, chatbot classification, and counselor action.', actions: '<button class="btn btn-outline" onclick="goBack()">Back to Dashboard</button>' },
};

let currentView = 'inbox';
let prevView = 'inbox';
let currentInboxFilter = 'all';

function initials(name) {
  return name.split(' ').map(part => part[0]).join('').slice(0, 2).toUpperCase();
}

function badgeHTML(status) {
  const map = {
    negative: ['negative', 'Negative'],
    neutral: ['neutral', 'Routine'],
    resolved: ['resolved', 'Resolved'],
    pending: ['pending', 'Pending'],
  };
  const [cls, label] = map[status] || ['pending', 'Pending'];
  return `<span class="badge ${cls}">${label}</span>`;
}

function updateHeader(viewId) {
  const meta = viewMeta[viewId] || {};
  headerTitle.textContent = meta.title || '';
  headerSub.textContent = meta.sub || '';
  headerActions.innerHTML = meta.actions || '';

  const newEntryBtn = document.getElementById('new-entry-btn');
  if (newEntryBtn) {
    newEntryBtn.addEventListener('click', () => switchView('manual-entry'));
  }
}

function switchView(viewId) {
  prevView = currentView;
  currentView = viewId;

  views.forEach(view => view.classList.remove('active'));
  const activeView = document.getElementById(`view-${viewId}`);
  if (activeView) activeView.classList.add('active');

  navItems.forEach(item => {
    item.classList.toggle('active', item.dataset.view === viewId);
  });

  updateHeader(viewId);
  window.scrollTo(0, 0);
}

function goBack() {
  switchView(prevView === currentView ? 'inbox' : prevView);
}

async function saveSettings() {
  return saveSettingsToStorage(getSettingsSnapshot());
}

navItems.forEach(item => {
  item.addEventListener('click', () => switchView(item.dataset.view));
});

sidebarToggle.addEventListener('click', () => {
  sidebar.classList.toggle('open');
  sidebarOverlay.classList.toggle('open');
});

sidebarOverlay.addEventListener('click', () => {
  sidebar.classList.remove('open');
  sidebarOverlay.classList.remove('open');
});

function makeRow(inquiry, includeActions = true) {
  const tr = document.createElement('tr');
  const actionsCell = includeActions
    ? `<td>
        <div class="action-cell">
          <button class="action-link view-btn">View</button>
          ${inquiry.status !== 'resolved' ? '<button class="action-link resolve-btn">Resolve</button>' : ''}
          ${inquiry.status === 'negative' ? '<button class="action-link takeover takeover-btn">Takeover</button>' : ''}
        </div>
      </td>`
    : '<td></td>';

  tr.innerHTML = `
    <td>
      <div class="student-cell">
        <div class="student-avatar">${initials(inquiry.student)}</div>
        <div>
          <div class="student-name">${inquiry.student}</div>
          <div class="student-id">${inquiry.studentId}</div>
        </div>
      </div>
    </td>
    <td><div class="msg-preview">${inquiry.message}</div></td>
    <td>${inquiry.category}</td>
    <td>${badgeHTML(inquiry.status)}</td>
    <td class="time-cell">${inquiry.time}</td>
    ${actionsCell}
  `;

  tr.querySelector('.view-btn')?.addEventListener('click', () => openCaseDetails(inquiry));
  tr.querySelector('.resolve-btn')?.addEventListener('click', () => {
    inquiry.status = 'resolved';
    renderAllTables();
    updateFlaggedCount();
  });
  tr.querySelector('.takeover-btn')?.addEventListener('click', () => takeOverInquiry(inquiry));

  return tr;
}

function renderTable(tbodyId, filter) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  tbody.innerHTML = '';

  const list = filter === 'all'
    ? sampleInquiries
    : sampleInquiries.filter(inquiry => inquiry.status === filter);

  if (!list.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--gray-400);padding:30px">No inquiries found.</td></tr>';
    return;
  }

  list.forEach(inquiry => tbody.appendChild(makeRow(inquiry)));
}

function renderAllTables() {
  renderTable('inquiry-tbody', currentInboxFilter);
  renderTable('flagged-tbody', 'negative');
  renderTable('resolved-tbody', 'resolved');
}

function updateFlaggedCount() {
  const count = sampleInquiries.filter(inquiry => inquiry.status === 'negative').length;
  const flaggedCount = document.getElementById('flagged-count');
  const statFlagged = document.getElementById('stat-flagged');
  const statFlagged2 = document.getElementById('stat-flagged-2');
  if (flaggedCount) flaggedCount.textContent = count;
  if (statFlagged) statFlagged.textContent = count;
  if (statFlagged2) statFlagged2.textContent = count;
}

filterTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    filterTabs.forEach(item => item.classList.remove('active'));
    tab.classList.add('active');
    currentInboxFilter = tab.dataset.filter;
    renderTable('inquiry-tbody', currentInboxFilter);
  });
});

function openCaseDetails(inquiry) {
  document.getElementById('case-avatar').textContent = initials(inquiry.student);
  document.getElementById('case-name').textContent = inquiry.student;
  document.getElementById('case-meta').textContent = `Student ID: ${inquiry.studentId} · Email: ${inquiry.email || `${inquiry.student.toLowerCase().replace(/\s+/g, '.')}@hau.edu.ph`}`;
  document.getElementById('case-message').textContent = inquiry.message;
  document.getElementById('case-category').textContent = inquiry.category;
  document.getElementById('case-time').textContent = inquiry.time;
  document.getElementById('case-emotion').textContent = inquiry.status === 'negative' ? 'Negative Emotion' : 'Neutral';
  document.getElementById('case-status-label').textContent = inquiry.status === 'negative' ? 'Pending Review' : (inquiry.status === 'resolved' ? 'Resolved' : 'Routine');

  const badge = document.getElementById('case-badge');
  badge.className = `badge ${inquiry.status === 'negative' ? 'negative' : (inquiry.status === 'resolved' ? 'resolved' : 'neutral')}`;
  badge.textContent = inquiry.status === 'negative' ? 'Negative' : (inquiry.status === 'resolved' ? 'Resolved' : 'Routine');

  const log = document.getElementById('case-chat-log');
  log.innerHTML = `
    <div class="chat-bubble student">
      <div class="bubble-from">Student <span class="bubble-time">${inquiry.time}</span></div>
      ${inquiry.message}
    </div>
    <div class="chat-bubble bot">
      <div class="bubble-from">Chatbot <span class="bubble-time">${inquiry.time}</span></div>
      I understand that this concern may be important or sensitive. Your message may need further attention from Guidance Office personnel.
    </div>
  `;

  const takeoverBtn = document.getElementById('case-takeover-btn');
  const resolveBtn = document.getElementById('case-resolve-btn');
  const pendingBtn = document.getElementById('case-pending-btn');

  takeoverBtn.onclick = () => takeOverInquiry(inquiry);

  resolveBtn.onclick = () => {
    inquiry.status = 'resolved';
    document.getElementById('case-status-label').textContent = 'Resolved';
    document.getElementById('case-badge').className = 'badge resolved';
    document.getElementById('case-badge').textContent = 'Resolved';
    renderAllTables();
    updateFlaggedCount();
    fetchJson(`${API_BASE}/api/inquiries/${inquiry.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'resolved' })
    }).catch(error => console.error(error));
    createToast('Case marked as resolved.', 'success');
  };

  pendingBtn.onclick = () => {
    inquiry.status = 'negative';
    document.getElementById('case-status-label').textContent = 'Pending Review';
    document.getElementById('case-badge').className = 'badge negative';
    document.getElementById('case-badge').textContent = 'Negative';
    renderAllTables();
    updateFlaggedCount();
    fetchJson(`${API_BASE}/api/inquiries/${inquiry.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'negative' })
    }).catch(error => console.error(error));
    createToast('Case marked as pending.', 'info');
  };

  document.getElementById('save-notes-btn').onclick = () => {
    const notes = document.getElementById('case-notes-input').value.trim();
    if (notes) {
      inquiry.staffNotes = notes;
      // append staff note into chat log
      const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const noteEl = document.createElement('div');
      noteEl.className = 'chat-bubble staff';
      noteEl.innerHTML = `<div class="bubble-from">Staff <span class="bubble-time">${timestamp}</span></div>${notes}`;
      log.appendChild(noteEl);
      document.getElementById('case-notes-input').value = '';
      fetchJson(`${API_BASE}/api/inquiries/${inquiry.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: inquiry.status || 'pending', staff_notes: notes })
      }).catch(error => console.error(error));
      createToast('Notes saved.', 'success');
    }
  };

  switchView('case-details');
}

function takeOverInquiry(inquiry) {
  inquiry.status = 'neutral';
  renderAllTables();
  updateFlaggedCount();
  createToast('Case taken over. Opening admin chat takeover page.', 'success');
  fetchJson(`${API_BASE}/api/inquiries/${inquiry.id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: 'neutral' })
  }).catch(error => console.error(error));
  const takeoverCase = {
    student: inquiry.student,
    studentId: inquiry.studentId,
    email: inquiry.email || `${inquiry.student.toLowerCase().replace(/\s+/g, '.')}@hau.edu.ph`,
    message: inquiry.message,
    category: inquiry.category,
    status: inquiry.status,
    time: inquiry.time,
    conversation: [
      { from: 'user', text: inquiry.message, time: inquiry.time },
      { from: 'bot', text: 'Your concern has been marked for staff takeover and is being handled by Guidance Office personnel.', time: inquiry.time }
    ]
  };
  localStorage.setItem('hau_takeover_case', JSON.stringify(takeoverCase));
  window.location.href = '/chatbot_admin';
}

async function loadBackendData() {
  try {
    const inquiries = await fetchJson(`${API_BASE}/api/inquiries`);
    sampleInquiries = (inquiries.items || []).map(mapInquiry);
  } catch (error) {
    console.error(error);
    sampleInquiries = [];
  }

  try {
    const appointments = await fetchJson(`${API_BASE}/api/appointments`);
    window.backendAppointments = (appointments.items || []).map(mapAppointment);
  } catch (error) {
    console.error(error);
    window.backendAppointments = [];
  }

  try {
    const settings = await fetchJson(`${API_BASE}/api/settings`);
    localStorage.setItem(settingsStorageKey, JSON.stringify(settings));
  } catch (error) {
    console.error(error);
  }

  renderAllTables();
  updateFlaggedCount();
  renderSettingsFromStorage();
  renderAppointmentsView();
}

function openCaseFromReport(name, id, message, category, status, time) {
  openCaseDetails({ student: name, studentId: id, message, category, status, time });
}

document.getElementById('save-entry-btn')?.addEventListener('click', () => {
  const name = document.getElementById('entry-name').value.trim();
  const studentId = document.getElementById('entry-id').value.trim();
  const email = document.getElementById('entry-email').value.trim();
  const message = document.getElementById('entry-message').value.trim();
  const category = document.getElementById('entry-category').value;
  const statusValue = document.getElementById('entry-status').value.toLowerCase();
  const now = new Date();
  const time = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });

  if (!name || !studentId || !message) {
    createToast('Please fill in Student Name, Student ID, and Message.', 'info');
    return;
  }

  const status = statusValue === 'resolved' ? 'resolved' : 'neutral';
  fetchJson(`${API_BASE}/api/inquiries`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      student_id: studentId,
      student_name: name,
      student_email: email,
      message,
      category,
      status,
      source: 'manual'
    })
  })
    .then(() => loadBackendData())
    .then(() => {
      ['entry-name', 'entry-id', 'entry-email', 'entry-message', 'entry-notes'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });
      createToast('Entry saved successfully!', 'success');
      switchView('inbox');
    })
    .catch(() => createToast('Unable to save entry right now.', 'info'));
});

document.getElementById('clear-entry-btn')?.addEventListener('click', () => {
  ['entry-name', 'entry-id', 'entry-email', 'entry-message', 'entry-notes'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
});

function logout() {
  sessionStorage.removeItem('hau_user');
  createToast('Logged out.', 'info');
  if (window.getLoginUrl) {
    setTimeout(() => window.location.replace(window.getLoginUrl()), 700);
  }
}

bindSettingsInteractions();
loadBackendData();

// UI buttons
document.getElementById('new-entry-btn')?.addEventListener('click', () => switchView('manual-entry'));

async function addCategoryFromButton() {
  const name = await showPrompt('Add Category', 'Category name');
  if (!name) return;
  const chips = document.querySelector('.category-chips');
  if (!chips) return;
  const chip = createCategoryChip(name);
  chips.appendChild(chip);
  chip.animate([{ transform: 'scale(0.96)', opacity: 0 }, { transform: 'scale(1)', opacity: 1 }], { duration: 260 });
  createToast('Category added', 'success');
  saveSettingsToStorage(undefined, false);
}

async function addFaqFromButton() {
  const title = await showPrompt('FAQ Title', 'Short title (e.g. Office Hours)');
  if (!title) return;
  const question = await showPrompt('FAQ Question', 'Example: What are your office hours?');
  if (!question) return;
  const answer = await showPrompt('FAQ Answer', 'Answer text', true);
  const container = createFaqBlock(title, question, answer);
  const faqPanel = getFaqPanel();
  if (appendFaqBlock(container, faqPanel)) {
    createToast('FAQ added', 'success');
    saveSettingsToStorage(undefined, false);
  } else {
    createToast('Unable to add FAQ right now', 'info');
  }
}

// Add category button
document.getElementById('add-category-btn')?.addEventListener('click', addCategoryFromButton);

// Add FAQ button
document.getElementById('add-faq-btn')?.addEventListener('click', addFaqFromButton);

// Save settings button in the UI
document.getElementById('save-settings-btn')?.addEventListener('click', () => saveSettings());
document.getElementById('add-appointment-btn')?.addEventListener('click', addAppointmentSlotFromForm);

window.saveSettings = saveSettings;
window.goBack = goBack;
window.openCaseFromReport = openCaseFromReport;
window.openCaseDetails = openCaseDetails;
window.logout = window.logout || logout;
window.addCategoryFromButton = addCategoryFromButton;
window.addFaqFromButton = addFaqFromButton;
