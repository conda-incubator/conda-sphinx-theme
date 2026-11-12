(function () {
  "use strict";

  function init() {
    for (const menu of document.querySelectorAll(
      "#navbar-main-elements .dropdown-menu"
    )) {
      const bar = menu.querySelector(".conda-projects-filter");
      const input = bar && bar.querySelector("input");
      const empty = menu.querySelector(".conda-projects-empty");
      if (!input) continue;

      const items = Array.from(menu.querySelectorAll("li")).filter((li) =>
        li.querySelector(".dropdown-item.nav-external, .dropdown-item.nav-internal")
      );

      const apply = () => {
        const query = input.value.trim().toLowerCase();
        let shown = 0;
        for (const li of items) {
          const match = !query || li.textContent.toLowerCase().includes(query);
          li.hidden = !match;
          if (match) shown += 1;
        }
        if (empty) empty.hidden = shown > 0;
      };

      input.addEventListener("input", apply);
      input.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && input.value) {
          input.value = "";
          apply();
          event.stopPropagation();
        }
      });
      document.addEventListener("hidden.bs.dropdown", () => {
        input.value = "";
        apply();
      });

      // Only reveal the filter once it can actually filter something
      bar.hidden = false;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
