/*
 * The Account Locked screen.
 *
 * Answers and hint requests post to the server with fetch, which replies
 * with JSON, so the page can animate without reloading. The server
 * decides everything: whether an answer is right, which question is
 * current, and which hints she may see.
 */
(function () {
  "use strict";

  var form = document.getElementById("unlock-form");
  if (!form) {
    return;
  }

  var card = document.getElementById("unlock-card");
  var lockedView = document.getElementById("unlock-locked");
  var verifiedView = document.getElementById("unlock-verified");
  var check = document.getElementById("unlock-check");
  var dots = document.querySelectorAll("#qdots .qdot");
  var questionBox = document.getElementById("unlock-question");
  var questionOrder = document.getElementById("unlock-question-order");
  var prompt = document.getElementById("unlock-prompt");
  var input = document.getElementById("unlock-answer");
  var submit = document.getElementById("unlock-submit");
  var message = document.getElementById("unlock-message");
  var hintToggle = document.getElementById("unlock-hint-toggle");
  var hintList = document.getElementById("unlock-hints");
  var helper = document.getElementById("helper");
  var helperBubble = document.getElementById("helper-bubble");
  var dialogueData = document.getElementById("dialogue-data");
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var busy = false;
  var helperTimer = null;

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

  function restartAnimation(el, className) {
    el.classList.remove(className);
    void el.offsetWidth;
    el.classList.add(className);
  }

  /* ---------- Talking to the server ---------- */

  function send(action) {
    var data = new FormData(form);
    data.set("action", action);
    // Not form.action: the buttons named "action" shadow that property.
    return fetch(form.getAttribute("action"), {
      method: "POST",
      body: data,
      headers: { Accept: "application/json" },
      credentials: "same-origin"
    }).then(function (response) {
      if (!response.ok) {
        throw new Error("Unexpected response");
      }
      return response.json();
    });
  }

  function setBusy(isBusy) {
    busy = isBusy;
    submit.disabled = isBusy;
    hintToggle.disabled = isBusy;
    submit.textContent = isBusy ? "Checking…" : "Submit";
  }

  /* ---------- Showing results ---------- */

  function showMessage(text, isError) {
    message.textContent = text;
    message.classList.toggle("is-error", Boolean(isError));
  }

  function showHints(state) {
    hintList.innerHTML = "";
    (state.hints || []).forEach(function (hint) {
      var item = document.createElement("li");
      item.textContent = hint;
      hintList.appendChild(item);
    });
    hintList.hidden = !(state.hints && state.hints.length);
    hintToggle.hidden = !state.hint_available;
  }

  function markDots(solved) {
    dots.forEach(function (dot, i) {
      var wasDone = dot.classList.contains("qdot--done");
      dot.classList.toggle("qdot--done", i < solved);
      dot.classList.toggle("qdot--current", i === solved);
      dot.classList.toggle("qdot--todo", i > solved);
      if (i < solved && !wasDone) {
        dot.classList.add("is-cracking");
      }
      var label = dot.querySelector(".visually-hidden");
      if (label) {
        label.textContent = i < solved ? "Answered" : i === solved ? "Current question" : "Not yet";
      }
    });
  }

  function popCheck() {
    restartAnimation(check, "is-visible");
    return wait(cssTime("--t-check", 900)).then(function () {
      check.classList.remove("is-visible");
    });
  }

  function wrong(state) {
    if (!reducedMotion.matches) {
      restartAnimation(card, "is-shaking");
    }
    showMessage("That answer doesn't match our records.", true);
    showHints(state);
    input.focus();
  }

  function nextQuestion(state) {
    markDots(state.solved);
    showMessage("", false);
    hideHelper();
    return popCheck().then(function () {
      questionBox.classList.add("is-leaving");
      return wait(reducedMotion.matches ? 0 : cssTime("--t-base", 300));
    }).then(function () {
      questionOrder.value = state.question.order;
      prompt.textContent = state.question.prompt;
      input.value = "";
      showHints(state);
      questionBox.classList.remove("is-leaving");
      restartAnimation(questionBox, "is-entering");
      input.focus();
    });
  }

  function unlocked(state) {
    markDots(state.total);
    showMessage("", false);
    hideHelper();
    return popCheck().then(function () {
      lockedView.hidden = true;
      verifiedView.hidden = false;
      card.classList.add("is-verified");
      return wait(cssTime("--t-unlocking", 2000));
    }).then(function () {
      window.location.href = state.redirect;
    });
  }

  /* ---------- Agent Orange's encouragement ---------- */

  function encouragement() {
    var lines = [];
    try {
      lines = JSON.parse(dialogueData.textContent).lines || [];
    } catch (error) {
      lines = [];
    }
    if (!lines.length) {
      return "";
    }
    return lines[Math.floor(Math.random() * lines.length)].text;
  }

  function showHelper() {
    var text = encouragement();
    if (!text) {
      return;
    }
    window.clearTimeout(helperTimer);
    helperBubble.textContent = text;
    helper.classList.remove("is-static");
    restartAnimation(helper, "is-visible");
    helperTimer = window.setTimeout(hideHelper, cssTime("--t-helper", 8000));
  }

  function hideHelper() {
    window.clearTimeout(helperTimer);
    helper.classList.remove("is-visible", "is-static");
  }

  helper.addEventListener("click", hideHelper);

  /* ---------- Events ---------- */

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (busy) {
      return;
    }
    var action = event.submitter && event.submitter.value === "hint" ? "hint" : "answer";
    if (action === "answer" && !input.value.trim()) {
      showMessage("Please type an answer.", true);
      input.focus();
      return;
    }

    setBusy(true);
    send(action).then(function (state) {
      setBusy(false);
      switch (state.result) {
        case "wrong":
          wrong(state);
          break;
        case "encourage":
          wrong(state);
          showHelper();
          break;
        case "hint":
          showHints(state);
          input.focus();
          break;
        case "blank":
          showMessage("Please type an answer.", true);
          input.focus();
          break;
        case "correct":
          setBusy(true);
          nextQuestion(state).then(function () {
            setBusy(false);
          });
          break;
        case "unlocked":
          setBusy(true);
          unlocked(state);
          break;
        default:
          window.location.reload();
      }
    }).catch(function () {
      setBusy(false);
      showMessage("Something went wrong. Please try again.", true);
    });
  });

  card.addEventListener("animationend", function (event) {
    if (event.animationName === "card-shake") {
      card.classList.remove("is-shaking");
    }
  });

  if (helper.classList.contains("is-static")) {
    helperTimer = window.setTimeout(hideHelper, cssTime("--t-helper", 8000));
  }
})();
