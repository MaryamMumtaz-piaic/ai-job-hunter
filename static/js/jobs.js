/* ── AI Job Hunter — Jobs Split-View Page ── */

let allJobs = [];
let filteredJobs = [];
let selectedJobId = null;
let savedJobIds = new Set();
let userProfile = null;
let coverLetterText = '';
let applyingJobId = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadJobs();
  initFilters();
  initApplyModal();
  initCoverLetterModal();
});

/* ── Load Jobs ── */
async function loadJobs() {
  const listEl = document.getElementById('job-list');
  if (!listEl) return;

  showListSkeleton(listEl);

  try {
    const data = await window.api.get('/api/jobs');
    allJobs = Array.isArray(data) ? data : (data.jobs || []);
    filteredJobs = [...allJobs];

    // Load saved job ids
    try {
      const saved = await window.api.get('/api/jobs/saved');
      savedJobIds = new Set((saved || []).map(j => j.id || j.job_id));
    } catch (_) {}

    updateJobCount();
    renderJobList(filteredJobs);

    if (filteredJobs.length > 0) selectJob(filteredJobs[0].id);
  } catch (err) {
    listEl.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <div class="empty-state-title">No jobs found</div>
        <div class="empty-state-desc">Analyze your resume to find matching jobs.</div>
        <a href="/analyze" class="btn-primary mt-4" style="text-decoration:none">Analyze My Resume</a>
      </div>`;
  }
}

/* ── Render Job List ── */
function renderJobList(jobs) {
  const listEl = document.getElementById('job-list');
  if (!listEl) return;

  if (!jobs.length) {
    listEl.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🎯</div>
        <div class="empty-state-title">No results</div>
        <div class="empty-state-desc">Try adjusting your filters or search query.</div>
      </div>`;
    clearJobDetail();
    return;
  }

  listEl.innerHTML = '';
  jobs.forEach(job => {
    const card = createJobCard(job);
    listEl.appendChild(card);
  });
}

function createJobCard(job) {
  const score = job.match_score || 0;
  const initials = window.getInitials(job.company || job.title);
  const color = window.avatarColor(job.company || '');
  const saved = savedJobIds.has(job.id);

  const div = document.createElement('div');
  div.className = `job-card${selectedJobId === job.id ? ' active' : ''}`;
  div.dataset.jobId = job.id;

  const salaryText = window.formatSalary(job.salary_min, job.salary_max, job.currency);
  const scoreClass = score >= 80 ? 'match-high' : score >= 60 ? 'match-mid' : 'match-low';

  div.innerHTML = `
    <div class="flex items-start gap-3">
      <div class="company-avatar" style="background:${color}">${escapeHtml(initials)}</div>
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-2">
          <div class="font-semibold text-gray-900 text-sm truncate">${escapeHtml(job.title)}</div>
          ${score ? `<span class="match-badge ${scoreClass} flex-shrink-0">${Math.round(score)}%</span>` : ''}
        </div>
        <div class="text-xs text-gray-500 mt-0.5">${escapeHtml(job.company || '—')}</div>
        <div class="text-xs text-gray-400 mt-1">${escapeHtml(job.location || job.country || '')}</div>
        <div class="flex items-center gap-2 mt-2 flex-wrap">
          <span class="tag">${escapeHtml(job.employment_type || 'Full-time')}</span>
          <span class="tag tag-blue">${escapeHtml(job.work_mode || 'On-site')}</span>
          ${salaryText !== 'Salary not disclosed' ? `<span class="text-xs text-gray-500">${escapeHtml(salaryText)}</span>` : ''}
        </div>
      </div>
    </div>`;

  div.addEventListener('click', () => selectJob(job.id));
  return div;
}

/* ── Select Job ── */
function selectJob(jobId) {
  selectedJobId = jobId;

  // Update active state on cards
  document.querySelectorAll('.job-card').forEach(card => {
    card.classList.toggle('active', card.dataset.jobId === jobId);
  });

  const job = allJobs.find(j => j.id === jobId);
  if (job) renderJobDetail(job);

  // Mobile: scroll to detail
  if (window.innerWidth <= 768) {
    const detail = document.getElementById('job-detail-panel');
    if (detail) detail.scrollIntoView({ behavior: 'smooth' });
  }
}

