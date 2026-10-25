/*
 * Agent sprite helpers for partials/agent.html.
 *
 * window.cocoAgent.setPose(el, "worried") shows one pose.
 * window.cocoAgent.setMouthOpen(el, true) opens the mouth in the current
 * pose, used to animate talking without swapping arms or eyes.
 */
(function () {
  "use strict";

  var POSES = ["idle", "talk", "point", "happy", "worried"];

  function setPose(el, pose) {
    if (!el || POSES.indexOf(pose) === -1) {
      return;
    }
    POSES.forEach(function (name) {
      el.classList.toggle("agent--" + name, name === pose);
    });
  }

  function setMouthOpen(el, open) {
    if (el) {
      el.classList.toggle("is-mouth-open", Boolean(open));
    }
  }

  window.cocoAgent = {
    poses: POSES.slice(),
    setPose: setPose,
    setMouthOpen: setMouthOpen
  };
})();
