/*
 * Character sprite helpers for partials/agent.html (and the villain).
 *
 * window.cocoSprite.setPose(el, "worried") shows one pose, if the sprite
 * has it. window.cocoSprite.setMouthOpen(el, true) animates talking in
 * the current pose (the agent's visor flickers; the villain's mouth opens).
 */
(function () {
  "use strict";

  function setPose(el, pose) {
    if (!el || !pose || !el.querySelector(".sprite__pose--" + pose)) {
      return;
    }
    Array.prototype.slice.call(el.classList).forEach(function (name) {
      if (name.indexOf("pose-") === 0) {
        el.classList.remove(name);
      }
    });
    el.classList.add("pose-" + pose);
  }

  function setMouthOpen(el, open) {
    if (el) {
      el.classList.toggle("is-mouth-open", Boolean(open));
    }
  }

  window.cocoSprite = {
    setPose: setPose,
    setMouthOpen: setMouthOpen
  };
})();