/* ── Render Job Detail ── */
function renderJobDetail(job) {
  const panel = document.getElementById('job-detail-panel');
  if (!panel) return;

  const score = job.match_score || 0;
  const scoreClass = score >= 80 ? 'match-high' : score >= 60 ? 'match-mid' : 'match-low';
  const color = window.avatarColor(job.company || '');
  const initials = window.getInitials(job.company || job.title);
  const saved = savedJobIds.has(job.id);
  const salaryText = window.formatSalary(job.salary_min, job.salary_max, job.currency);

  const matchedSkills = job.matched_skills || [];
  const missingSkills = job.missing_skills || [];

  panel.innerHTML = `
    <div class="flex items-start gap-4 mb-6">
      <div class="company-avatar company-avatar-lg" style="background:${color}">${escapeHtml(initials)}</div>
      <div class="flex-1">
        <h2 class="text-xl font-bold text-gray-900">${escapeHtml(job.title)}</h2>
        <div class="text-gray-600 font-medium">${escapeHtml(job.company || '')}</div>
        <div class="flex flex-wrap gap-2 mt-2 text-sm text-gray-500">
          <span>📍 ${escapeHtml(job.location || job.country || '—')}</span>
          <span>· ${escapeHtml(job.work_mode || '—')}</span>
          <span>· ${escapeHtml(job.employment_type || '—')}</span>
        </div>
        <div class="mt-1 text-sm font-semibold text-gray-700">${escapeHtml(salaryText)}</div>
      </div>
      ${score ? `
        <div class="match-circle-lg flex-shrink-0">
          <span class="match-pct">${Math.round(score)}%</span>
          <span class="match-label">match</span>
        </div>` : ''}
    </div>

    ${job.why_match ? `
    <div class="bg-indigo-50 border border-indigo-100 rounded-lg p-4 mb-6">
      <div class="text-sm font-semibold text-indigo-700 mb-1">Why you're a match</div>
      <div class="text-sm text-indigo-600">${escapeHtml(job.why_match)}</div>
    </div>` : ''}

    ${(matchedSkills.length || missingSkills.length) ? `
    <div class="grid grid-cols-2 gap-4 mb-6">
      ${matchedSkills.length ? `
      <div>
        <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Matched Skills</div>
        <div class="flex flex-wrap gap-1.5">
          ${matchedSkills.map(s => `<span class="tag tag-green">${escapeHtml(s)}</span>`).join('')}
        </div>
      </div>` : ''}
      ${missingSkills.length ? `
      <div>
        <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Potential Gaps</div>
        <div class="flex flex-wrap gap-1.5">
          ${missingSkills.map(s => `<span class="tag tag-red">${escapeHtml(s)}</span>`).join('')}
        </div>
      </div>` : ''}
    </div>` : ''}

    ${job.description ? `
    <div class="mb-6">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">About the Role</h3>
      <div class="text-sm text-gray-600 leading-relaxed">${escapeHtml(job.description)}</div>
    </div>` : ''}

    ${job.requirements && job.requirements.length ? `
    <div class="mb-6">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">Requirements</h3>
      <ul class="text-sm text-gray-600 space-y-1 list-disc list-inside">
        ${job.requirements.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
      </ul>
    </div>` : ''}

    ${job.skills && job.skills.length ? `
    <div class="mb-6">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">Required Skills</h3>
      <div class="flex flex-wrap gap-1.5">
        ${job.skills.map(s => `<span class="tag">${escapeHtml(s)}</span>`).join('')}
      </div>
    </div>` : ''}

    ${job.benefits && job.benefits.length ? `
    <div class="mb-6">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">Benefits</h3>
      <ul class="text-sm text-gray-600 space-y-1 list-disc list-inside">
        ${job.benefits.map(b => `<li>${escapeHtml(b)}</li>`).join('')}
      </ul>
    </div>` : ''}

    ${job.company_description ? `
    <div class="mb-6">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">About ${escapeHtml(job.company || 'the Company')}</h3>
      <div class="text-sm text-gray-600">${escapeHtml(job.company_description)}</div>
    </div>` : ''}

    <div class="flex flex-wrap gap-3 mt-8 pt-6 border-t border-gray-100">
      <button onclick="openApplyFlow('${escapeHtml(job.id)}')" class="btn-primary">Apply Now</button>
      <button onclick="toggleSaveJob('${escapeHtml(job.id)}')" id="save-btn-${escapeHtml(job.id)}"
        class="btn-secondary ${saved ? 'border-indigo-300 text-indigo-600' : ''}">
        ${saved ? '★ Saved' : '☆ Save Job'}
      </button>
      <button onclick="openCoverLetterFlow('${escapeHtml(job.id)}')" class="btn-secondary">
        ✉ Generate Cover Letter
      </button>
    </div>`;
}

function clearJobDetail() {
  const panel = document.getElementById('job-detail-panel');
  if (panel) panel.innerHTML = `
    <div class="empty-state" style="height:100%">
      <div class="empty-state-icon">👈</div>
      <div class="empty-state-title">Select a job</div>
      <div class="empty-state-desc">Choose a job from the list to view details.</div>
    </div>`;
}

/* ── Save Job ── */
async function toggleSaveJob(jobId) {
  try {
    const isSaved = savedJobIds.has(jobId);
    await window.api.post(`/api/jobs/${jobId}/save`, { saved: !isSaved });
    if (isSaved) {
      savedJobIds.delete(jobId);
      window.showToast('Job removed from saved.', 'info');
    } else {
      savedJobIds.add(jobId);
      window.showToast('Job saved!', 'success');
    }
    // Re-render detail save button
    const btn = document.getElementById(`save-btn-${jobId}`);
    if (btn) {
      btn.textContent = savedJobIds.has(jobId) ? '★ Saved' : '☆ Save Job';
      btn.classList.toggle('border-indigo-300', savedJobIds.has(jobId));
      btn.classList.toggle('text-indigo-600', savedJobIds.has(jobId));
    }
  } catch (err) {
    window.showToast(err.message || 'Could not save job.', 'error');
  }
}

/* ── Filters & Search ── */
function initFilters() {
  const searchInput  = document.getElementById('job-search');
  const modeFilter   = document.getElementById('filter-mode');
  const typeFilter   = document.getElementById('filter-type');
  const countryFilter = document.getElementById('filter-country');

  const applyFilters = window.debounce(() => {
    const q = (searchInput?.value || '').toLowerCase();
    const mode    = modeFilter?.value || '';
    const type    = typeFilter?.value || '';
    const country = countryFilter?.value || '';

    filteredJobs = allJobs.filter(job => {
      const textMatch = !q || job.title?.toLowerCase().includes(q) || job.company?.toLowerCase().includes(q);
      const modeMatch = !mode || job.work_mode === mode;
      const typeMatch = !type || job.employment_type === type;
      const countryMatch = !country || job.country === country;
      return textMatch && modeMatch && typeMatch && countryMatch;
    });

    updateJobCount();
    renderJobList(filteredJobs);
    if (filteredJobs.length) selectJob(filteredJobs[0].id);
    else clearJobDetail();
  }, 250);

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (modeFilter)  modeFilter.addEventListener('change', applyFilters);
  if (typeFilter)  typeFilter.addEventListener('change', applyFilters);
  if (countryFilter) countryFilter.addEventListener('change', applyFilters);
}

function updateJobCount() {
  const countEl = document.getElementById('job-count');
  if (countEl) countEl.textContent = `${filteredJobs.length} job${filteredJobs.length !== 1 ? 's' : ''} found`;
}

/* ── Apply Modal ── */
function initApplyModal() {
  const closeBtn = document.getElementById('close-apply-modal');
  if (closeBtn) closeBtn.addEventListener('click', () => closeModal('apply-modal'));

  const submitBtn = document.getElementById('btn-submit-application');
  if (submitBtn) submitBtn.addEventListener('click', submitApplicationHandler);
}

async function openApplyFlow(jobId) {
  applyingJobId = jobId;
  openModal('apply-modal');

  const job = allJobs.find(j => j.id === jobId);
  const jobTitleEl = document.getElementById('apply-job-title');
  const jobCompanyEl = document.getElementById('apply-job-company');
  if (jobTitleEl && job) jobTitleEl.textContent = job.title;
  if (jobCompanyEl && job) jobCompanyEl.textContent = job.company;

  // Load user profile to prefill
  try {
    if (!userProfile) userProfile = await window.api.get('/api/profile');
    prefillApplicationForm(userProfile);
  } catch (_) {}
}

function prefillApplicationForm(profile) {
  const fields = {
    'apply-name':     profile.full_name || '',
    'apply-email':    profile.email || '',
    'apply-phone':    profile.phone || '',
    'apply-location': profile.location || '',
    'apply-linkedin': profile.linkedin || '',
    'apply-github':   profile.github || '',
  };
  Object.entries(fields).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (el) el.value = val;
  });
}

