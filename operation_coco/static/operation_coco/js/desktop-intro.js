/*
 * The desktop intro: the villain's grand entrance, then Agent Orange's
 * rundown and the first thaw.
 *
 * Villain: calm, warning (wind and flickering frost), flyby, return to
 * hover at the top, gloat (dialogue), then exit as his snow settles over
 * the icons. Agent: the rift opens at the lower right, he hops out,
 * talks, and on the "thaw" cue casts a warm beam that cracks and melts
 * the ice on the first app. When the thaw finishes the page tells the
 * server, so a reload shows the calm desktop with that app thawed.
 *
 * Each step is a function returning a Promise; durations come from the
 * --t-* tokens in coco.css. Flight paths use the Web Animations API
 * because they depend on the screen size.
 */
(function () {
  "use strict";

  var intro = document.getElementById("intro");
  if (!intro) {
    return;
  }

  var ride = document.getElementById("villain-ride");
  var villain = document.getElementById("villain");
  var trail = document.getElementById("intro-trail");
  var beam = document.getElementById("intro-beam");
  var beamPath = document.getElementById("intro-beam-path");
  var vignette = document.getElementById("frost-vignette");
  var meter = document.getElementById("heart-meter");
  var topbar = document.querySelector(".topbar");
  var riftZone = document.getElementById("rift-zone");
  var rift = document.getElementById("rift");
  var agent = riftZone.querySelector(".agent");
  var target = document.querySelector('.app[data-stage="' + intro.dataset.stage + '"]');
  var appsList = document.getElementById("desktop-apps");
  var apps = appsList.querySelectorAll(".app");
  var scenes = JSON.parse(document.getElementById("dialogue-data").textContent);
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var trailTimer = null;

  /* ---------- Helpers ---------- */

  function calm() {
    return reducedMotion.matches;
  }

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

  function setPose(el, pose) {
    if (window.cocoSprite) {
      window.cocoSprite.setPose(el, pose);
    }
  }

  function restartClass(el, className) {
    el.classList.remove(className);
    void el.offsetWidth;
    el.classList.add(className);
  }

  function dialogueEnded() {
    return new Promise(function (resolve) {
      document.addEventListener("dialogue:end", resolve, { once: true });
    });
  }

  /* ---------- The villain's flight ---------- */

  function geometry() {
    var width = window.innerWidth;
    var rideWidth = ride.offsetWidth;
    var rideHeight = ride.offsetHeight;
    var barBottom = topbar ? topbar.getBoundingClientRect().bottom : 0;
    // He sticks up out of the car (more so standing), so leave headroom.
    var top = barBottom + rideWidth * 0.48;
    if (width <= 640) {
      // On phones the icons sit across the top, so hover below them.
      top = Math.max(top, appsList.getBoundingClientRect().bottom + rideWidth * 0.5);
    }
    return {
      width: width,
      w: rideWidth,
      h: rideHeight,
      top: top,
      center: (width - rideWidth) / 2
    };
  }

  function at(x, y, turn) {
    return { transform: "translate(" + x + "px, " + y + "px) rotate(" + (turn || 0) + "deg)" };
  }

  function fly(frames, duration, easing) {
    return ride.animate(frames, { duration: duration, easing: easing, fill: "forwards" }).finished;
  }

  function face(direction) {
    ride.style.setProperty("--face", direction);
    ride.dataset.face = direction;
  }

  // Snow exhaust puffing out behind the car, with the odd frosty sparkle.
  function puff() {
    var box = ride.getBoundingClientRect();
    var behind = ride.dataset.face === "-1" ? box.right - box.width * 0.04 : box.left + box.width * 0.04;
    var bit = document.createElement("span");
    bit.className = Math.random() < 0.25 ? "puff puff--sparkle" : "puff";
    bit.style.left = behind + "px";
    bit.style.top = box.top + box.height * (0.45 + Math.random() * 0.2) + "px";
    bit.style.setProperty("--drift", (Math.random() * 40 - 20).toFixed(0) + "px");
    bit.addEventListener("animationend", function () {
      bit.remove();
    });
    trail.appendChild(bit);
  }

  function startTrail() {
    if (!calm() && trailTimer === null) {
      trailTimer = window.setInterval(puff, 60);
    }
  }

  function stopTrail() {
    window.clearInterval(trailTimer);
    trailTimer = null;
  }

  /* ---------- Villain scene ---------- */

  // 1. Calm: the desktop as it is, gentle snow.
  function calmMoment() {
    return wait(cssTime("--t-calm", 1500));
  }

  // 2. Warning: wind picks up, frost flickers at the edges, the meter shivers.
  function warning() {
    if (calm()) {
      return Promise.resolve();
    }
    if (window.cocoSnow) {
      window.cocoSnow.setWind(260);
    }
    vignette.classList.add("is-flickering");
    if (meter) {
      meter.classList.add("is-shivering");
    }
    return wait(cssTime("--t-warning", 1000));
  }

  // 3. Flyby: he streaks across the top, frost swooshing over the icons.
  function flyby() {
    if (calm()) {
      return Promise.resolve();
    }
    var g = geometry();
    var duration = cssTime("--t-flyby", 1500);
    ride.classList.add("is-flying");
    face(1);
    startTrail();
    window.setTimeout(function () {
      apps.forEach(function (app) {
        restartClass(app, "is-swooshed");
      });
    }, duration * 0.2);
    return fly([
      at(-g.w - 80, g.top + 24, 4),
      Object.assign(at(g.center, g.top - 8, -3), { offset: 0.5 }),
      at(g.width + 80, g.top + 12, 3)
    ], duration, "ease-in-out");
  }

  // 4. Return: he loops back in from the right, swerves, and brakes to a hover.
  function comeBack() {
    var g = geometry();
    if (calm()) {
      ride.classList.add("is-flying");
      ride.animate([at(g.center, g.top), at(g.center, g.top)], { duration: 1, fill: "forwards" });
      return ride.animate([{ opacity: 0 }, { opacity: 1 }], {
        duration: cssTime("--t-reduced-fade", 300), fill: "forwards"
      }).finished;
    }
    face(-1);
    return fly([
      at(g.width + 80, g.top + 48, 0),
      Object.assign(at(g.width * 0.62 - g.w / 2, g.top + 64, 10), { offset: 0.45 }),
      Object.assign(at(g.center - 36, g.top - 8, -9), { offset: 0.8 }),
      at(g.center, g.top, 0)
    ], cssTime("--t-return", 1000), "ease-out").then(function () {
      stopTrail();
      if (window.cocoSnow) {
        window.cocoSnow.setWind(0);
      }
      vignette.classList.remove("is-flickering");
      if (meter) {
        meter.classList.remove("is-shivering");
      }
      ride.classList.add("is-hovering");
      // Turn to face right, toward the heart meter.
      face(1);
    });
  }

  // 5. Gloat: he stands up in the car and talks.
  function gloat() {
    ride.classList.add("is-standing");
    setPose(villain, "cackle");
    var ended = dialogueEnded();
    window.cocoDialogue.start(scenes.villain, { actors: { villain: villain } });
    return ended;
  }

  // 6. Exit: he guns it off the top-right; his snow settles over the icons.
  function exit() {
    var g = geometry();
    ride.classList.remove("is-standing", "is-hovering");
    var done;
    if (calm()) {
      done = ride.animate([{ opacity: 1 }, { opacity: 0 }], {
        duration: cssTime("--t-reduced-fade", 300), fill: "forwards"
      }).finished;
    } else {
      face(1);
      startTrail();
      done = fly([
        at(g.center, g.top, 0),
        Object.assign(at(g.center + 30, g.top + 18, 8), { offset: 0.2 }),
        at(g.width + g.w, -g.h - 120, -18)
      ], cssTime("--t-exit", 1200), "cubic-bezier(0.5, 0, 0.9, 0.4)");
    }
    return done.then(function () {
      stopTrail();
      ride.classList.remove("is-flying");
      apps.forEach(function (app) {
        if (app.classList.contains("is-frozen")) {
          app.classList.add("is-thick");
        }
      });
      return wait(cssTime("--t-settle", 900));
    });
  }

  /* ---------- Agent Orange ---------- */

  // 1. The rift tears open at the lower right.
  function openRift() {
    riftZone.removeAttribute("aria-hidden");
    if (calm()) {
      rift.classList.add("is-open", "is-settled");
      agent.classList.add("is-here");
      setPose(agent, "idle");
      return wait(cssTime("--t-reduced-fade", 300));
    }
    rift.classList.add("is-open", "is-opening");
    return wait(cssTime("--t-rift-desktop", 1000));
  }

  // 2. He hops out worried and settles into idle.
  function arrive() {
    if (calm()) {
      return Promise.resolve();
    }
    rift.classList.remove("is-opening");
    rift.classList.add("is-settled");
    setPose(agent, "worried");
    agent.classList.add("is-arriving");
    return wait(cssTime("--t-arrive", 800)).then(function () {
      agent.classList.remove("is-arriving");
      agent.classList.add("is-here");
      setPose(agent, "idle");
    });
  }

  // 3. The rundown. The "thaw" cue thaws the first app.
  function rundown() {
    var ended = dialogueEnded();
    window.cocoDialogue.start(scenes.agent, { actors: { agent: agent } });
    return ended;
  }

  // 5. Afterwards he waits by the portal, now and then glancing at the app.
  function standBy() {
    window.setInterval(function () {
      if (!window.cocoDialogue.isOpen()) {
        setPose(agent, "point");
        window.setTimeout(function () {
          setPose(agent, "idle");
        }, cssTime("--t-glance", 1500));
      }
    }, cssTime("--t-glance-every", 7000));
  }

  /* ---------- The thaw ---------- */

  function fireBeam() {
    var hand = agent.getBoundingClientRect();
    var tile = target.querySelector(".app__tile").getBoundingClientRect();
    // The cast pose's raised hand sits at about (13%, 32%) of the sprite.
    var hx = hand.left + hand.width * 0.13;
    var hy = hand.top + hand.height * 0.32;
    var ix = tile.left + tile.width / 2;
    var iy = tile.top + tile.height / 2;
    var cx = (hx + ix) / 2;
    var cy = Math.min(hy, iy) - Math.max(80, Math.abs(hx - ix) * 0.25);
    beamPath.setAttribute("d", "M" + hx + " " + hy + "Q" + cx + " " + cy + " " + ix + " " + iy);
    restartClass(beam, "is-firing");
  }

  function drips() {
    var tile = target.querySelector(".app__tile");
    for (var i = 0; i < 4; i++) {
      var drop = document.createElement("span");
      drop.className = "drip";
      drop.style.left = 18 + i * 20 + Math.random() * 8 + "%";
      drop.style.animationDelay = i * 90 + "ms";
      drop.addEventListener("animationend", function (event) {
        event.target.remove();
      });
      tile.appendChild(drop);
    }
  }

  function makeLink(app) {
    var button = app.querySelector(".app__button");
    var tooltip = app.querySelector(".app__tooltip");
    var link = document.createElement("a");
    link.className = "app__button";
    link.href = app.dataset.url;
    link.setAttribute("data-app-link", "");
    link.setAttribute("data-frost-transition", "");
    while (button.firstChild) {
      link.appendChild(button.firstChild);
    }
    button.replaceWith(link);
    if (tooltip) {
      tooltip.remove();
    }
  }

  function tellServer() {
    var token = intro.querySelector("input[name=csrfmiddlewaretoken]");
    return fetch(intro.dataset.doneUrl, {
      method: "POST",
      headers: { "X-CSRFToken": token ? token.value : "" },
      credentials: "same-origin"
    }).catch(function () {
      // If this fails she just sees the intro again next time.
    });
  }

  function thaw() {
    restartClass(agent, "is-flaring");
    var steps;
    if (calm()) {
      target.classList.add("is-melting");
      steps = wait(cssTime("--t-reduced-fade", 300));
    } else {
      fireBeam();
      steps = wait(cssTime("--t-beam", 500)).then(function () {
        target.classList.add("is-cracking");
        return wait(cssTime("--t-crack-web", 700));
      }).then(function () {
        target.classList.add("is-melting");
        drips();
        return wait(cssTime("--t-melt", 800));
      });
    }
    return steps.then(function () {
      target.classList.remove("is-frozen", "is-thick", "is-cracking", "is-melting", "is-shaking", "is-tipped");
      target.classList.add("is-thawed", "is-just-thawed");
      makeLink(target);
      beam.classList.remove("is-firing");
      return tellServer();
    });
  }

  document.addEventListener("dialogue:cue", function (event) {
    if (event.detail.cue === "thaw") {
      thaw();
    } else if (event.detail.cue === "villain_exit") {
      setPose(villain, "cackle");
    }
  });

  /* ---------- Run it ---------- */

  var sequence = [
    calmMoment, warning, flyby, comeBack, gloat, exit,
    openRift, arrive, rundown, standBy
  ];

  sequence.reduce(function (previous, step) {
    return previous.then(step);
  }, Promise.resolve());
})();
