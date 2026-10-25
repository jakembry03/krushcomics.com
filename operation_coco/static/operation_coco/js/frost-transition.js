/*
 * Frost transition: links marked data-frost-transition fade the screen to
 * frosty white before navigating. Skipped with reduced motion, and for
 * clicks that open a new tab or window.
 */
(function () {
  "use strict";

  var flash = document.querySelector(".frost-flash");
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  if (!flash) {
    return;
  }

  function duration() {
    var value = getComputedStyle(document.documentElement).getPropertyValue("--t-frost-transition");
    var ms = parseFloat(value);
    return isNaN(ms) ? 400 : ms;
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a[data-frost-transition]");
    if (!link || event.defaultPrevented || reducedMotion.matches) {
      return;
    }
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }

    event.preventDefault();
    flash.classList.remove("frost-flash--arrive");
    flash.classList.add("is-active");
    window.setTimeout(function () {
      window.location.href = link.href;
    }, duration());
  });

  // Coming back with the browser's Back button can restore the page
  // mid-transition, so clear the frost.
  window.addEventListener("pageshow", function () {
    flash.classList.remove("is-active");
  });
})();