async function submitApplicationHandler() {
  const job = allJobs.find(j => j.id === applyingJobId);
  if (!job) return;

  const coverLetterEl = document.getElementById('apply-cover-letter');
  const payload = {
    job_id: applyingJobId,
    cover_letter: coverLetterEl?.value || coverLetterText,
    candidate_name:     document.getElementById('apply-name')?.value || '',
    candidate_email:    document.getElementById('apply-email')?.value || '',
    candidate_phone:    document.getElementById('apply-phone')?.value || '',
    candidate_location: document.getElementById('apply-location')?.value || '',
    candidate_linkedin: document.getElementById('apply-linkedin')?.value || '',
    candidate_github:   document.getElementById('apply-github')?.value || '',
  };

  const btn = document.getElementById('btn-submit-application');
  window.setButtonLoading(btn, true, 'Submitting…');

  try {
    await window.api.post('/api/applications', payload);
    window.showToast('Application submitted successfully!', 'success');
    closeModal('apply-modal');
    // Update apply button in detail panel
    const applyBtn = document.querySelector(`[onclick="openApplyFlow('${applyingJobId}')"]`);
    if (applyBtn) { applyBtn.textContent = '✓ Applied'; applyBtn.disabled = true; }
  } catch (err) {
    window.showToast(err.message || 'Submission failed. Try again.', 'error');
  } finally {
    window.setButtonLoading(btn, false);
  }
}

