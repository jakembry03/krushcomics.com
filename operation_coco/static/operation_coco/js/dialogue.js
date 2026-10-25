/*
 * The reusable dialogue box (partials/dialogue_box.html).
 *
 * window.cocoDialogue.start(script, { agent: element }) opens the box and
 * plays the script: { speaker, lines: [{ pose, text, button? }] }.
 *
 * - Lines type out at --dialogue-cps characters per second, with the
 *   agent's mouth flapping in the line's pose while it types.
 * - Click, tap, Enter, or Space shows the whole line, or moves on once it
 *   is finished.
 * - A line with a button ({ label, url }) shows it when finished.
 * - Each line is announced through an aria-live region.
 * - With reduced motion, lines appear in full.
 */
(function () {
  "use strict";

  var root = document.getElementById("dialogue");
  if (!root) {
    return;
  }

  var panel = document.getElementById("dialogue-panel");
  var speakerEl = document.getElementById("dialogue-speaker");
  var ghostEl = document.getElementById("dialogue-ghost");
  var typedEl = document.getElementById("dialogue-typed");
  var liveEl = document.getElementById("dialogue-live");
  var nextEl = document.getElementById("dialogue-next");
  var actionsEl = document.getElementById("dialogue-actions");
  var actionEl = document.getElementById("dialogue-action");
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  var script = null;
  var agent = null;
  var index = -1;
  var typing = false;
  var typeStart = 0;
  var rafId = null;
  var mouthTimer = null;

  function cssNumber(name, fallback) {
    var value = parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
    return isNaN(value) ? fallback : value;
  }

  function currentLine() {
    return script.lines[index];
  }

  /* ---------- Agent ---------- */

  function setPose(pose) {
    if (agent && pose && window.cocoSprite) {
      window.cocoSprite.setPose(agent, pose);
    }
  }

  function startMouth() {
    if (!agent || !window.cocoSprite) {
      return;
    }
    var open = false;
    mouthTimer = window.setInterval(function () {
      open = !open;
      window.cocoSprite.setMouthOpen(agent, open);
    }, cssNumber("--t-mouth", 160));
  }

  function stopMouth() {
    window.clearInterval(mouthTimer);
    mouthTimer = null;
    if (agent && window.cocoSprite) {
      window.cocoSprite.setMouthOpen(agent, false);
    }
  }

  /* ---------- Lines ---------- */

  function showLine(i) {
    index = i;
    var line = currentLine();

    setPose(line.pose);
    ghostEl.textContent = line.text;
    typedEl.textContent = "";
    liveEl.textContent = line.text;
    nextEl.hidden = true;
    actionsEl.hidden = true;

    if (reducedMotion.matches) {
      finishLine();
      return;
    }

    typing = true;
    typeStart = performance.now();
    startMouth();
    rafId = requestAnimationFrame(type);
  }

  function type(now) {
    var text = currentLine().text;
    var count = Math.floor(((now - typeStart) / 1000) * cssNumber("--dialogue-cps", 35));
    if (count >= text.length) {
      finishLine();
      return;
    }
    typedEl.textContent = text.slice(0, count);
    rafId = requestAnimationFrame(type);
  }

  function finishLine() {
    var line = currentLine();
    cancelAnimationFrame(rafId);
    rafId = null;
    typing = false;
    stopMouth();
    typedEl.textContent = line.text;

    if (line.button) {
      actionEl.textContent = line.button.label;
      actionEl.href = line.button.url;
      actionsEl.hidden = false;
      actionEl.focus({ preventScroll: true });
    } else if (index < script.lines.length - 1) {
      nextEl.hidden = false;
    }
  }

  function advance() {
    if (!script) {
      return;
    }
    if (typing) {
      finishLine();
    } else if (index < script.lines.length - 1 && !currentLine().button) {
      showLine(index + 1);
    }
  }

  /* ---------- Opening ---------- */

  function start(data, options) {
    if (!data || !data.lines || !data.lines.length) {
      return;
    }
    script = data;
    agent = (options && options.agent) || null;
    speakerEl.textContent = data.speaker || "";

    root.hidden = false;
    // Let the hidden -> shown change paint before sliding up.
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        root.classList.add("is-open");
      });
    });
    panel.focus({ preventScroll: true });
    showLine(0);
  }

  /* ---------- Input ---------- */

  panel.addEventListener("click", function (event) {
    if (!actionEl.contains(event.target)) {
      advance();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (!script || root.hidden || event.repeat) {
      return;
    }
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }
    if (event.target === actionEl) {
      // Enter follows the link natively; make Space do the same.
      if (event.key === " ") {
        event.preventDefault();
        actionEl.click();
      }
      return;
    }
    if (event.target.closest && event.target.closest("input, textarea, select, button, a")) {
      return;
    }
    event.preventDefault();
    advance();
  });

  window.cocoDialogue = {
    start: start,
    advance: advance
  };

  if (root.hasAttribute("data-autostart")) {
    var dataEl = document.getElementById("dialogue-data");
    if (dataEl) {
      start(JSON.parse(dataEl.textContent), { agent: document.querySelector(".agent") });
    }
  }
})();
