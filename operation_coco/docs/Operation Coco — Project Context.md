# Operation Coco — Project Context

Oct 24, 2026 · @Jake Embry

Standing context for Claude Code. Read this before every phase spec; it holds the story, the rules, and the look that every phase follows.

## What this is

Operation Coco is a puzzle-hunt website Jake is building as a wedding gift for his fiancée, Coco. They marry on December 12, 2026; the site must be finished and tested by December 5. It lives as a self-contained Django app inside Jake's site, krushcomics.com.

**The player.** Coco is not technical. Every screen must tell her exactly what to do next, in plain words. She should never feel stuck or need to know anything about computers. She may play on a laptop or a phone.

**The story: Frozen Heart.**

- An ice villain (\[name TBD\]) has frozen Jake's heart, and present-day Jake is trapped in the ice.
- A masked secret agent arrives through a time rift to help. For now he goes by **Agent Orange** (a working name). Secretly he is Jake from the future, but his face stays hidden under a hood and mask until the finale.
- The agent guides Coco through puzzles that move through their relationship from the beginning, year by year. Each solve thaws Jake's heart a little more, and the agent's glowing suit lines shift from icy blue toward warm orange as it thaws.
- In the finale the heart fully thaws, the agent pulls back his hood and mask to reveal he is Jake, and Coco reads Jake's final letter.

**Tone.** Playful and a little silly on the surface (secret-agent banter, a cartoon villain), sincere underneath. Winter, December, snow, frost, and warmth returning. Family-friendly: the villain is theatrical and goofy, never actually scary or cruel.

**Dialogue and personal content.**

- Claude Code may write **draft dialogue** so the story has life during development. Mark every draft scene with `"draft": True` and a `# DRAFT DIALOGUE — Jake will rewrite` comment so Jake can find and replace it all later.
- Draft dialogue must not invent personal facts about Jake, Coco, or their relationship (places, dates, names, inside jokes). Speak about the relationship in general terms only.
- Real answers, hints, and letters come from Jake and never appear in the repo (see Rules).

## Rules for Claude Code

These apply to every phase. If a task seems to require breaking one, stop and ask Jake.

**Git**

- Work only on the `operation-coco` branch. Before any change, confirm it is checked out; if not, stop and ask.
- Never commit to, merge into, or push `main`. Never deploy.
- Commit in small, described steps so Jake can review each one.

**Isolation from the rest of krushcomics**

- All code lives in the `operation_coco` app. Do not edit files in any other app.
- The only allowed edits outside the app: adding `"operation_coco"` to `INSTALLED_APPS`, and one `include` line in the project's root `urls.py`.
- Do not import from other project apps. The app depends only on Django and the standard library, so it can later move to its own repo.
- Templates do not extend the site's `base.html`. The app has its own base template and stylesheet.
- No changes to settings, middleware, auth, or the database configuration beyond the two edits above.

**Tech choices**

- Plain Django templates, vanilla JavaScript, and plain CSS. No npm, no build step, no frontend framework.
- No new Python or JS dependencies without asking Jake first.
- Self-host fonts and assets in the app's static folder. No external CDNs, trackers, or analytics.
- Always link internally with `{% url 'operation_coco:...' %}`, never hardcoded paths, so the app can move to a subdomain later.

**Privacy and security**

- Never transmit, log, or store anything Coco types into a fake password field. She may type a real password.
- Real answers, dialogue, and letters must never be committed. Placeholders only in the repo; real content arrives later through the admin or a private, git-ignored fixture.
- Later phases check answers on the server using salted hashes. Never put real answers in templates or JavaScript.

**Quality**

- Works on current desktop and mobile browsers, portrait phone included.
- Respect `prefers-reduced-motion`: snow and big animations reduce to a gentle or static version.
- Keyboard usable with visible focus states.
- Add Django tests for every view, and run `python manage.py test operation_coco` before each commit.

## App structure

The app is mounted at `/operation-coco/` with the URL namespace `operation_coco`. Templates and static files are namespaced so nothing collides with the rest of the site.

```
operation_coco/
    __init__.py
    apps.py
    urls.py              # app_name = "operation_coco"
    views.py
    dialogue.py          # placeholder dialogue scripts, one per scene
    tests.py
    templates/operation_coco/
        base.html        # own base: fonts, CSS tokens, snow canvas
        gate.html
        login.html
        next.html        # temporary end-of-phase placeholder
        partials/
            agent.html       # the agent sprite
            dialogue_box.html
    static/operation_coco/
        css/coco.css
        js/snow.js
        js/dialogue.js
        js/login.js
        img/agent/       # sprite SVGs, one file per pose
        fonts/
```

**Conventions**

- One JS file per behavior, loaded with `defer`. No inline `<script>` blocks except Django's `json_script` data.
- Dialogue is defined in `dialogue.py` and passed to the page with `{{ data|json_script:"dialogue-data" }}`, so it can later move into the database without changing the front end.
- All colors, fonts, and timings come from CSS custom properties in `coco.css` (see Visual identity).

## Visual identity

The look is a frozen winter night washed in light purple: soft, magical, and calm, with warm pink reserved for the heart and anything that means warmth returning.

| Token | Hex | Use |
| --- | --- | --- |
| `--night` | #1B1638 | Deepest background, sky at the top |
| `--dusk` | #3A2F6B | Background gradient middle |
| `--lavender` | #B9A7F0 | Main purple hue, glows, highlights |
| `--lilac-mist` | #E9E3FF | Frosted-glass panels |
| `--ice` | #A8E6FF | Ice, frost edges, focus rings |
| `--frost-white` | #F7F9FF | Text on dark, snowflakes |
| `--heart` | #FF7AA8 | The heart, warmth, success states |
| `--rift` | #7B5CFF | Time-rift core |
| `--rift-glow` | #5CE1FF | Time-rift outer glow |
| `--ink` | #231C45 | Text on light panels, sprite outlines |

