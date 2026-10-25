# Operation Coco — Phase 2 Build Spec

Oct 24, 2026 · @Jake Embry

Phase 2 picks up where the failed login ends: Coco answers three security questions, the FrostOS desktop opens with every app frozen, the villain flies in to gloat, and Agent Orange thaws the first app for her. Read **Operation Coco — Project Context** first; its rules apply here. Phase 1 is built and working, so change it only where this spec says to.

## Scope, flow and pages

**The flow from Coco's side**

1. The password fails and Agent Orange arrives (Phase 1, with redrawn sprite and new draft dialogue). He tells her the account has been locked and she'll have to prove she's really Coco. His last line's button leads to the security questions.
2. The lock screen changes to **Account locked**. She answers three security questions, one at a time.
3. After the third, "Identity verified" and an unlocking bar, then the FrostOS desktop loads.
4. Every app icon on the desktop is frozen in ice. After a calm moment, the villain flies across the screen in his car, stops, and gloats about freezing Jake's heart.
5. The villain zooms off. The time rift opens and Agent Orange returns to explain the mission.
6. Agent Orange thaws one app icon. It glows, and his last line tells her to click it.
7. Clicking it opens a "to be continued" placeholder where Phase 3 will begin.

**Pages**

| URL | Name | Purpose | Requires |
| --- | --- | --- | --- |
| `/operation-coco/unlock/` | `operation_coco:unlock` | Security questions, one per screen | nothing |
| `/operation-coco/desktop/` | `operation_coco:desktop` | Frozen desktop, villain, agent, first thaw | all 3 questions answered |
| `/operation-coco/stage/1/` | `operation_coco:stage` | Placeholder for the first memory puzzle | all 3 questions answered |
| `/operation-coco/next/` | (existing) | Now redirects to `unlock` | — |
| `/operation-coco/reset/` | `operation_coco:reset` | Clears this app's session keys and returns to the gate, for Jake's testing | — |

A page whose requirement isn't met redirects to `unlock`, never to an error page.

**Out of scope:** the first memory puzzle itself, rewards and encryption, any real letters, audio, and the finale.

## Agent Orange and the thaw glow

The agent sprite from Phase 1 is replaced everywhere by the new Agent Orange design in the Project Context doc: black hood, full black mask with a glowing visor slit, black tactical suit with glowing circuit lines and a chest heart emblem. Redraw all poses, add the new `cast` pose, and build the hood and mask as separate groups over a hidden `#face` group.

**New tokens in `coco.css`**

| Token | Hex | Use |
| --- | --- | --- |
| `--glow-cold` | #3FD0FF | Agent glow at thaw 0 |
| `--glow-warm` | #FF8A2A | Agent glow at thaw 1 |
| `--villain` | #4FD1B5 | Villain accent and his name tag |
| `--ice-block` | #CDEFFF | Ice covering frozen icons, at partial opacity |

**How the glow is computed**

- A helper `get_thaw_level(request)` returns a number from 0 to 1 from session progress. In Phase 2 it is always 0. Later phases raise it as puzzles are solved.
- Every page sets `--thaw` on `<body>` from that value, e.g. `style="--thaw: 0"`.
- In CSS: `--agent-glow: color-mix(in oklab, var(--glow-warm) calc(var(--thaw) * 100%), var(--glow-cold));`
- The agent SVGs use `currentColor` or `var(--agent-glow)` for every glowing stroke and the heart emblem, plus a soft `drop-shadow` glow in the same color.
- Add a development-only way to preview the glow: when `DEBUG` is true, `?thaw=0.5` on any page overrides the value. It must do nothing in production.

**The `cast` effect.** When the agent thaws something, his glow briefly flares to full `--glow-warm` for about 600 ms, then fades back to his current thaw color. It hints at what the glow will become.

## Security questions

Three questions about the relationship, in order from its beginning. Jake already has the questions and answers. **They must never appear in the code, templates, fixtures, tests, docs, or git history.** Jake enters them himself with a setup command, and only salted hashes of the answers are stored.

**The screen** (same FrostOS lock-screen look as Phase 1, snow falling again)

