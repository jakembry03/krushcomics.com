/*
 * The FrostOS lock screen.
 *
 * Privacy: whatever Coco types into the password field is never read,
 * sent, logged, or stored. The submit is stopped and the field cleared.
 */
(function () {
  "use strict";

  var form = document.getElementById("password-form");
  var input = document.getElementById("password-input");

  /* ---------- Clock ---------- */

  var timeEls = document.querySelectorAll('[data-clock="time"]');
  var dateEls = document.querySelectorAll('[data-clock="date"]');
  var clockTimer = null;

  function renderClock() {
    var now = new Date();
    var time = now.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    var date = now.toLocaleDateString([], { weekday: "long", month: "long", day: "numeric" });
    timeEls.forEach(function (el) {
      el.textContent = time;
    });
    dateEls.forEach(function (el) {
      el.textContent = date;
    });
  }

  function startClock() {
    renderClock();
    // Tick again just after the next minute starts.
    clockTimer = window.setTimeout(startClock, 60000 - (Date.now() % 60000) + 50);
  }

  /* ---------- Password form ---------- */

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    input.value = "";
  });

  // On phones, keep the field in view once the keyboard has opened.
  input.addEventListener("focus", function () {
    window.setTimeout(function () {
      input.scrollIntoView({ block: "center", behavior: "smooth" });
    }, 300);
  });

  startClock();
})();
