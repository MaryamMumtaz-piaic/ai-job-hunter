/* ── Toast Notification System ── */
(function () {
  function ensureContainer() {
    let c = document.getElementById('toast-container');
    if (!c) {
      c = document.createElement('div');
      c.id = 'toast-container';
      document.body.appendChild(c);
    }
    return c;
  }

  const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };

  window.showToast = function (message, type = 'info', duration = 4000) {
    const container = ensureContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || 'ℹ'}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('toast-out');
      setTimeout(() => toast.remove(), 220);
    }, duration);
  };
})();

/* ── API Helper ── */
window.api = {
  async get(url) {
    const r = await fetch(url, { credentials: 'include' });
    if (!r.ok) {
      let msg = 'Request failed';
      try { const d = await r.json(); msg = d.detail || d.message || msg; } catch {}
      throw new Error(msg);
    }
    return r.json();
  },

  async post(url, data) {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data),
    });
    if (!r.ok) {
      let msg = 'Request failed';
      try { const d = await r.json(); msg = d.detail || d.message || msg; } catch {}
      throw new Error(msg);
    }
    return r.json();
  },

  async put(url, data) {
    const r = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data),
    });
    if (!r.ok) {
      let msg = 'Request failed';
      try { const d = await r.json(); msg = d.detail || d.message || msg; } catch {}
      throw new Error(msg);
    }
    return r.json();
  },

  async postForm(url, formData) {
    const r = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      body: formData,
    });
    if (!r.ok) {
      let msg = 'Request failed';
      try { const d = await r.json(); msg = d.detail || d.message || msg; } catch {}
      throw new Error(msg);
    }
    return r.json();
  },

  async del(url) {
    const r = await fetch(url, { method: 'DELETE', credentials: 'include' });
    if (!r.ok) {
      let msg = 'Request failed';
      try { const d = await r.json(); msg = d.detail || d.message || msg; } catch {}
      throw new Error(msg);
    }
    return r.json();
  },
};

/* ── Tag Input Widget ── */
window.TagInput = class {
  constructor(containerEl, initialTags = [], { placeholder = 'Type and press Enter…', onChange } = {}) {
    this.container = typeof containerEl === 'string' ? document.querySelector(containerEl) : containerEl;
    this.tags = [...initialTags];
    this.placeholder = placeholder;
    this.onChange = onChange || null;
    this._render();
  }

  addTag(tag) {
    tag = tag.trim();
    if (!tag || this.tags.includes(tag)) return;
    this.tags.push(tag);
    this._render();
    if (this.onChange) this.onChange(this.tags);
  }

  removeTag(tag) {
    this.tags = this.tags.filter(t => t !== tag);
    this._render();
    if (this.onChange) this.onChange(this.tags);
  }

  setTags(tags) {
    this.tags = [...tags];
    this._render();
  }

  getTags() { return [...this.tags]; }

  _render() {
    this.container.innerHTML = '';
    this.container.className = 'tag-input-container';

    this.tags.forEach(tag => {
      const pill = document.createElement('span');
      pill.className = 'tag';
      pill.innerHTML = `${tag} <button class="tag-remove" data-tag="${tag}">×</button>`;
      pill.querySelector('.tag-remove').addEventListener('click', () => this.removeTag(tag));
      this.container.appendChild(pill);
    });

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'tag-input-field';
    input.placeholder = this.tags.length ? '' : this.placeholder;
    input.addEventListener('keydown', e => {
      if ((e.key === 'Enter' || e.key === ',') && input.value.trim()) {
        e.preventDefault();
        this.addTag(input.value.replace(',', ''));
        input.value = '';
      } else if (e.key === 'Backspace' && !input.value && this.tags.length) {
        this.removeTag(this.tags[this.tags.length - 1]);
      }
    });
    this.container.appendChild(input);
    this.container.addEventListener('click', () => input.focus());
  }
};

/* ── Modal System ── */
window.openModal = function (modalId) {
  const el = document.getElementById(modalId);
  if (el) {
    el.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }
};

window.closeModal = function (modalId) {
  const el = document.getElementById(modalId);
  if (el) {
    el.classList.add('hidden');
    document.body.style.overflow = '';
  }
};

// Close modal on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.add('hidden');
    document.body.style.overflow = '';
  }
});

// Close modal on Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay:not(.hidden)').forEach(m => {
      m.classList.add('hidden');
      document.body.style.overflow = '';
    });
  }
});

/* ── Format Date ── */
window.formatDate = function (dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
};

/* ── Format Salary ── */
window.formatSalary = function (min, max, currency = 'USD') {
  if (!min && !max) return 'Salary not disclosed';
  const symbol = currency === 'USD' ? '$' : currency === 'GBP' ? '£' : currency === 'EUR' ? '€' : '$';
  const fmt = n => n >= 1000 ? `${symbol}${Math.round(n / 1000)}K` : `${symbol}${n}`;
  if (min && max) return `${fmt(min)} – ${fmt(max)}`;
  if (min) return `From ${fmt(min)}`;
  return `Up to ${fmt(max)}`;
};

/* ── Get Initials ── */
window.getInitials = function (name) {
  if (!name) return '?';
  const words = name.trim().split(/\s+/);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[words.length - 1][0]).toUpperCase();
};

/* ── Avatar Color (deterministic) ── */
const AVATAR_COLORS = [
  '#4f46e5','#7c3aed','#2563eb','#059669','#d97706',
  '#dc2626','#0891b2','#be185d','#16a34a','#9333ea',
];
window.avatarColor = function (name) {
  let hash = 0;
  for (let i = 0; i < (name || '').length; i++) hash = (hash * 31 + name.charCodeAt(i)) & 0xffffffff;
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
};

/* ── Status Badge HTML ── */
window.statusBadge = function (status) {
  const s = (status || '').toLowerCase().replace(/ /g, '-');
  const labels = {
    draft: 'Draft', pending: 'Pending Approval', approved: 'Approved',
    submitted: 'Submitted', interview: 'Interview', rejected: 'Rejected', offer: 'Offer'
  };
  const label = labels[s] || status;
  return `<span class="status-badge badge-${s}">${label}</span>`;
};

/* ── Match Badge HTML ── */
window.matchBadge = function (score) {
  const pct = Math.round(score);
  const cls = pct >= 80 ? 'match-high' : pct >= 60 ? 'match-mid' : 'match-low';
  return `<span class="match-badge ${cls}">${pct}% match</span>`;
};

/* ── Loading Button Helper ── */
window.setButtonLoading = function (btn, loading, originalText) {
  if (loading) {
    btn.disabled = true;
    btn.dataset.origText = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> ${originalText || 'Loading…'}`;
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.dataset.origText || originalText || 'Submit';
  }
};

/* ── Debounce ── */
window.debounce = function (fn, delay = 300) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
};

/* ── Dropdown Avatar Menu ── */
document.addEventListener('DOMContentLoaded', () => {
  const avatarBtn = document.getElementById('avatar-menu-btn');
  const avatarDropdown = document.getElementById('avatar-dropdown');
  if (avatarBtn && avatarDropdown) {
    avatarBtn.addEventListener('click', e => {
      e.stopPropagation();
      avatarDropdown.classList.toggle('hidden');
    });
    document.addEventListener('click', () => avatarDropdown.classList.add('hidden'));
  }
});
