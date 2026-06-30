/* ─────────────────────────────────────────
   chat.js — SOC Guidance Office Chatbot
   Frontend logic: messaging, rule-based
   responses, emotion badges, escalation.

   NOTE: Replace the local response simulation with a POST
   call to your Flask `/chat` route. That route should load and
   run your local model, returning JSON with response text,
   emotion classification, and escalation status.
───────────────────────────────────────── */

// ── DOM References ──
// Redirect to login if no session (simple client-side guard)
if (!sessionStorage.getItem('hau_user')) {
  window.location.replace("/login");
}
const chatArea  = document.getElementById('chat-area');

const input     = document.getElementById('msg-input');
const qrBar     = document.getElementById('quick-replies');
const API_BASE  = window.location.origin;

// Escalation / takeover state
let currentEscalationId = sessionStorage.getItem('current_escalation') || null;
let isEscalated = !!currentEscalationId;

function serializeChat() {
  const rows = Array.from(chatArea.querySelectorAll('.msg-row'));
  return rows.map(r => {
    const isUser = r.classList.contains('user');
    const bubble = r.querySelector('.bubble');
    const timeEl = r.querySelector('.bubble-time');
    return { from: isUser ? 'user' : 'bot', text: bubble ? bubble.innerText : '', time: timeEl ? timeEl.textContent : '' };
  });
}

function pushEscalationEvent(evt) {
  try { localStorage.setItem('hau_escalation_event', JSON.stringify(evt)); }
  catch (e) { console.warn('Escalation event failed', e); }
}

function pushStaffMessage(obj) {
  try { localStorage.setItem('hau_escalation_staff_msg', JSON.stringify(obj)); }
  catch (e) { console.warn('Staff msg failed', e); }
}

function pushUserMessage(obj) {
  try { localStorage.setItem('hau_escalation_user_msg', JSON.stringify(obj)); }
  catch (e) { console.warn('User msg failed', e); }
}

// ── Set greeting timestamp ──
document.getElementById('greeting-time').textContent = getTime();

function getTime() {
  return new Date().toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit'
  });
}

// ── Auto-grow textarea ──
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 100) + 'px';
});

// ── Send on Enter (Shift+Enter = new line) ──
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// ─────────────────────────────
// UTILITIES
// ─────────────────────────────



function scrollToBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ─────────────────────────────
// APPEND MESSAGES
// ─────────────────────────────

