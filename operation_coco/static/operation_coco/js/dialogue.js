/*
 * The reusable dialogue box (partials/dialogue_box.html).
 *
 * window.cocoDialogue.start(script, { actors: { agent: el, villain: el } })
 * opens the box and plays a script prepared by dialogue.prepare():
 *   { speakers: { agent: { name }, ... },
 *     lines: [{ speaker, pose, text, cue?, button? }] }
 *
 * - Each line shows its speaker's name tag and sets that speaker's pose.
 * - Lines type out at --dialogue-cps characters per second while the
 *   speaker's sprite talks.
 * - Click, tap, Enter, or Space shows the whole line, or moves on once it
 *   is finished.
 * - A line with a cue fires a "dialogue:cue" event on document when it
 *   starts (detail: { cue, index, line }); the page script handles it.
 * - A line with a button ({ label, url }) shows it when finished.
 * - Moving on from a last line without a button closes the box and fires
 *   "dialogue:end".
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
  var actors = {};
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

  function emit(name, detail) {
    document.dispatchEvent(new CustomEvent(name, { detail: detail }));
  }

  /* ---------- Speakers ---------- */

  function actorFor(line) {
    return actors[line.speaker] || null;
  }

  function showSpeaker(line) {
    var speaker = (script.speakers && script.speakers[line.speaker]) || {};
    speakerEl.textContent = speaker.name || "";
    speakerEl.hidden = !speaker.name;
    speakerEl.className = "dialogue__name dialogue__name--" + line.speaker;
  }

  function startMouth(actor) {
    if (!actor || !window.cocoSprite) {
      return;
    }
    var open = false;
    mouthTimer = window.setInterval(function () {
      open = !open;
      window.cocoSprite.setMouthOpen(actor, open);
    }, cssNumber("--t-mouth", 160));
  }

  function stopMouth() {
    window.clearInterval(mouthTimer);
    mouthTimer = null;
    if (window.cocoSprite) {
      Object.keys(actors).forEach(function (name) {
        window.cocoSprite.setMouthOpen(actors[name], false);
      });
    }
  }

  /* ---------- Lines ---------- */

  function showLine(i) {
    index = i;
    var line = currentLine();
    var actor = actorFor(line);

    showSpeaker(line);
    if (actor && line.pose && window.cocoSprite) {
      window.cocoSprite.setPose(actor, line.pose);
    }
    ghostEl.textContent = line.text;
    typedEl.textContent = "";
    liveEl.textContent = line.text;
    nextEl.hidden = true;
    actionsEl.hidden = true;

    if (line.cue) {
      emit("dialogue:cue", { cue: line.cue, index: i, line: line });
    }

    if (reducedMotion.matches) {
      finishLine();
      return;
    }

    typing = true;
    typeStart = performance.now();
    startMouth(actor);
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
    } else {
      // Also shown on the last line: one more tap closes the box.
      nextEl.hidden = false;
    }
  }

  function advance() {
    if (!script) {
      return;
    }
    if (typing) {
      finishLine();
    } else if (currentLine().button) {
      return;
    } else if (index < script.lines.length - 1) {
      showLine(index + 1);
    } else {
      close();
      emit("dialogue:end", {});
    }
  }

  /* ---------- Opening and closing ---------- */

  function start(data, options) {
    if (!data || !data.lines || !data.lines.length) {
      return;
    }
    options = options || {};
    stopMouth();
    cancelAnimationFrame(rafId);

    script = data;
    actors = options.actors || {};
    if (options.agent && !actors.agent) {
      actors.agent = options.agent;
    }

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

  function close() {
    cancelAnimationFrame(rafId);
    rafId = null;
    typing = false;
    stopMouth();
    script = null;
    root.classList.remove("is-open");
    if (root.contains(document.activeElement)) {
      document.activeElement.blur();
    }
    window.setTimeout(function () {
      if (!script) {
        root.hidden = true;
      }
    }, cssNumber("--t-dialogue-in", 450));
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
    advance: advance,
    close: close,
    isOpen: function () {
      return Boolean(script);
    }
  };

  if (root.hasAttribute("data-autostart")) {
    var dataEl = document.getElementById("dialogue-data");
    if (dataEl) {
      start(JSON.parse(dataEl.textContent), { actors: { agent: document.querySelector(".agent") } });
    }
  }
})();
