# Operation Coco — Phase 1 Build Spec

Oct 24, 2026 · @Jake Embry

Phase 1 builds the gate page and the frozen login screen: Coco tries a password, it fails, a time rift opens, and future Jake arrives to talk to her. Read **Operation Coco — Project Context** first; its rules apply here.

## Scope and pages

Phase 1 has three pages, no database models, and no server-side form handling.

| URL | Name | Template | Purpose |
| --- | --- | --- | --- |
| `/operation-coco/` | `operation_coco:gate` | `gate.html` | Landing page with the "If you are Coco" button |
| `/operation-coco/login/` | `operation_coco:login` | `login.html` | Fake lock screen, failed password, rift, agent, dialogue |
| `/operation-coco/next/` | `operation_coco:next` | `next.html` | Temporary "to be continued" page where Phase 2 will start |

**In scope:** the app skeleton, its base template and stylesheet, falling snow, the three pages, the failed-login sequence, the time rift, the agent sprite (draft art), the reusable dialogue box, placeholder dialogue, and tests.

**Out of scope:** security questions, answer checking, progress tracking, models, real dialogue, audio, a subdomain, and any link from the main krushcomics site. Jake adds that link himself.

## Gate page

The gate is the doorway from krushcomics. It sets the winter mood in one screen and has exactly one thing to do.

- Full-screen night gradient, falling snow, pine silhouettes along the bottom (see Visual identity).
- Centered frosted-glass card containing:
  - Title in the display font: **Coco's Wedding Game**
  - One line below: "If you are Coco, please proceed."
  - A large button: **Proceed** (or \[label TBD by Jake\]), linking to `operation_coco:login`.
- The button glows softly in `--lavender` and brightens on hover and focus. Minimum touch target 48 px tall.
- On click, play a short fade-to-white "frost" transition (about 400 ms) before navigating. Skip it with reduced motion.
- Page `<title>`: "Operation Coco".
- Add `<meta name="robots" content="noindex, nofollow">` to every page in the app so search engines don't list it.

## Login screen

The login page looks like the lock screen of a virtual machine, the kind that opens in a browser tab. It is decoration only: nothing on it works except the password field and the agent's dialogue.

**Framing**

- The whole page is the "virtual desktop." A thin top bar reads **FrostOS** on the left with fake status icons on the right (Wi-Fi, battery, a snowflake). The icons do nothing.
- Background: the winter night scene with snow, plus a soft lavender aurora band behind the login card.
- Do not imitate the branding of Windows, macOS, or any real operating system. FrostOS is fictional.

**Center column, top to bottom**

1. A live clock (hours and minutes, large, light weight) with the date below it, from the visitor's local time.
2. A round avatar, 96 px: a frosted circle with a small icy heart icon inside.
3. Username: **Coco**, shown as text, not an editable field.
4. Password field with placeholder "Password" and a submit arrow button on its right edge. Enter also submits.
5. A small hint line under it in `--frost-white` at 70% opacity: "Enter your password to sign in."

**Password field rules (privacy)**

- The field sits in a `<form>` whose submit handler calls `preventDefault()`. No `action`, no `method="post"`, no fetch, no logging.
- Set `autocomplete="off"` and give the input no `name` attribute, so browsers don't offer to save it.
- Clear the field's value immediately after a submit.

**Phone layout**

- The top bar shrinks to the clock and icons; the card fills 90% of the width; the date stays visible.
- Nothing scrolls horizontally, and the keyboard opening must not hide the password field.

## The failed login sequence

Any submit fails, including an empty one. The first attempt starts this sequence; it runs once and cannot be retriggered without reloading. Total length is about 5 seconds before the first dialogue line.

1. **Verifying (0.8 s).** The input and button disable. A small spinner and "Verifying…" replace the hint line.
2. **Denied (1 s).** The card does a short horizontal shake. The hint line becomes "Incorrect password." in `--heart`. The field clears.
3. **The freeze (1 s).** The snow slows to a stop in mid-air. Frost creeps in from the screen edges as a translucent `--ice` vignette with crystal texture. The clock freezes.
4. **The rift opens (1.2 s).** To the right of the login card (above it on phones), a time rift tears open: a vertical oval of swirling `--rift` light with a `--rift-glow` halo and sparks drifting out of it. It grows from a bright point.
5. **The agent arrives (0.8 s).** The agent sprite pops out of the rift with a small hop, lands beside the card in the `worried` pose, and settles into `idle`. The rift shrinks to a small shimmering portal behind him and stays there.
6. **Dialogue begins.** The dialogue box slides up from the bottom of the screen and the first line starts typing.

**Details**

- Use CSS animations and classes toggled by `login.js`; each step is a function, chained by `animationend` events or timers, so steps are easy to re-time.
- With reduced motion: skip the shake and the creeping frost, fade the rift and agent in over 300 ms, and start the dialogue right away.
- After the agent appears, the login card stays visible but dimmed and frosted over, so the scene reads as "the computer is frozen."
- The snow stays stopped for the rest of this page. That makes the freeze feel like part of the story.

## Dialogue system

