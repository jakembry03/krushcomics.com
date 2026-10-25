/*
 * The FrostOS clock: fills every [data-clock="time"] and
 * [data-clock="date"] element with the visitor's local time and date,
 * updating each minute. window.cocoClock.stop() freezes it.
 */
(function () {
  "use strict";

  var timeEls = document.querySelectorAll('[data-clock="time"]');
  var dateEls = document.querySelectorAll('[data-clock="date"]');
  var timer = null;

  if (!timeEls.length && !dateEls.length) {
    return;
  }

  function render() {
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

  function tick() {
    render();
    // Tick again just after the next minute starts.
    timer = window.setTimeout(tick, 60000 - (Date.now() % 60000) + 50);
  }

  function stop() {
    window.clearTimeout(timer);
    timer = null;
  }

  tick();

  window.cocoClock = { stop: stop };
})();
