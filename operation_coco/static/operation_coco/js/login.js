/*
 * The FrostOS lock screen and the failed-login sequence.
 *
 * Privacy: whatever Coco types into the password field is never read,
 * sent, logged, or stored. The submit is stopped and the field cleared.
 *
 * Any submit, even an empty one, fails and starts the sequence once:
 * verifying, denied, the freeze, the rift opens, the agent arrives, and
 * the dialogue begins. Each step is a function returning a Promise, and
 * their durations come from the --t-* tokens in coco.css.
 */
(function () {
  "use strict";

  var form = document.getElementById("password-form");
  var input = document.getElementById("password-input");
  var submitButton = document.getElementById("password-submit");
  var hint = document.getElementById("login-hint");
  var hintText = document.getElementById("login-hint-text");
  var spinner = document.getElementById("login-spinner");
  var card = document.getElementById("login-card");
  var clock = document.getElementById("clock");
  var vignette = document.getElementById("frost-vignette");
  var riftZone = document.getElementById("rift-zone");
  var rift = document.getElementById("rift");
  var agent = riftZone.querySelector(".agent");
  var dialogueData = document.getElementById("dialogue-data");
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* ---------- Helpers ---------- */

  function cssTime(name, fallback) {
    var value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    var number = parseFloat(value);
    if (isNaN(number)) {
      return fallback;
    }
    return /ms$/.test(value) ? number : number * 1000;
  }

  function wait(ms) {
    return new Promise(function (resolve) {
      window.setTimeout(resolve, ms);
    });
  }

  function setPose(pose) {
    if (window.cocoSprite) {
      window.cocoSprite.setPose(agent, pose);
    }
  }

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

  function stopClock() {
    window.clearTimeout(clockTimer);
    clockTimer = null;
  }

  /* ---------- The failed-login sequence ---------- */

  // 1. Verifying: lock the form and show a spinner.
  function verify() {
    input.blur();
    input.disabled = true;
    submitButton.disabled = true;
    spinner.hidden = false;
    hintText.textContent = "Verifying…";
    return wait(cssTime("--t-verify", 800));
  }

  // 2. Denied: shake the card and show the error.
  function deny() {
    spinner.hidden = true;
    hint.classList.add("is-error");
    hintText.textContent = "Incorrect password.";
    input.value = "";
    if (!reducedMotion.matches) {
      card.classList.add("is-shaking");
    }
    return wait(cssTime("--t-denied", 1000));
  }

  // 3. The freeze: snow stops in mid-air, frost creeps in, the clock stops.
  function freeze() {
    var duration = cssTime("--t-freeze", 1000);
    var calm = reducedMotion.matches;
    card.classList.remove("is-shaking");
    stopClock();
    clock.classList.add("is-frozen");
    if (!calm) {
      vignette.classList.add("is-active");
    }
    var snow = window.cocoSnow ? window.cocoSnow.freeze(calm ? 0 : duration) : Promise.resolve();
    return calm ? snow : Promise.all([snow, wait(duration)]);
  }

  // 4. The rift tears open from a bright point.
  function openRift() {
    riftZone.removeAttribute("aria-hidden");
    if (reducedMotion.matches) {
      // Rift and agent fade in together.
      rift.classList.add("is-open", "is-settled");
      agent.classList.add("is-here");
      setPose("idle");
      card.classList.add("is-frozen");
      return wait(cssTime("--t-reduced-fade", 300));
    }
    rift.classList.add("is-open", "is-opening");
    return wait(cssTime("--t-rift", 1200));
  }

  // 5. The agent hops out worried, lands, and settles; the rift shrinks.
  function arrive() {
    if (reducedMotion.matches) {
      return Promise.resolve();
    }
    rift.classList.remove("is-opening");
    rift.classList.add("is-settled");
    setPose("worried");
    agent.classList.add("is-arriving");
    card.classList.add("is-frozen");
    return wait(cssTime("--t-arrive", 800)).then(function () {
      agent.classList.remove("is-arriving");
      agent.classList.add("is-here");
      setPose("idle");
    });
  }

  // 6. The dialogue box slides up and the first line starts typing.
  function startDialogue() {
    card.inert = true;
    document.body.classList.add("is-talking");
    if (window.cocoDialogue && dialogueData) {
      window.cocoDialogue.start(JSON.parse(dialogueData.textContent), { agent: agent });
    }
  }

  var sequence = [verify, deny, freeze, openRift, arrive, startDialogue];
  var started = false;

  function runSequence() {
    sequence.reduce(function (previous, step) {
      return previous.then(step);
    }, Promise.resolve());
  }

  /* ---------- Password form ---------- */

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    input.value = "";
    if (!started) {
      started = true;
      runSequence();
    }
  });

  // On phones, keep the field in view once the keyboard has opened.
  input.addEventListener("focus", function () {
    window.setTimeout(function () {
      input.scrollIntoView({ block: "center", behavior: reducedMotion.matches ? "auto" : "smooth" });
    }, 300);
  });

  startClock();
})();
