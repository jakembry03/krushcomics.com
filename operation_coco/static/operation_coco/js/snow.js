/*
 * Falling snow on the full-screen canvas behind every page.
 *
 * - 60 to 120 flakes of mixed size and speed with a gentle sideways drift.
 * - Pauses while the tab is hidden.
 * - With reduced motion, a few slow flakes instead.
 * - window.cocoSnow.freeze(ms) eases the snow to a stop in mid-air and
 *   keeps it there. Returns a Promise that resolves once it has stopped.
 */
(function () {
  "use strict";

  var canvas = document.getElementById("snow-canvas");
  if (!canvas || !canvas.getContext) {
    return;
  }

  var ctx = canvas.getContext("2d");
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  var flakes = [];
  var width = 0;
  var height = 0;
  var color = "";
  var rafId = null;
  var lastTime = null;
  var clock = 0;

  // 1 is normal speed, 0 is stopped. freeze() eases this down to 0.
  var speed = 1;
  var frozen = false;
  var freezeStart = null;
  var freezeDuration = 0;
  var freezeDone = null;

  function readColor() {
    var value = getComputedStyle(document.documentElement).getPropertyValue("--frost-white");
    color = value.trim() || "white";
  }

  function targetCount() {
    if (reducedMotion.matches) {
      return 14;
    }
    // Scale with screen area, kept between 60 and 120.
    return Math.round(Math.min(120, Math.max(60, (width * height) / 11000)));
  }

  function makeFlake(anywhere) {
    var radius = 1 + Math.pow(Math.random(), 2) * 3;
    var calm = reducedMotion.matches;
    return {
      x: Math.random() * width,
      y: anywhere ? Math.random() * height : -radius * 2,
      r: radius,
      // Bigger flakes are closer, so they fall faster. Pixels per second.
      fall: calm ? 8 + radius * 3 : 18 + radius * 16 + Math.random() * 10,
      drift: calm ? 4 : 8 + Math.random() * 14,
      sway: 0.3 + Math.random() * 0.7,
      phase: Math.random() * Math.PI * 2,
      alpha: 0.45 + Math.random() * 0.5
    };
  }

  function rebuild() {
    var count = targetCount();
    flakes = [];
    for (var i = 0; i < count; i++) {
      flakes.push(makeFlake(true));
    }
  }

  function resize() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var oldWidth = width;
    var oldHeight = height;
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    if (!flakes.length) {
      rebuild();
    } else if (oldWidth && oldHeight) {
      // Keep the same flakes (important once frozen), just rescaled.
      flakes.forEach(function (flake) {
        flake.x = (flake.x / oldWidth) * width;
        flake.y = (flake.y / oldHeight) * height;
      });
    }
    draw();
  }

  function update(dt) {
    clock += dt * speed;
    for (var i = 0; i < flakes.length; i++) {
      var flake = flakes[i];
      flake.y += flake.fall * dt * speed;
      flake.x += Math.sin(clock * flake.sway + flake.phase) * flake.drift * dt * speed;

      if (flake.y > height + flake.r * 2) {
        flakes[i] = makeFlake(false);
      } else if (flake.x > width + 10) {
        flake.x = -10;
      } else if (flake.x < -10) {
        flake.x = width + 10;
      }
    }
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = color;
    for (var i = 0; i < flakes.length; i++) {
      var flake = flakes[i];
      ctx.globalAlpha = flake.alpha;
      ctx.beginPath();
      ctx.arc(flake.x, flake.y, flake.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function frame(now) {
    rafId = null;
    var dt = lastTime === null ? 0 : Math.min((now - lastTime) / 1000, 0.1);
    lastTime = now;

    if (freezeStart !== null) {
      var progress = freezeDuration > 0 ? (now - freezeStart) / freezeDuration : 1;
      if (progress >= 1) {
        speed = 0;
        frozen = true;
        freezeStart = null;
      } else {
        // Ease out: quick at first, settling gently into stillness.
        speed = Math.pow(1 - progress, 2);
      }
    }

    update(dt);
    draw();

    if (frozen) {
      if (freezeDone) {
        freezeDone();
        freezeDone = null;
      }
      return;
    }
    start();
  }

  function start() {
    if (rafId === null && !frozen && !document.hidden) {
      rafId = requestAnimationFrame(frame);
    }
  }

  function stop() {
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    lastTime = null;
  }

  function freeze(duration) {
    if (frozen) {
      return Promise.resolve();
    }
    return new Promise(function (resolve) {
      freezeDuration = reducedMotion.matches ? 0 : Math.max(0, duration || 0);
      freezeStart = performance.now();
      freezeDone = resolve;
      if (document.hidden || rafId === null) {
        // Not animating right now, so stop on the spot.
        speed = 0;
        frozen = true;
        freezeStart = null;
        stop();
        draw();
        freezeDone = null;
        resolve();
      }
    });
  }

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) {
      stop();
    } else {
      start();
    }
  });

  window.addEventListener("resize", resize);

  reducedMotion.addEventListener("change", function () {
    if (!frozen) {
      rebuild();
    }
  });

  readColor();
  resize();
  start();

  window.cocoSnow = {
    freeze: freeze,
    isFrozen: function () {
      return frozen;
    }
  };
})();