These are starting values. Jake may tune them, so never hardcode a color outside `coco.css`.

**Type**

- Titles: a storybook display serif such as Cinzel (self-hosted).
- Interface text: a clean sans such as Inter.
- Agent dialogue and "system" messages: a friendly monospace such as JetBrains Mono, which adds the computer feel.

**Surfaces**

- Background: vertical gradient from `--night` to `--dusk`, with a faint lavender glow near the horizon and silhouettes of snowy pines along the bottom.
- Panels: frosted glass, meaning semi-transparent `--lilac-mist`, backdrop blur, a thin `--ice` border, and rounded corners.

**Motion**

- Snow falls on every page: a full-screen canvas behind the content, 60–120 flakes of mixed size and speed with a slight drift. Pause it when the tab is hidden. With reduced motion, show a few slow flakes or a static scene.
- Animations should feel soft: easing curves, nothing faster than about 150 ms.
- No sound in Phase 1. Any later audio must start muted with a visible toggle.

## Characters

Both characters are original designs. Shared art style: cartoon game sprites with chunky proportions (head about a third of total height), thick dark outlines in `--ink`, flat colors with one soft shade tone, and a small highlight. Jake's reference is the general cartoon feel of TryHackMe's Advent of Cyber art; use it only as a style direction, and never copy any TryHackMe character, logo, mascot, or artwork.

### Agent Orange (the guide)

A futuristic secret agent. Working name only; Jake will rename him later, so keep the name in one constant (`AGENT_NAME` in `dialogue.py`).

- **Hood:** a black hood, drawn up, framing the face with a sharp silhouette.
- **Mask:** a sleek matte-black mask covering the whole face, with a narrow glowing visor slit for eyes. No facial features visible.
- **Suit:** fitted black tactical suit with thin glowing circuit-trace lines along the arms, chest, and hood edge. A small glowing heart emblem on the chest.
- **The glow tells the story.** All glowing lines and the heart emblem use one color, `--agent-glow`, which shifts from icy blue (`--glow-cold`) at the start toward warm orange (`--glow-warm`) as Jake's heart thaws. The color comes from the thaw level (see the Phase 2 spec); never hardcode it in the SVG.
- **Built for the reveal.** The hood and mask are separate SVG groups (`#hood`, `#mask`) layered over a face group (`#face`) that stays hidden until the finale, when they animate off. The face group can be an empty placeholder for now.
- **Jake's features (finale only):** \[hair, beard, glasses, skin tone, eye color — Jake to fill in later\].

**Poses** (one SVG per pose in `img/agent/`, same canvas size and anchor point): `idle` (slight bob), `talk`, `point`, `happy`, `worried`, and `cast` (arm raised, glow flaring, used when he thaws something).

### The villain

An ice villain who froze Jake's heart. Name: \[TBD by Jake\]; keep it in one constant (`VILLAIN_NAME` in `dialogue.py`).

- **Vibe:** a gleeful, chaotic trickster. Jake's inspirations are the energy of the Joker, a gremlin, Junkrat from Overwatch, the Green Goblin, and Jack Frost. Blend that energy into a new character; do not copy any of their costumes, faces, or signature features.
- **Look:** small, wiry, and hunched, with long fingers and pointed ears. Frost-pale skin with a blue tint, spiky hair made of jagged ice crystals, a huge manic grin with little icicle teeth, and wild mismatched eyes (one bigger than the other). Tattered frost-blue coat with icicle tails, and goggles pushed up on his forehead.
- **Colors:** icy white, frost blue, and a sickly teal accent (`--villain` token), so he never shares the agent's glow color.
- **Ride:** a rickety flying car, half sled and half jalopy, with sputtering jet thrusters, icicles hanging off it, and a trail of snow exhaust. Draw the car as its own SVG so the villain can sit in it and the two fly together.

**Poses** (in `img/villain/`): `idle` (fidgeting in the car), `cackle`, `point`, `smug`, and `angry` (for later phases).

**Build notes for both**

- Hand-written SVGs with named groups (`#head`, `#eyes`, `#mouth`, `#cape`/`#coat`) so CSS can animate blinks, bobbing, and coat flutter.
- These are working drafts. Jake may swap in commissioned or hand-drawn art later, so pages reference poses by file name only.

## Roadmap

Build only the phase Jake has handed over a spec for. Later phases are listed so earlier ones don't paint the project into a corner.

1. **Phase 1 — Gate and frozen login.** Built. Landing page, fake lock screen, failed password, time rift, agent arrives and talks.
2. **Phase 2 — Security questions and the frozen desktop.** Three questions about the relationship checked on the server, then the FrostOS desktop with frozen app icons, the villain's arrival, and Agent Orange thawing the first icon.
3. **Phases 3+ — Memory puzzles.** Each frozen app is one puzzle, in the order the relationship happened. Each solve raises the thaw level, thaws the next app, and unlocks a reward (letter, photo, voice memo), encrypted with a key derived from its answer.
4. **Finale.** The heart fully thaws, Agent Orange removes his hood and mask to reveal he is Jake, and Coco reads the final letter.

**Shared systems every phase uses**

- **Thaw level:** a number from 0 to 1 stored in the session. It drives the agent's glow color and the heart meter.
- **Progress gating:** each page checks session progress on the server, so later stages can't be reached by typing a URL.
- **Reusable partials:** the dialogue box, agent sprite, villain sprite, and desktop shell.
- **One desktop icon per stage:** icons stay frozen until their stage unlocks.
