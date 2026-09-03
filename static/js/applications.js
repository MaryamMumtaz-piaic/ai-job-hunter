/* ── AI Job Hunter — Applications Tracker Page ── */

let allApplications = [];
let currentFilter = 'all';
let activeApplicationId = null;

const STATUS_ORDER = ['draft', 'pending', 'approved', 'submitted', 'interview', 'offer', 'rejected'];
const STATUS_LABELS = {
  draft: 'Draft', pending: 'Pending Approval', approved: 'Approved',
  submitted: 'Submitted', interview: 'Interview', rejected: 'Rejected', offer: 'Offer'
};

document.addEventListener('DOMContentLoaded', async () => {
  await loadApplications();
  initStatusTabs();
  initDetailModal();
});

/* ── Load Applications ── */
async function loadApplications() {
  const gridEl = document.getElementById('applications-grid');
  if (!gridEl) return;

  showGridSkeleton(gridEl);

  try {
    const data = await window.api.get('/api/applications');
    allApplications = Array.isArray(data) ? data : (data.applications || []);
    // Sort newest first
    allApplications.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
    updateSummaryStats();
    renderApplications(filterApps(currentFilter));
  } catch (err) {
    gridEl.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-state-icon">📋</div>
        <div class="empty-state-title">No applications yet</div>
        <div class="empty-state-desc">Start exploring opportunities that match your profile.</div>
        <a href="/jobs" class="btn-primary mt-4" style="text-decoration:none">Find Jobs</a>
      </div>`;
  }
}

/* ── Render Application Cards ── */
function renderApplications(apps) {
  const gridEl = document.getElementById('applications-grid');
  if (!gridEl) return;

  if (!apps.length) {
    gridEl.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-state-icon">🔎</div>
        <div class="empty-state-title">No applications in this category</div>
        <div class="empty-state-desc">Applications with this status will appear here.</div>
      </div>`;
    return;
  }

  gridEl.innerHTML = '';
  apps.forEach(app => {
    const card = createApplicationCard(app);
    gridEl.appendChild(card);
  });
}

function createApplicationCard(app) {
  const color = window.avatarColor(app.company || app.job_title || '');
  const initials = window.getInitials(app.company || app.job_title || '?');
  const dateStr = window.formatDate(app.created_at || app.applied_date || '');
  const status = (app.status || 'draft').toLowerCase();

  const div = document.createElement('div');
  div.className = 'stat-card cursor-pointer hover:shadow-md transition-shadow';
  div.dataset.appId = app.id;

  div.innerHTML = `
    <div class="flex items-start gap-3 mb-3">
      <div class="company-avatar" style="background:${color}">${escapeHtml(initials)}</div>
      <div class="flex-1 min-w-0">
        <div class="font-semibold text-gray-900 text-sm truncate">${escapeHtml(app.job_title || '—')}</div>
        <div class="text-xs text-gray-500 mt-0.5">${escapeHtml(app.company || '—')}</div>
      </div>
    </div>
    <div class="flex items-center justify-between mt-3">
      <div class="text-xs text-gray-400">Applied: ${escapeHtml(dateStr)}</div>
      ${window.statusBadge(status)}
    </div>
    ${app.match_score ? `<div class="mt-2">${window.matchBadge(app.match_score)}</div>` : ''}
    <button class="btn-secondary w-full mt-3" style="font-size:0.8rem;padding:0.4rem 0.75rem"
      onclick="viewApplication('${escapeHtml(app.id)}')">View Application</button>`;

  div.addEventListener('click', e => {
    if (!e.target.tagName === 'BUTTON') viewApplication(app.id);
  });

  return div;
}

/* ── Status Filter Tabs ── */
function initStatusTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      currentFilter = btn.dataset.status || 'all';
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderApplications(filterApps(currentFilter));
    });
  });
}

function filterApps(status) {
  if (status === 'all') return allApplications;
  return allApplications.filter(a => (a.status || '').toLowerCase() === status);
}

/* ── Stats Summary ── */
function updateSummaryStats() {
  const total     = allApplications.length;
  const pending   = allApplications.filter(a => ['draft','pending'].includes((a.status||'').toLowerCase())).length;
  const submitted = allApplications.filter(a => (a.status||'').toLowerCase() === 'submitted').length;
  const interviews = allApplications.filter(a => (a.status||'').toLowerCase() === 'interview').length;

  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set('stat-total', total);
  set('stat-pending', pending);
  set('stat-submitted', submitted);
  set('stat-interviews', interviews);
}