/* ── Cover Letter Modal ── */
function initCoverLetterModal() {
  const closeBtn = document.getElementById('close-cl-modal');
  if (closeBtn) closeBtn.addEventListener('click', () => closeModal('cover-letter-modal'));

  const copyBtn = document.getElementById('btn-copy-cl');
  if (copyBtn) copyBtn.addEventListener('click', copyCoverLetter);

  const regenBtn = document.getElementById('btn-regen-cl');
  if (regenBtn) regenBtn.addEventListener('click', () => generateCoverLetter(applyingJobId));

  const useBtn = document.getElementById('btn-use-cl');
  if (useBtn) useBtn.addEventListener('click', useCoverLetter);
}

async function openCoverLetterFlow(jobId) {
  applyingJobId = jobId;
  openModal('cover-letter-modal');
  const job = allJobs.find(j => j.id === jobId);
  const titleEl = document.getElementById('cl-job-title');
  if (titleEl && job) titleEl.textContent = `${job.title} at ${job.company}`;
  await generateCoverLetter(jobId);
}

async function generateCoverLetter(jobId) {
  const textarea = document.getElementById('cl-textarea');
  const status   = document.getElementById('cl-status');
  if (!textarea) return;

  if (status) status.innerHTML = '<span class="spinner"></span> Generating…';
  textarea.disabled = true;
  textarea.value = '';

  try {
    const data = await window.api.post('/api/cover-letter/generate', { job_id: jobId });
    coverLetterText = data.cover_letter || '';
    textarea.value = coverLetterText;
    textarea.disabled = false;
    if (status) status.textContent = '';
    window.showToast('Cover letter generated!', 'success');
  } catch (err) {
    textarea.disabled = false;
    if (status) status.textContent = '';
    window.showToast(err.message || 'Could not generate cover letter.', 'error');
  }
}

function copyCoverLetter() {
  const textarea = document.getElementById('cl-textarea');
  if (!textarea || !textarea.value) return;
  navigator.clipboard.writeText(textarea.value).then(() => {
    window.showToast('Copied to clipboard!', 'success');
  }).catch(() => {
    textarea.select();
    document.execCommand('copy');
    window.showToast('Copied!', 'success');
  });
}

function useCoverLetter() {
  const textarea = document.getElementById('cl-textarea');
  if (textarea) coverLetterText = textarea.value;
  closeModal('cover-letter-modal');
  // Open apply modal with cover letter pre-filled
  openApplyFlow(applyingJobId).then(() => {
    const applyClEl = document.getElementById('apply-cover-letter');
    if (applyClEl) applyClEl.value = coverLetterText;
  });
}

/* ── Skeleton Loader ── */
function showListSkeleton(listEl) {
  listEl.innerHTML = Array.from({ length: 5 }).map(() => `
    <div class="job-card" style="pointer-events:none">
      <div class="flex items-start gap-3">
        <div class="skeleton" style="width:2.5rem;height:2.5rem;border-radius:0.5rem"></div>
        <div class="flex-1">
          <div class="skeleton" style="height:0.875rem;width:70%;margin-bottom:0.5rem"></div>
          <div class="skeleton" style="height:0.75rem;width:45%;margin-bottom:0.5rem"></div>
          <div class="skeleton" style="height:0.75rem;width:55%"></div>
        </div>
      </div>
    </div>`).join('');
}

/* ── Utility ── */
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(String(str)));
  return d.innerHTML;
}

// Expose for inline onclick handlers
window.openApplyFlow = openApplyFlow;
window.toggleSaveJob = toggleSaveJob;
window.openCoverLetterFlow = openCoverLetterFlow;
