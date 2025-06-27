/**
 * Emergency navigation helper for the employee multi-step form.
 * Goal: guarantee that
 *   1. The correct step content is visible
 *   2. A conspicuous submit / continue button is always available
 * This code purposefully ignores existing CSS/JS and forces visibility.
 */
(function () {
  console.log('🚨 Emergency form navigation fix loaded');

  function getCurrentStep() {
    const input = document.querySelector('input[name="step"]');
    return input ? parseInt(input.value, 10) || 1 : 1;
  }

  function showCurrentStep(step) {
    // hide all steps
    document.querySelectorAll('.form-step').forEach((d) => {
      d.style.display = 'none';
    });
    // show current
    const active = document.getElementById(`step-${step}-content`);
    if (active) active.style.display = 'block';

    // update indicator bar
    document.querySelectorAll('.step').forEach((el, idx) => {
      const n = idx + 1;
      el.classList.toggle('active', n === step);
      el.classList.toggle('completed', n < step);
    });
  }

  function ensureFixedButton(step) {
    if (document.querySelector('.emergency-submit-button')) return; // already added

    const btn = document.createElement('div');
    btn.className = 'emergency-submit-button';
    btn.style.cssText =
      'position:fixed;left:0;bottom:0;width:100%;background:#0d6efd;color:#fff;' +
      'font-size:18px;font-weight:600;text-align:center;padding:14px 0;z-index:9999;cursor:pointer;';

    const labels = [
      '',
      'Continue to Contact Info (Step 2)',
      'Continue to Employment Info (Step 3)',
      'Continue to Financial Info (Step 4)',
      'Create Employee',
    ];
    btn.textContent = labels[Math.min(step, 4)];

    btn.addEventListener('click', () => {
      const form = document.querySelector('form');
      if (form) form.submit();
    });

    document.body.appendChild(btn);
  }

  function applyFix() {
    const step = getCurrentStep();
    showCurrentStep(step);
    ensureFixedButton(step);
  }

  // initial run
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyFix);
  } else {
    applyFix();
  }

  // re-run on any user click (defensive)
  document.addEventListener('click', () => setTimeout(applyFix, 50));
})();