- The card header changes to a frosted lock icon and **Account locked**, with the line "Please answer your security questions to unlock your account."
- Three progress dots show which question she's on.
- One question at a time: the question text, an answer field, and a **Submit** button. Enter also submits.
- **Wrong answer:** the card shakes and the line reads "That answer doesn't match our records." The field keeps her text so she can fix a typo.
- **Hints:** after the first wrong answer, a "Need a hint?" link appears. Each click reveals the next hint for that question (up to three, if Jake has entered them).
- **Encouragement:** after three wrong answers on one question, Agent Orange pops in from a small rift in the corner with one short encouraging line, then leaves.
- **Right answer:** a check mark, the ice on that progress dot cracks away, and the next question slides in.
- **After question three:** "Identity verified. Welcome back, Coco." then an "Unlocking…" bar for about 2 seconds, then redirect to the desktop.

This is a real form: POST with CSRF, handled by the server. That's fine here, unlike the fake password field, because these are answers Jake chose, not a password of hers.

**Storage**

- Model `SecurityQuestion`: `order` (unique int), `prompt` (text), `answer_hashes` (JSON list of hash strings), `hints` (JSON list of up to 3 strings).
- Register it in the admin with `answer_hashes` read-only.
- Session keys: `coco_questions_solved` (0–3) and `coco_unlocked` (bool). A correct answer only advances from the current question; skipping ahead by URL or form tampering is impossible.

**Answer checking**

- `normalize_answer(text)`: NFKC Unicode normalization, lowercase, `&` becomes "and", remove everything except letters, digits, and spaces, drop the words "a", "an", "the", and "and", then remove all spaces. So "The Cat & the Hat" and "cat hat" normalize the same, as do "A Red Balloon" and "red balloon". Use only made-up examples like these anywhere in the code.
- Store each accepted answer as `make_password(normalize_answer(answer))`. Check with `check_password` against every stored hash.

**Setup command:** `python manage.py set_coco_questions`

- Interactive. For each of the three questions it asks for the question text with `input()`, then the main answer and any extra accepted variants with `getpass()` (a blank entry ends the variants), then up to three hints with `input()`.
- It normalizes and hashes the answers, saves the three `SecurityQuestion` rows (replacing any existing ones), and never prints, logs, or writes answers anywhere else.
- It prints a confirmation like "Saved 3 questions" when done.

**Tests** create their own dummy questions with made-up answers in `setUp`.

## The frozen desktop

The desktop is the hub for the rest of the game: every later puzzle starts from one of its icons. Build it as a reusable partial (`partials/desktop_shell.html`).

**Layout**

- **Top bar:** FrostOS on the left; on the right the fake status icons, the clock, and a **heart meter**: a small heart icon encased in ice with "Jake's heart: 0% thawed." The percentage comes from the thaw level.
- **Wallpaper:** the winter night scene, a little darker and colder than the lock screen, with snow falling.
- **Icons:** six app icons in a grid on the left side of the screen (a centered 3×2 grid on phones). Each is a rounded-square icon with a label under it, styled like a friendly desktop app.
- **Taskbar:** a frosted bar along the bottom with a few decorative pinned icons. Nothing on it works.

**The icons**

- One icon per future stage, in story order. Placeholder names and simple original icons for now: Memories, Messages, Photos, Maps, Music, and Letters. Keep the list in one Python constant (`DESKTOP_APPS`) with `slug`, `label`, `icon`, and `stage` fields, since Jake will rename and reorder them.
- **Frozen state:** a translucent `--ice-block` slab over the icon with crystal facets and a few cracks, frost creeping over the label, and the whole icon desaturated. Not clickable.
- **Clicking a frozen icon:** a tiny shake and a small tooltip, "Frozen solid." Nothing else.
- **Thawed state:** the ice is gone, the icon is full color with a soft `--glow-warm` halo and a gentle pulse, and it links to its stage URL.
- Which icons are thawed is decided on the server from session progress. In Phase 2, the first icon becomes thawed once the desktop intro finishes.

**Intro only plays once**

- On the first visit, the villain-and-agent intro plays (next two sections). When it finishes, the page sends a small POST to `operation_coco:desktop_intro_done`, which sets the session key `coco_desktop_intro_seen` and marks stage 1 thawed.
- On later visits the desktop loads calm, with stage 1 already thawed and no intro. A small **Replay intro** link in the taskbar lets her watch it again.

## The villain arrives

The villain design is in the Project Context doc. This is his first appearance, so it should feel like a cartoon villain's grand entrance: fast, loud in motion, and funny.

**Sequence**