function appendUserMessage(text) {
  const row = document.createElement('div');
  row.className = 'msg-row user';
  row.innerHTML = `
    <div class="bubble-wrap">
      <div class="bubble">${escapeHtml(text)}</div>
      <span class="bubble-time">${getTime()}</span>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

function appendBotMessage(htmlContent, emotionLabel) {
  const row = document.createElement('div');
  row.className = 'msg-row bot';

  let badge = '';
  if (emotionLabel === 'negative') {
    badge = `<span class="emotion-badge negative">Negative emotion detected</span>`;
  } else if (emotionLabel === 'neutral') {
    badge = `<span class="emotion-badge neutral">Routine inquiry</span>`;
  }

  row.innerHTML = `
    <div class="avatar">G</div>
    <div class="bubble-wrap">
      <div class="bubble">${htmlContent}${badge ? '<br>' + badge : ''}</div>
      <span class="bubble-time">${getTime()}</span>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

function appendEscalationNotice() {
  const wrap = document.createElement('div');
  wrap.className = 'escalation-wrap';
  wrap.innerHTML = `
    <div class="escalation-notice">
      <span class="icon"></span>
      <span>Your message has been flagged and referred to a Guidance Office counselor. A staff member will follow up with you shortly.</span>
    </div>`;
  chatArea.appendChild(wrap);
  scrollToBottom();
}

function showTypingIndicator() {
  const row = document.createElement('div');
  row.className = 'typing-row';
  row.id = 'typing-indicator';
  row.innerHTML = `
    <div class="avatar">G</div>
    <div class="typing-bubble">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

function removeTypingIndicator() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

// ─────────────────────────────
// RULE-BASED RESPONSE ENGINE
// (Placeholder — replace with
//  Flask API call in Week 2)
// ─────────────────────────────

const rules = [
  {
    pattern: /office hour|open|schedule|when|time/i,
    response: 'The SOC Guidance Office is open <strong>Monday to Friday, 8:00 AM – 5:00 PM</strong>. We are closed on weekends and public holidays.',
    emotion: 'neutral'
  },
  {
    pattern: /appoint|book|schedule a meet|consult|visit/i,
    response: 'To book an appointment, you may visit the SOC Guidance Office personally or send an email to <strong>soc.guidance@hau.edu.ph</strong>. Walk-in consultations are also welcome during office hours.',
    emotion: 'neutral'
  },
  {
    pattern: /counsel|therapy|mental health|stress|anxious|anxiety|depress|sad|overwhelm|hopeless/i,
    response: 'We\'re here for you. Our counselors provide a safe and confidential space to talk about what you\'re going through.',
    emotion: 'negative',
    escalate: true
  },
  {
    pattern: /bully|harass|abuse|threat|hurt|unsafe|scared|afraid|danger/i,
    response: 'Thank you for reaching out. Your safety and wellbeing matter to us. Please know you are not alone.',
    emotion: 'negative',
    escalate: true
  },
  {
    pattern: /document|clearance|certification|record|form/i,
    response: 'For document requests, please visit the SOC Guidance Office and fill out the appropriate request form. Processing typically takes <strong>3–5 working days</strong>.',
    emotion: 'neutral'
  },
  {
    pattern: /frustrat|disappoint|angry|upset|unfair|no one help|nobody|ignored/i,
    response: 'I\'m sorry to hear you\'re feeling this way. Let me connect you with one of our counselors who can give you the proper attention you deserve.',
    emotion: 'negative',
    escalate: true
  },
  {
    pattern: /contact|email|phone|reach|how to/i,
    response: 'You may reach the SOC Guidance Office at <strong>soc.guidance@hau.edu.ph</strong> or visit us at the School of Computing building during office hours.',
    emotion: 'neutral'
  },
  {
    pattern: /classmate|friend|concern|report|problem with/i,
    response: 'Thank you for bringing this to our attention. Please provide more details about your concern so we can assist you better.',
    emotion: 'neutral'
  },
];

function getResponse(text) {
  for (const rule of rules) {
    if (rule.pattern.test(text)) return rule;
  }
  return {
    response: 'Thank you for reaching out to the SOC Guidance Office. Your message has been received. For specific concerns, you may also visit us during office hours or email <strong>soc.guidance@hau.edu.ph</strong>.',
    emotion: 'neutral'
  };
}

// ─────────────────────────────
// SEND MESSAGE
// ─────────────────────────────

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  // Clear input
  input.value = '';
  input.style.height = 'auto';

  // Hide quick replies after first message
  qrBar.style.display = 'none';

  // Show user message
  appendUserMessage(text);

  // Show typing indicator
  showTypingIndicator();

  fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: text,
      user_name: JSON.parse(sessionStorage.getItem('hau_user') || '{}').name || '',
      user_email: JSON.parse(sessionStorage.getItem('hau_user') || '{}').email || '',
      conversation: serializeChat()
    })
  })
  .then(res => res.json())
  .then(data => {
    removeTypingIndicator();
    if (isEscalated && currentEscalationId) {
      const evt = { id: currentEscalationId, from: 'user', text, time: new Date().toISOString() };
      pushUserMessage(evt);
      appendBotMessage('Your message has been sent to the Guidance Office counselor.', 'neutral');
      return;
    }

    appendBotMessage(data.response || 'Sorry, I could not generate a response.', data.emotion || '');

    if (data.escalate) {
      const user = JSON.parse(sessionStorage.getItem('hau_user') || '{}');
      const escId = Date.now().toString();
      const esc = {
        id: escId,
        userEmail: user.email || 'unknown',
        userName: user.name || user.email || 'Unknown',
        time: new Date().toISOString(),
        status: 'open',
        conversation: serializeChat()
      };
      const listRaw = localStorage.getItem('hau_escalations');
      const list = listRaw ? JSON.parse(listRaw) : [];
      list.push(esc);
      localStorage.setItem('hau_escalations', JSON.stringify(list));
      pushEscalationEvent({ type: 'new', id: escId, userEmail: esc.userEmail, userName: esc.userName, time: esc.time });
      currentEscalationId = escId;
      sessionStorage.setItem('current_escalation', escId);
      isEscalated = true;
      setTimeout(appendEscalationNotice, 400);
      input.placeholder = 'A staff member will join shortly — your messages will be sent to staff.';
    }
  })
  .catch(() => {
    removeTypingIndicator();
    appendBotMessage('Sorry, I am having trouble connecting right now. Please try again.', '');
  });
}

function showAppointmentPrompt() {
  const existing = document.getElementById('appointment-confirmation');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.id = 'appointment-confirmation';
  overlay.className = 'confirmation-popup';
  overlay.innerHTML = `
    <div class="confirmation-card">
      <h3>Book an appointment?</h3>
      <p>You’ll be taken to the appointment request form where you can submit your details for guidance support.</p>
      <div class="confirmation-actions">
        <button type="button" class="cancel-btn">Cancel</button>
        <button type="button" class="confirm-btn">Open form</button>
      </div>
    </div>`;

  document.body.appendChild(overlay);

  overlay.querySelector('.cancel-btn').addEventListener('click', () => overlay.remove());
  overlay.querySelector('.confirm-btn').addEventListener('click', () => {
    overlay.remove();
    window.location.href = "/appointment";
  });
}

function sendQuick(text) {
  if (/book an appointment/i.test(text)) {
    showAppointmentPrompt();
    return;
  }
  input.value = text;
  sendMessage();
}

function appendStaffMessage(text) {
  const row = document.createElement('div');
  row.className = 'msg-row bot';
  row.innerHTML = `
    <div class="avatar">S</div>
    <div class="bubble-wrap">
      <div class="bubble">${escapeHtml(text)}</div>
      <span class="bubble-time">${getTime()}</span>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

// Listen for storage events so staff messages and escalation events propagate across tabs
window.addEventListener('storage', (e) => {
  try {
    if (!e.key || !e.newValue) return;
    if (e.key === 'hau_escalation_staff_msg') {
      const msg = JSON.parse(e.newValue);
      if (msg && msg.id && msg.id === currentEscalationId) {
        appendStaffMessage(msg.text);
      }
    }
    // If a new escalation is created elsewhere that targets this user, set local state
    if (e.key === 'hau_escalation_event') {
      const ev = JSON.parse(e.newValue);
      // no-op for now; dashboard handles listing
    }
  } catch (err) { console.warn('storage handler error', err); }
});
