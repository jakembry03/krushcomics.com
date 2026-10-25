/*
 * The FrostOS desktop's frozen icons: clicking one gives a tiny shake
 * and a "Frozen solid." tooltip, and nothing else.
 */
(function () {
  "use strict";

  var apps = document.getElementById("desktop-apps");
  if (!apps) {
    return;
  }

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var timers = new WeakMap();

  function cssTime(name, fallback) {
    var value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    var number = parseFloat(value);
    if (isNaN(number)) {
      return fallback;
    }
    return /ms$/.test(value) ? number : number * 1000;
  }

  apps.addEventListener("click", function (event) {
    var app = event.target.closest(".app.is-frozen");
    if (!app) {
      return;
    }
    event.preventDefault();

    if (!reducedMotion.matches) {
      app.classList.remove("is-shaking");
      void app.offsetWidth;
      app.classList.add("is-shaking");
    }

    var tooltip = app.querySelector(".app__tooltip");
    if (tooltip) {
      tooltip.textContent = "Frozen solid.";
      app.classList.add("is-tipped");
      window.clearTimeout(timers.get(app));
      timers.set(app, window.setTimeout(function () {
        app.classList.remove("is-tipped");
      }, cssTime("--t-tooltip", 1600)));
    }
  });

  apps.addEventListener("animationend", function (event) {
    if (event.animationName === "app-shake") {
      event.target.closest(".app").classList.remove("is-shaking");
    }
  });
})();