1. **Calm (1.5 s).** The desktop loads with gentle snow. Coco can look around; frozen icons shake if clicked.
2. **Warning (1 s).** The snow turns sideways as if a wind picked up. The screen edges flicker with frost and the heart meter shivers.
3. **Flyby (1.5 s).** The flying car streaks across from left to right, high on the screen, trailing snow exhaust and a frosty sparkle. A swoosh of frost spreads across the icons as he passes.
4. **Return (1 s).** He loops back in from the right, swerves, and brakes to a hover at the top center, the car bobbing.
5. **Gloat.** He stands up in the car in the `cackle` pose and the dialogue box opens with his name tag in `--villain`. He switches between `cackle`, `point` (at the heart meter), and `smug` as he talks.
6. **Exit (1.2 s).** After his last line he cackles, guns the thrusters, and shoots off the top-right of the screen. His trail of snow drifts down and settles over the icons, making the ice look thicker.

**Details**

- Every frozen icon stays frozen through this whole scene.
- No real timer. He can say time is running out, but nothing on screen counts down, and Coco can never fail or run out of time.
- With reduced motion: no flyby; he fades in at the top center, talks, and fades out.

## Agent Orange's rundown and the first thaw

**Sequence**

1. **Rift (1 s).** A moment after the villain leaves, the time rift tears open at the lower right of the screen (above the dialogue area on phones), the same effect as Phase 1.
2. **Arrival (0.8 s).** Agent Orange hops out in `worried` and settles into `idle`. The rift shrinks to a small portal behind him.
3. **Rundown.** His dialogue explains what happened and what she has to do (beats below). He uses `point` toward the heart meter when he mentions Jake's heart.
4. **The thaw (2 s).** On his second-to-last line he switches to `cast` and his glow flares. A beam of warm light arcs from his hand to the first icon. The ice on it cracks in a spreading web, splits, and melts away with a few drips. The icon comes back to full color with its warm halo and pulse, and its label unfrosts.
5. **Call to action.** His last line tells her to click the glowing app. The dialogue box closes so the desktop is fully usable, and Agent Orange stays beside the portal in `idle`, occasionally glancing at the icon.
6. **Click.** The thawed icon leads to the stage 1 placeholder: a frosted card with the agent and "\[PLACEHOLDER: to be continued\]".

The POST to `desktop_intro_done` happens when the thaw animation finishes, so a reload after that point shows the calm desktop with the first icon thawed.

## Draft dialogue

Claude Code writes draft dialogue for every scene in this phase, and rewrites the Phase 1 placeholder lines to match the new story. Follow the dialogue rules in the Project Context doc: mark every scene `"draft": True`, add the `# DRAFT DIALOGUE — Jake will rewrite` comment, and invent no personal details about Jake, Coco, or their relationship.

**Voices**

- **Agent Orange:** calm, confident, warm. Secret-agent cadence with a little dry wit. Calls her "Coco" or "Agent Coco." Never says he's Jake, but now and then seems to know her a little too well. Encouraging, never condescending.
- **The villain:** theatrical and gleeful. Cackles, ice and cold puns, big gestures, monologues a beat too long. Menacing in a cartoon way only; nothing actually cruel or frightening.
- Keep every line under about 140 characters so it fits the box on a phone. Five to nine lines per scene.

**Data format changes**

- Each line now names its `speaker` (`"agent"` or `"villain"`), since scenes can mix them.
- A line may carry a `cue` that fires an animation when the line starts, e.g. `"cue": "thaw"` or `"cue": "villain_exit"`. `dialogue.js` emits a `dialogue:cue` event and the page script handles it.
- Names come from the `AGENT_NAME` and `VILLAIN_NAME` constants.

**Scene beats**

1. **`phase1_intro`** (rewrite) — Agent Orange stops her: the password won't work. Someone has broken in and locked Jake's system. He introduces himself as Agent Orange, from a long way off. To get in, she has to prove she's really Coco. Button: on to the security questions (`operation_coco:unlock`).
2. **`unlock_encourage`** — a pool of three or four single lines; one is picked at random when she misses a question three times. Example tone: take your time, the answer is in your memories, try the hint.
3. **`desktop_villain`** — the villain introduces himself with flair, gloats that he has frozen Jake's heart solid, points at the heart meter, says every memory on this computer is frozen too, warns that she only has so much time before Jake is frozen forever, then cackles and leaves (`cue: villain_exit` on the last line).
4. **`desktop_agent`** — Agent Orange arrives: it looks like Jake's heart has been frozen over. She's the only one who can save him, and they have to move fast. He'll help as best he can, but she alone has the power to save him. Each frozen app holds a memory; every memory she recovers thaws his heart a little more. He thaws the first one (`cue: thaw`). Final line: click the glowing app to begin.

