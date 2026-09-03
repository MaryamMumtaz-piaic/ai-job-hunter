/* ── AI Job Hunter — Analyze Page ── */

let currentStep = 1;
let resumeFileId = null;
let portfolioFileId = null;
let extractedSkills = [];
let titlesTagInput = null;
let skillsTagInput = null;

/* ── Stage Definitions ── */
const STAGES = [
  { id: 'stage-resume', label: 'Reading resume',             delay: 800  },
  { id: 'stage-skills', label: 'Extracting skills',          delay: 1800 },
  { id: 'stage-prefs',  label: 'Processing job preferences', delay: 3000 },
  { id: 'stage-scan',   label: 'Scanning job database',      delay: 4200 },
  { id: 'stage-match',  label: 'Matching opportunities',     delay: 5800 },
  { id: 'stage-rank',   label: 'Ranking by relevance',       delay: 7500 },
  { id: 'stage-prep',   label: 'Preparing recommendations',  delay: 9000 },
];

document.addEventListener('DOMContentLoaded', () => {
  initDropzone('resume-dropzone', 'resume-file-input', 'resume', handleResumeUpload);
  initDropzone('portfolio-dropzone', 'portfolio-file-input', 'portfolio', handlePortfolioUpload);
  initTagInputs();
  initPreferences();
  initStepNav();
});

/* ── Dropzone Init ── */
function initDropzone(zoneId, inputId, type, handler) {
  const zone = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  if (!zone || !input) return;

  zone.addEventListener('click', () => input.click());
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) handler(file, zone);
  });
  input.addEventListener('change', () => {
    if (input.files[0]) handler(input.files[0], zone);
  });
}

/* ── Resume Upload ── */
async function handleResumeUpload(file, zone) {
  if (!validateFile(file)) return;
  setZoneUploading(zone, file.name);
  try {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('type', 'resume');
    const data = await window.api.postForm('/api/resume/upload', fd);
    resumeFileId = data.file_id;
    setZoneDone(zone, file.name, 'resume');
    window.showToast('Resume uploaded successfully!', 'success');
    enableStep2Button();
    // Analyze resume in background to prefill skills
    analyzeResumeBackground(data.file_id);
  } catch (err) {
    setZoneError(zone);
    window.showToast(err.message || 'Upload failed. Try again.', 'error');
  }
}

/* ── Portfolio Upload ── */
async function handlePortfolioUpload(file, zone) {
  if (!validateFile(file)) return;
  setZoneUploading(zone, file.name);
  try {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('type', 'portfolio');
    const data = await window.api.postForm('/api/resume/upload', fd);
    portfolioFileId = data.file_id;
    setZoneDone(zone, file.name, 'portfolio');
    window.showToast('Portfolio uploaded!', 'success');
  } catch (err) {
    setZoneError(zone);
    window.showToast(err.message || 'Upload failed.', 'error');
  }
}

function validateFile(file) {
  const allowed = ['application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'];
  const ext = file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(file.type) && !['pdf','docx','txt'].includes(ext)) {
    window.showToast('Please upload a PDF, DOCX, or TXT file.', 'error');
    return false;
  }
  if (file.size > 10 * 1024 * 1024) {
    window.showToast('File must be under 10 MB.', 'error');
    return false;
  }
  return true;
}

function setZoneUploading(zone, name) {
  zone.innerHTML = `
    <div class="flex flex-col items-center gap-2 text-indigo-600">
      <span class="spinner" style="width:2rem;height:2rem;border-width:3px"></span>
      <span class="text-sm font-medium">Uploading ${escapeHtml(name)}…</span>
    </div>`;
}

function setZoneDone(zone, name, type) {
  zone.classList.add('uploaded');
  zone.innerHTML = `
    <div class="flex flex-col items-center gap-2 text-emerald-600">
      <span style="font-size:2rem">✓</span>
      <span class="text-sm font-medium">${type === 'resume' ? 'Resume' : 'Portfolio'} uploaded</span>
      <span class="text-xs text-gray-500">${escapeHtml(name)}</span>
    </div>`;
}

function setZoneError(zone) {
  zone.innerHTML = `
    <div class="flex flex-col items-center gap-2 text-red-500">
      <span style="font-size:2rem">✕</span>
      <span class="text-sm font-medium">Upload failed — click to retry</span>
    </div>`;
}

/* ── Background Resume Analysis (prefill skills) ── */
async function analyzeResumeBackground(fileId) {
  try {
    const data = await window.api.post('/api/resume/analyze', { file_id: fileId });
    if (data.skills && data.skills.length) {
      extractedSkills = data.skills;
      if (skillsTagInput) skillsTagInput.setTags(extractedSkills);
    }
    if (data.job_titles && data.job_titles.length && titlesTagInput) {
      const existing = titlesTagInput.getTags();
      if (!existing.length) titlesTagInput.setTags(data.job_titles.slice(0, 3));
    }
  } catch (_) { /* silent — user can fill manually */ }
}

/* ── Tag Inputs ── */
function initTagInputs() {
  const titlesEl = document.getElementById('desired-titles-container');
  const skillsEl = document.getElementById('skills-container');
  if (titlesEl) {
    titlesTagInput = new window.TagInput(titlesEl, [], { placeholder: 'e.g. AI Engineer, Backend Developer…' });
  }
  if (skillsEl) {
    skillsTagInput = new window.TagInput(skillsEl, [], { placeholder: 'e.g. Python, FastAPI, React…' });
  }
}

