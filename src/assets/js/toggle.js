(function () {
  document.querySelectorAll('[data-wbw-toggle]').forEach(function (btn) {
    const panelId = btn.getAttribute('aria-controls');
    const panel = document.getElementById(panelId);
    if (!panel) return;
    btn.addEventListener('click', function () {
      const open = panel.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
    });
  });
})();