**Example of the format only** (not final words):

```python
# DRAFT DIALOGUE — Jake will rewrite
DESKTOP_AGENT = {
    "draft": True,
    "lines": [
        {"speaker": "agent", "pose": "worried", "text": "..."},
        {"speaker": "agent", "pose": "cast", "text": "...", "cue": "thaw"},
    ],
}
```

## Build steps

Work through these in order. Commit after each numbered step, run `python manage.py test operation_coco` before every commit, and stop at the end for Jake's review.

1. **Check the branch.** Confirm you're on the same feature branch Phase 1 was built on and the working tree is clean. If not, stop and ask.
2. **Thaw level and tokens.** Add the new CSS tokens, `get_thaw_level()`, `--thaw` on `<body>` for every page, the `--agent-glow` mix, and the `DEBUG`-only `?thaw=` override.
3. **Redraw Agent Orange.** New SVGs for all six poses with the hood, mask, glowing lines, and hidden `#face` group. Swap them into Phase 1 and check the Phase 1 sequence still plays correctly at thaw 0 and 0.5.
4. **Upgrade the dialogue system.** Per-line `speaker`, a villain name tag style, and `cue` events. Phase 1 must keep working.
5. **Rewrite Phase 1 dialogue.** Draft `phase1_intro` from the beats, with its button going to `unlock`. Make `/next/` redirect to `unlock`.
6. **Security question model.** `SecurityQuestion`, its migration (run it on the local development database only), and the admin registration.
7. **Answer checking.** `normalize_answer()` and the hash check, with unit tests using made-up answers.
8. **Setup command.** `set_coco_questions`, interactive, with `getpass` for answers. Test it with mocked input.
9. **Unlock page.** The Account Locked screen, one question at a time, wrong-answer shake, tiered hints, the encouragement pop-in, and "Identity verified" with the unlocking bar. Add a progress-gating helper used by every later view.
10. **Desktop shell.** The partial, top bar with heart meter, `DESKTOP_APPS`, frozen and thawed icon states, the "Frozen solid" tooltip, and the taskbar. Gate it behind `coco_unlocked`.
11. **Villain art.** SVGs for the five villain poses and the flying car.
12. **Desktop intro.** The villain sequence, the agent rundown, the thaw animation, the `desktop_intro_done` POST, the calm return visit, and the Replay intro link.
13. **Stage placeholder and reset.** `stage/1/` (gated) and the `reset` view.
14. **Draft dialogue.** Write `unlock_encourage`, `desktop_villain`, and `desktop_agent` from the beats.
15. **Tests.** Gating redirects for every gated URL; correct answers advance one question at a time and wrong ones don't; normalization cases; hints only appear after a miss; `desktop_intro_done` sets the session key; reset clears it; `?thaw=` is ignored when `DEBUG` is false.
16. **Final check.** `git diff --stat main` must show only files inside `operation_coco/` plus the two lines from Phase 1. Confirm no fixture, test, or file contains real questions or answers.
17. **Report and stop.** Summarize what changed, list every placeholder and draft scene for Jake, give him the exact steps to run the migration and `set_coco_questions`, and note anything unclear. Don't start Phase 3.

## Acceptance checklist

Jake checks these by hand, after running the migration and `set_coco_questions` with the real answers on his local machine.

- [ ] `python manage.py test operation_coco` passes
- [ ] The rest of krushcomics looks and works exactly as before
- [ ] Agent Orange has the hood, mask, and glowing lines in every pose, Phase 1 included
- [ ] `?thaw=0`, `?thaw=0.5`, and `?thaw=1` shift his glow from blue to orange locally
- [ ] Phase 1 dialogue ends with a button to the security questions
- [ ] Each real answer works, including with different capitalization, punctuation, and "the"
- [ ] Wrong answers shake and keep the text; hints appear after a miss
- [ ] Three misses on one question bring in Agent Orange with an encouraging line
- [ ] Visiting `/desktop/` or `/stage/1/` directly before unlocking redirects to the questions
- [ ] The desktop shows six frozen icons and "Jake's heart: 0% thawed"
- [ ] Villain flies in, gloats, and leaves; Agent Orange arrives and thaws the first icon
- [ ] The thawed icon opens the stage 1 placeholder
- [ ] Reloading after the intro shows the calm desktop with the first icon still thawed
- [ ] Replay intro works; `/reset/` starts everything over
- [ ] Works on a phone in portrait and with reduced motion turned on
- [ ] No real question or answer appears anywhere in the repo or git history
