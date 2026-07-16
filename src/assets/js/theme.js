(function () {
  const KEY = "sds-theme";
  const buttons = document.querySelectorAll(".theme-switch button");

  function apply(choice) {
    if (choice === "system") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", choice);
    }
    buttons.forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.themeChoice === choice));
    });
  }

  let saved = "system";
  try {
    const v = localStorage.getItem(KEY);
    if (v === "light" || v === "dark" || v === "system") saved = v;
  } catch (e) { /* private mode etc. */ }
  apply(saved);

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const choice = btn.dataset.themeChoice;
      try { localStorage.setItem(KEY, choice); } catch (e) { /* ignore */ }
      apply(choice);
    });
  });
})();