/* ── Detail Modal ── */
function initDetailModal() {
  const closeBtn = document.getElementById('close-detail-modal');
  if (closeBtn) closeBtn.addEventListener('click', () => closeModal('application-detail-modal'));

  const approveBtn = document.getElementById('btn-approve-submit');
  if (approveBtn) approveBtn.addEventListener('click', approveAndSubmit);

  const statusSelect = document.getElementById('detail-status-select');
  if (statusSelect) statusSelect.addEventListener('change', () => updateStatusFromSelect(statusSelect.value));
}

async function viewApplication(appId) {
  activeApplicationId = appId;
  const app = allApplications.find(a => a.id === appId);
  if (!app) return;

  // Populate modal
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val || '—'; };
  const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };

  set('detail-job-title',    app.job_title || '');
  set('detail-company',      app.company || '');
  set('detail-location',     app.location || '');
  set('detail-date',         window.formatDate(app.created_at || app.applied_date || ''));
  set('detail-name',         app.candidate_name || '');
  set('detail-email',        app.candidate_email || '');
  set('detail-phone',        app.candidate_phone || '');
  set('detail-location-cand', app.candidate_location || '');

  const statusEl = document.getElementById('detail-status-badge');
  if (statusEl) statusEl.innerHTML = window.statusBadge(app.status || 'draft');

  const statusSelect = document.getElementById('detail-status-select');
  if (statusSelect) statusSelect.value = (app.status || 'draft').toLowerCase();

  // Cover letter
  const clArea = document.getElementById('detail-cover-letter');
  if (clArea) clArea.value = app.cover_letter || '';

  // Approve button visibility
  const approveBtn = document.getElementById('btn-approve-submit');
  if (approveBtn) {
    const status = (app.status || '').toLowerCase();
    approveBtn.style.display = ['draft', 'pending'].includes(status) ? '' : 'none';
  }

  openModal('application-detail-modal');
}

async function updateStatus(appId, newStatus) {
  try {
    await window.api.put(`/api/applications/${appId}`, { status: newStatus });
    const app = allApplications.find(a => a.id === appId);
    if (app) app.status = newStatus;
    updateSummaryStats();
    renderApplications(filterApps(currentFilter));
    window.showToast(`Status updated to ${STATUS_LABELS[newStatus] || newStatus}`, 'success');
  } catch (err) {
    window.showToast(err.message || 'Could not update status.', 'error');
  }
}

async function updateStatusFromSelect(newStatus) {
  if (!activeApplicationId) return;
  await updateStatus(activeApplicationId, newStatus);

  // Update badge in modal
  const statusEl = document.getElementById('detail-status-badge');
  if (statusEl) statusEl.innerHTML = window.statusBadge(newStatus);

  // Hide approve button if no longer pending
  const approveBtn = document.getElementById('btn-approve-submit');
  if (approveBtn) {
    approveBtn.style.display = ['draft', 'pending'].includes(newStatus) ? '' : 'none';
  }
}

async function approveAndSubmit() {
  if (!activeApplicationId) return;

  const btn = document.getElementById('btn-approve-submit');
  window.setButtonLoading(btn, true, 'Submitting…');

  // Save cover letter edits first
  const clArea = document.getElementById('detail-cover-letter');
  if (clArea) {
    try {
      await window.api.put(`/api/applications/${activeApplicationId}`, {
        cover_letter: clArea.value,
        status: 'submitted',
      });
    } catch (_) {}
  }

  try {
    await window.api.put(`/api/applications/${activeApplicationId}`, { status: 'submitted' });
    const app = allApplications.find(a => a.id === activeApplicationId);
    if (app) app.status = 'submitted';

    window.showToast('Application submitted successfully!', 'success');
    updateSummaryStats();
    renderApplications(filterApps(currentFilter));
    closeModal('application-detail-modal');
  } catch (err) {
    window.showToast(err.message || 'Submission failed.', 'error');
    window.setButtonLoading(btn, false);
  }
}

/* ── Skeleton ── */
function showGridSkeleton(gridEl) {
  gridEl.innerHTML = Array.from({ length: 6 }).map(() => `
    <div class="stat-card">
      <div class="flex items-start gap-3 mb-3">
        <div class="skeleton" style="width:2.5rem;height:2.5rem;border-radius:0.5rem"></div>
        <div class="flex-1">
          <div class="skeleton" style="height:0.875rem;width:70%;margin-bottom:0.5rem"></div>
          <div class="skeleton" style="height:0.75rem;width:45%"></div>
        </div>
      </div>
      <div class="skeleton" style="height:0.75rem;width:55%;margin-top:0.75rem"></div>
      <div class="skeleton" style="height:2rem;width:100%;margin-top:0.75rem;border-radius:0.5rem"></div>
    </div>`).join('');
}

/* ── Utility ── */
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(String(str)));
  return d.innerHTML;
}

// Expose for inline handlers
window.viewApplication = viewApplication;
window.updateStatus    = updateStatus;
