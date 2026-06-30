/* =========================================================
   SOC Guidance Office – Appointment Form
   script.js
   ========================================================= */
'use strict';
// The server already protects this route; keep the page usable if sessionStorage
// is empty after a restart.
const user = window.requireAuth ? window.requireAuth() : null;
// ── DOM References ──────────────────────────────────────────────────────────
const form         = document.getElementById('appointmentForm');
const submitBtn    = document.getElementById('submitBtn');
const clearBtn     = document.getElementById('clearBtn');
const backBtn      = document.getElementById('backBtn');
const modal        = document.getElementById('successModal');
const modalClose   = document.getElementById('modalClose');
const refIdEl      = document.getElementById('refId');
// ── Field definitions (id + validation rules) ───────────────────────────────
const FIELDS = [
  {
    id:       'fullName',
    label:    'Full Name',
    required: true,
    validate: (v) => {
      if (!v.trim()) return 'Full Name is required.';
      if (v.trim().length < 3) return 'Please enter your full name (min. 3 characters).';
      if (!/^[a-zA-ZÀ-ÿ\s'\-\.]+$/.test(v.trim())) return 'Name should contain letters only.';
      return null;
    }
  },
  {
    id:       'studentId',
    label:    'Student ID',
    required: true,
    validate: (v) => {
      if (!v.trim()) return 'Student ID is required.';
      if (!/^\d{8}$/.test(v.trim())) return 'Enter exactly 8 digits (e.g. 20******).';
      return null;
    }
  },
  {
    id:       'email',
    label:    'Email Address',
    required: true,
    validate: (v) => {
      if (!v.trim()) return 'Email Address is required.';
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(v.trim())) return 'Please enter a valid email address.';
      return null;
    }
  },
  {
    id:       'contact',
    label:    'Contact Number',
    required: true,
    validate: (v) => {
      const cleaned = v.replace(/\s/g, '');
      if (!cleaned) return 'Contact Number is required.';
      if (!/^(09|\+639)\d{9}$/.test(cleaned)) return 'Enter a valid PH mobile number (e.g. 09XX XXX XXXX).';
      return null;
    }
  },
  {
    id:       'prefDate',
    label:    'Preferred Date',
    required: true,
    validate: (v) => {
      if (!v) return 'Preferred Date is required.';
      const selected = new Date(v);
      const today    = new Date();
      today.setHours(0, 0, 0, 0);
      if (selected < today) return 'Please select a future date.';
      const day = selected.getDay();
      if (day === 0 || day === 6) return 'Please select a weekday (Mon–Fri).';
      return null;
    }
  },
  {
    id:       'prefTime',
    label:    'Preferred Time',
    required: true,
    validate: (v) => {
      if (!v) return 'Preferred Time is required.';
      const [h, m] = v.split(':').map(Number);
      const totalMin = h * 60 + m;
      // Office hours: 8:00 AM – 5:00 PM
      if (totalMin < 8 * 60 || totalMin > 17 * 60) return 'Please select a time between 8:00 AM and 5:00 PM.';
      return null;
    }
  },
  {
    id:       'appointmentType',
    label:    'Appointment Type',
    required: true,
    validate: (v) => {
      if (!v) return 'Please select an appointment type.';
      return null;
    }
  },
  {
    id:       'reason',
    label:    'Reason for Appointment',
    required: true,
    validate: (v) => {
      if (!v.trim()) return 'Please provide a reason for your appointment.';
      if (v.trim().length < 20) return 'Please provide a bit more detail (min. 20 characters).';
      if (v.trim().length > 1000) return 'Reason must not exceed 1000 characters.';
      return null;
    }
  }
];
// ── Helpers ──────────────────────────────────────────────────────────────────
/**
 * Show or clear an error message for a given field.
 * @param {string} id     - Field element ID
 * @param {string|null} msg - Error text or null to clear
 */
function setError(id, msg) {
  const input    = document.getElementById(id);
  const errorEl  = document.getElementById(`${id}-error`);
  if (msg) {
    input.classList.add('input-error');
    if (errorEl) errorEl.textContent = msg;
  } else {
    input.classList.remove('input-error');
    if (errorEl) errorEl.textContent = '';
  }
}
/**
 * Validate a single field and update UI.
 * @param {{ id: string, validate: function }} field
 * @returns {boolean} true if valid
 */
function validateField(field) {
  const el  = document.getElementById(field.id);
  const val = el.value;
  const err = field.validate(val);
  setError(field.id, err);
  return err === null;
}
/**
 * Generate a random reference ID like GU-2026-XXXXX.
 * @returns {string}
 */
function generateRefId() {
  const year    = new Date().getFullYear();
  const random  = Math.floor(10000 + Math.random() * 90000);
  return `GU-${year}-${random}`;
}
/**
 * Set the minimum date input to today.
 */
function setMinDate() {
  const dateInput = document.getElementById('prefDate');
  const today     = new Date().toISOString().split('T')[0];
  dateInput.setAttribute('min', today);
}
// ── Live Validation (on blur) ────────────────────────────────────────────────
FIELDS.forEach((field) => {
  const el = document.getElementById(field.id);
  if (!el) return;
  // Validate on blur
  el.addEventListener('blur', () => validateField(field));
  // Clear error while typing/changing (after first blur)
  el.addEventListener('input', () => {
    if (el.classList.contains('input-error')) {
      validateField(field);
    }
  });
  // For select, also listen on change
  if (el.tagName === 'SELECT') {
    el.addEventListener('change', () => validateField(field));
  }
});
// ── Form Submission ──────────────────────────────────────────────────────────
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  let isValid = true;

  FIELDS.forEach(field => {
    if (!validateField(field)) isValid = false;
  });

  if (!isValid) {
    const firstError = form.querySelector('.input-error');

    if (firstError) {
      firstError.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });

      firstError.focus();
    }

    return;
  }

  submitBtn.classList.add('loading');
  submitBtn.disabled = true;

  const referenceId = generateRefId();

  const payload = {
    ...collectFormData(),
    referenceId,
    userEmail: user?.email || '',
    userName: user?.name || ''
  };

  try {

    const response = await fetch(`${window.location.origin}/api/appointments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        student_name: payload.fullName,
        student_email: payload.email,
        preferred_date: payload.preferredDate,
        preferred_time: payload.preferredTime,
        reason: payload.reason,
      })
    });

    if (!response.ok) {
      throw new Error();
    }

    refIdEl.textContent = referenceId;
    openModal();

  } catch (err) {

    alert('Unable to submit appointment request. Please try again.');

  } finally {

    submitBtn.classList.remove('loading');
    submitBtn.disabled = false;

  }
});
// ── Collect Form Data ────────────────────────────────────────────────────────
function collectFormData() {
  return {
    fullName: document.getElementById('fullName').value.trim(),
    studentId: document.getElementById('studentId').value.trim(),
    email: document.getElementById('email').value.trim(),
    contact: document.getElementById('contact').value.trim(),
    preferredDate: document.getElementById('prefDate').value,
    preferredTime: document.getElementById('prefTime').value,
    appointmentType: document.getElementById('appointmentType').value,
    reason: document.getElementById('reason').value.trim(),
    submittedAt: new Date().toISOString()
  };
}
// ── Clear Form ───────────────────────────────────────────────────────────────
clearBtn.addEventListener('click', () => {
  if (!confirm('Are you sure you want to clear all fields?')) return;
  resetForm();
});

backBtn?.addEventListener('click', () => {
  window.location.href = '/chatbot';
});

function resetForm() {
  form.reset();
  // Remove all error states
  FIELDS.forEach((field) => setError(field.id, null));
  // Scroll to top of form
  form.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
// ── Modal Controls ───────────────────────────────────────────────────────────
function openModal() {
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  modalClose.focus();
}
function closeModal() {
  modal.classList.remove('active');
  document.body.style.overflow = '';
  resetForm();
  submitBtn.focus();
}
modalClose.addEventListener('click', closeModal);
// Close on overlay click
modal.addEventListener('click', (e) => {
  if (e.target === modal) closeModal();
});
// Close on Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modal.classList.contains('active')) {
    closeModal();
  }
});
// ── Character Counter for Reason ─────────────────────────────────────────────
(function setupCharCounter() {
  const reasonEl   = document.getElementById('reason');
  const errorEl    = document.getElementById('reason-error');
  const MAX_CHARS  = 1000;
  // Create counter element
  const counter        = document.createElement('span');
  counter.className    = 'char-counter';
  counter.style.cssText = `
    display: block;
    font-size: 0.72rem;
    color: var(--text-muted);
    text-align: right;
    margin-top: 4px;
  `;
  // Insert after the textarea's parent form-group
  reasonEl.parentNode.appendChild(counter);
  updateCounter();
  reasonEl.addEventListener('input', updateCounter);
  function updateCounter() {
    const len = reasonEl.value.length;
    counter.textContent = `${len} / ${MAX_CHARS}`;
    counter.style.color = len > MAX_CHARS ? '#cc2222' : 'var(--text-muted)';
  }
})();
// ── Contact Number Auto-Formatting ───────────────────────────────────────────
(function setupContactFormat() {
  const contactEl = document.getElementById('contact');
  contactEl.addEventListener('input', () => {
    let val     = contactEl.value.replace(/\D/g, '');
    if (val.startsWith('63')) val = '0' + val.slice(2);
    if (val.length > 11) val = val.slice(0, 11);
    // Format: XXXX XXX XXXX
    const parts = [val.slice(0, 4), val.slice(4, 7), val.slice(7, 11)].filter(Boolean);
    contactEl.value = parts.join(' ');
  });
})();
// ── Init ─────────────────────────────────────────────────────────────────────
setMinDate();