/* ── Preferences Setup ── */
function initPreferences() {
  // Country select — "Any" value handling
  const countrySelect = document.getElementById('country');
  if (countrySelect) {
    countrySelect.addEventListener('change', () => {
      const cityRow = document.getElementById('city-row');
      if (cityRow) cityRow.style.display = countrySelect.value === 'Any' ? 'none' : '';
    });
  }
}

/* ── Step Navigation ── */
function initStepNav() {
  const nextBtn = document.getElementById('btn-next-step');
  const backBtn = document.getElementById('btn-back-step');
  const analyzeBtn = document.getElementById('btn-analyze');

  if (nextBtn) nextBtn.addEventListener('click', goToStep2);
  if (backBtn) backBtn.addEventListener('click', goToStep1);
  if (analyzeBtn) analyzeBtn.addEventListener('click', startAnalysis);
}

function enableStep2Button() {
  const btn = document.getElementById('btn-next-step');
  if (btn) { btn.disabled = false; btn.classList.remove('opacity-50', 'cursor-not-allowed'); }
}

function goToStep1() {
  currentStep = 1;
  showStep(1);
}

function goToStep2() {
  if (!resumeFileId) {
    window.showToast('Please upload your resume first.', 'warning');
    return;
  }
  currentStep = 2;
  showStep(2);
}

function showStep(n) {
  document.querySelectorAll('[data-step]').forEach(el => {
    el.style.display = el.dataset.step == n ? '' : 'none';
  });
  // Update step indicator dots
  document.querySelectorAll('.step-dot').forEach(dot => {
    const s = parseInt(dot.dataset.stepNum);
    dot.classList.toggle('active', s === n);
    dot.classList.toggle('complete', s < n);
    dot.classList.toggle('text-gray-400', s > n);
  });
  document.querySelectorAll('.step-line').forEach(line => {
    const s = parseInt(line.dataset.afterStep);
    line.classList.toggle('complete', s < n);
  });
}

/* ── Main Analysis Flow ── */
async function startAnalysis() {
  const prefs = collectPreferences();
  if (!prefs) return;  // validation failed

  // Save preferences
  try {
    await window.api.post('/api/profile/preferences', prefs);
    window.showToast('Preferences saved!', 'success');
  } catch (_) {}

  // Switch to loading screen
  showStep(3);

  const startTime = Date.now();
  let apiDone = false;
  let matchResults = null;

  // Kick off API call in parallel with animation
  const apiPromise = window.api.post('/api/jobs/analyze', prefs)
    .then(data => { apiDone = true; matchResults = data; })
    .catch(err => { apiDone = true; window.showToast(err.message || 'Analysis failed', 'error'); });

  // Run stage animation
  await runStageAnimation();

  // Wait for API if still running (max 60s total)
  const elapsed = Date.now() - startTime;
  if (!apiDone) {
    const maxWait = 60000 - elapsed;
    await Promise.race([apiPromise, sleep(maxWait)]);
  }

  if (matchResults && !matchResults.error) {
    window.showToast('Analysis complete! Loading your matches…', 'success');
    setTimeout(() => { window.location.href = '/jobs'; }, 600);
  } else {
    // Go to jobs anyway — backend may have partial results
    setTimeout(() => { window.location.href = '/jobs'; }, 600);
  }
}

async function runStageAnimation() {
  const progressFill = document.getElementById('analysis-progress-fill');

  for (let i = 0; i < STAGES.length; i++) {
    const stage = STAGES[i];
    const el = document.getElementById(stage.id);

    // Mark previous as complete
    if (i > 0) {
      const prev = document.getElementById(STAGES[i - 1].id);
      if (prev) setStageState(prev, 'complete');
    }
    if (el) setStageState(el, 'active');

    // Update progress bar
    if (progressFill) progressFill.style.width = `${Math.round(((i + 1) / STAGES.length) * 100)}%`;

    // Wait until this stage's delay from start
    const waitTime = i === 0 ? stage.delay : STAGES[i].delay - STAGES[i - 1].delay;
    await sleep(waitTime);
  }

  // Mark last stage complete
  const lastEl = document.getElementById(STAGES[STAGES.length - 1].id);
  if (lastEl) setStageState(lastEl, 'complete');
  if (progressFill) progressFill.style.width = '100%';

  await sleep(500);
}

function setStageState(el, state) {
  el.className = `stage-item stage-${state}`;
}

/* ── Collect Preferences from Form ── */
function collectPreferences() {
  const jobType   = document.getElementById('job_type')?.value || '';
  const workMode  = document.getElementById('work_mode')?.value || '';
  const country   = document.getElementById('country')?.value || '';
  const city      = document.getElementById('city')?.value.trim() || '';
  const expLevel  = document.getElementById('experience_level')?.value || '';
  const salMin    = parseFloat(document.getElementById('salary_min')?.value) || null;
  const salMax    = parseFloat(document.getElementById('salary_max')?.value) || null;
  const empPref   = document.getElementById('employment_pref')?.value || '';
  const titles    = titlesTagInput ? titlesTagInput.getTags() : [];
  const skills    = skillsTagInput ? skillsTagInput.getTags() : [];

  if (!jobType || !workMode) {
    window.showToast('Please fill in Job Type and Work Mode.', 'warning');
    return null;
  }

  return {
    job_type: jobType,
    work_mode: workMode,
    desired_titles: titles,
    country,
    city,
    salary_min: salMin,
    salary_max: salMax,
    experience_level: expLevel,
    employment_pref: empPref,
    skills,
    resume_file_id: resumeFileId,
    portfolio_file_id: portfolioFileId,
  };
}

/* ── Utilities ── */
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function escapeHtml(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(str));
  return d.innerHTML;
}