The dialogue box is a reusable partial (`partials/dialogue_box.html` + `dialogue.js`) that every later phase will use, so build it general, not just for this scene.

**Look**

- A frosted-glass panel docked to the bottom of the screen, full width on phones and max 720 px on desktop.
- A name tag on its top-left edge showing the speaker's codename.
- Text in the monospace font, about 18 px, high contrast.
- A small blinking ▼ in the bottom-right corner when a line is finished, meaning "tap to continue."

**Behavior**

- Each line types out at about 35 characters per second. While a line types, the agent alternates between `talk` and the line's pose.
- Click, tap, Enter, or Space: if the line is still typing, show it in full; if it's finished, go to the next line.
- The final line can carry a button instead of the ▼. Its label and target come from the data.
- Text appears in an `aria-live="polite"` region so screen readers announce each line.
- With reduced motion, lines appear in full instead of typing.

**Data format** (in `dialogue.py`, rendered with `json_script`)

```python
PHASE1_INTRO = {
    "speaker": "[Agent codename]",
    "lines": [
        {"pose": "worried", "text": "[PLACEHOLDER: agent stops her and explains the password won't work]"},
        {"pose": "idle",    "text": "[PLACEHOLDER: agent introduces himself as Jake from the future]"},
        {"pose": "worried", "text": "[PLACEHOLDER: the ice villain froze present-day Jake's heart]"},
        {"pose": "point",   "text": "[PLACEHOLDER: only she can thaw it, and he'll guide her]"},
        {"pose": "happy",   "text": "[PLACEHOLDER: call to action]",
         "button": {"label": "[PLACEHOLDER: button label]", "url_name": "operation_coco:next"}},
    ],
}
```

The view resolves `url_name` with `reverse()` before rendering, so the front end receives a ready URL. Jake will replace every placeholder line himself; keep them obviously unfinished.

## Build steps

Work through these in order. Commit after each numbered step, run the tests before every commit, and stop at the end for Jake's review.

1. **Check the branch.** Run `git branch --show-current`. If it isn't `operation-coco`, stop and ask Jake.
2. **Create the app.** `python manage.py startapp operation_coco`, then lay out the folders from App structure.
3. **Register it.** Add `"operation_coco"` to `INSTALLED_APPS` and `path("operation-coco/", include("operation_coco.urls"))` to the root `urls.py`. Touch nothing else outside the app.
4. **URLs and views.** Three simple views (`gate`, `login`, `next`) rendering their templates, with `app_name = "operation_coco"`.
5. **Base template and stylesheet.** `base.html` with fonts, the `noindex` meta tag, the CSS tokens, the background scene, and the snow canvas slot. Commit and check that all three pages render.
6. **Snow.** `snow.js`: canvas snowfall with drift, a pause when the tab is hidden, a reduced-motion version, and a `window.cocoSnow.freeze()` function the login page can call.
7. **Gate page.** The card, title, line, button, and frost transition.
8. **Login screen, static.** Top bar, clock, avatar, username, password field, hint line, and phone layout. No failure behavior yet.
9. **Agent sprite.** Draft SVGs for the five poses in `img/agent/`, and the `partials/agent.html` partial that swaps poses by class.
10. **Dialogue box.** The partial, `dialogue.js`, and the placeholder `PHASE1_INTRO` script passed in by the login view.
11. **Failed login sequence.** `login.js` running steps 1–6 of the sequence, including the freeze, rift, agent arrival, and dialogue start.
12. **Next page.** A simple frosted card: "\[PLACEHOLDER: to be continued\]" with the agent in `idle`.
13. **Tests.** In `tests.py`: each URL returns 200 and uses its template; the gate links to the login URL; the login page contains no `<form>` with `method="post"` or an `action`; the login response contains the `dialogue-data` script; every page has the `noindex` tag.
14. **Final check.** Run `git diff --stat main`. Only files inside `operation_coco/`, the settings line, and the root URL line may appear.
15. **Report and stop.** Summarize what was built, list every placeholder Jake needs to fill, and note anything in the spec that was unclear. Don't start Phase 2.

## Acceptance checklist

Jake checks these by hand before calling Phase 1 done.

- [ ] `python manage.py test operation_coco` passes
- [ ] Only `operation_coco/`, `INSTALLED_APPS`, and the root URL line changed
- [ ] The rest of krushcomics looks and works exactly as before
- [ ] Gate page shows the title, the line, and the button, with snow falling
- [ ] Button leads to the login screen with the frost transition
- [ ] Login screen shows FrostOS bar, live clock and date, avatar, Coco, password field
- [ ] Any password, including empty, fails
- [ ] Browser dev tools show no network request when the password is submitted
- [ ] Browser does not offer to save the password
- [ ] Snow freezes, frost creeps in, rift opens, agent hops out
- [ ] Dialogue types out; tap, click, Enter, and Space all advance it
- [ ] Last line's button goes to the next page
- [ ] Works on a phone in portrait, with nothing hidden behind the keyboard
- [ ] With reduced motion turned on, everything still works with calmer animation
- [ ] Every placeholder is listed in Claude Code's final report
