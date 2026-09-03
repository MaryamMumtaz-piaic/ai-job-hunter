document.addEventListener('DOMContentLoaded', () => {
  /* ── Password Strength ── */
  function calcStrength(pw) {
    let score = 0;
    if (pw.length >= 8)  score++;
    if (pw.length >= 12) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    return score; // 0–5
  }

  function renderStrength(score, container) {
    if (!container) return;
    const levels = ['', 'strength-weak', 'strength-fair', 'strength-fair', 'strength-good', 'strength-strong'];
    const labels = ['', 'Weak', 'Fair', 'Fair', 'Good', 'Strong'];
    container.className = `strength-bar ${levels[score] || ''}`;
    const fill = container.querySelector('.strength-fill');
    if (fill) fill.style.width = `${(score / 5) * 100}%`;
    const labelEl = document.getElementById('pw-strength-label');
    if (labelEl) { labelEl.textContent = labels[score] || ''; }
  }

  function showFieldError(fieldId, msg) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    field.classList.add('border-red-400');
    let err = field.parentElement.querySelector('.field-error');
    if (!err) {
      err = document.createElement('p');
      err.className = 'field-error text-xs text-red-500 mt-1';
      field.parentElement.appendChild(err);
    }
    err.textContent = msg;
  }

  function clearFieldErrors(form) {
    form.querySelectorAll('.field-error').forEach(e => e.remove());
    form.querySelectorAll('.border-red-400').forEach(e => e.classList.remove('border-red-400'));
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  /* ── Signup ── */
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    const pwInput = document.getElementById('password');
    const strengthBar = document.getElementById('pw-strength-bar');

    if (pwInput && strengthBar) {
      pwInput.addEventListener('input', () => {
        const score = calcStrength(pwInput.value);
        renderStrength(score, strengthBar);
      });
    }

    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearFieldErrors(signupForm);

      const name     = document.getElementById('full_name')?.value.trim() || '';
      const email    = document.getElementById('email')?.value.trim() || '';
      const password = document.getElementById('password')?.value || '';
      const confirm  = document.getElementById('confirm_password')?.value || '';

      let valid = true;
      if (!name) { showFieldError('full_name', 'Full name is required'); valid = false; }
      if (!email || !validateEmail(email)) { showFieldError('email', 'Enter a valid email address'); valid = false; }
      if (password.length < 6) { showFieldError('password', 'Password must be at least 6 characters'); valid = false; }
      if (password !== confirm) { showFieldError('confirm_password', 'Passwords do not match'); valid = false; }
      if (!valid) return;

      const btn = signupForm.querySelector('[type="submit"]');
      window.setButtonLoading(btn, true, 'Creating account…');

      try {
        await window.api.post('/api/auth/signup', { full_name: name, email, password, confirm_password: confirm });
        window.showToast('Account created! Please sign in.', 'success');
        setTimeout(() => { window.location.href = '/signin'; }, 1200);
      } catch (err) {
        window.showToast(err.message || 'Signup failed. Please try again.', 'error');
        window.setButtonLoading(btn, false);
      }
    });
  }

  /* ── Signin ── */
  const signinForm = document.getElementById('signin-form');
  if (signinForm) {
    signinForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearFieldErrors(signinForm);

      const email    = document.getElementById('email')?.value.trim() || '';
      const password = document.getElementById('password')?.value || '';

      let valid = true;
      if (!email || !validateEmail(email)) { showFieldError('email', 'Enter a valid email address'); valid = false; }
      if (!password) { showFieldError('password', 'Password is required'); valid = false; }
      if (!valid) return;

      const btn = signinForm.querySelector('[type="submit"]');
      window.setButtonLoading(btn, true, 'Signing in…');

      try {
        const data = await window.api.post('/api/auth/signin', { email, password });
        window.showToast(`Welcome back, ${data.user?.full_name?.split(' ')[0] || 'there'}!`, 'success');
        setTimeout(() => { window.location.href = data.redirect || '/dashboard'; }, 800);
      } catch (err) {
        window.showToast(err.message || 'Invalid email or password.', 'error');
        window.setButtonLoading(btn, false);
      }
    });
  }

  /* ── Password Toggle Visibility ── */
  document.querySelectorAll('[data-toggle-password]').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.togglePassword;
      const input = document.getElementById(targetId);
      if (!input) return;
      if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
      } else {
        input.type = 'password';
        btn.textContent = '👁';
      }
    });
  });
});
