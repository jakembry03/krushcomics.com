# Operation Coco — Project Context

Oct 24, 2026 · @Jake Embry

Standing context for Claude Code. Read this before every phase spec; it holds the story, the rules, and the look that every phase follows.

## What this is

Operation Coco is a puzzle-hunt website Jake is building as a wedding gift for his fiancée, Coco. They marry on December 12, 2026; the site must be finished and tested by December 5. It lives as a self-contained Django app inside Jake's site, krushcomics.com.

**The player.** Coco is not technical. Every screen must tell her exactly what to do next, in plain words. She should never feel stuck or need to know anything about computers. She may play on a laptop or a phone.

**The story: Frozen Heart.**

- An ice villain (\[name TBD\]) has frozen Jake's heart, and present-day Jake is trapped in the ice.
- A superhero agent arrives through a time rift to help. He is Jake from the future.
- The agent guides Coco through a series of puzzles. Each one is a memory from their relationship, and each solve thaws Jake's heart a little more.
- The final puzzle thaws it completely and brings Jake back. The ending is a letter from Jake.

**Tone.** Playful and a little silly on the surface (secret-agent banter, a cartoon hero), sincere underneath. Winter, December, snow, frost, and warmth returning.

**Content placeholders.** Jake writes all dialogue, answers, and letters himself. Until he does, use clearly marked placeholders like `[PLACEHOLDER: agent introduces himself]`. Never invent personal details about Jake, Coco, or their relationship.

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

## The agent character

The guide is Jake from the future, a small superhero who arrives through a time rift. Codename: \[TBD by Jake\]. He is an original character; Jake's own likeness, not anyone else's design.

**Art style**

- Cartoon game sprite: chunky proportions with a large head (about a third of total height), big expressive eyes, and a confident grin.
- Thick dark outlines in `--ink`, flat colors with one soft shade tone, and a small highlight.
- Jake's reference is the general cartoon feel of TryHackMe's Advent of Cyber art. Use that only as a style direction (bold outlines, flat shading, friendly heroic poses). Do not copy any TryHackMe character, logo, mascot, or artwork.

**Design**

- Superhero suit in deep indigo with thin glowing `--ice` circuit-trace lines, a nod to Jake's hacker side.
- Short cape in `--lavender`, frosted at the edges.
- A heart emblem on the chest in `--heart`, glowing softly. It ties to the story: he carries the warmth that will thaw present-day Jake.

**Color progression (warming up)**

- He starts with an icy blue look: cool blue suit, `--ice` circuit traces, and a frosty cape. That gives the hacker/programmer feel and shows that he is frozen too.
- As Coco moves through the puzzles, his colors shift gradually and slowly toward a warm orange, a little more with each solve, until he is fully warm at the finale.
- The `--heart` emblem stays pink the whole way. It is the warmth he carries.
- Build it so a single value drives the shift: the agent's colors are CSS custom properties in `coco.css`, mixed between an icy set and a warm set by one `--agent-warmth` value from 0 (frozen) to 1 (fully warm). Later phases set that value from server-side progress; Phase 1 keeps it at 0.
- Jake's features: \[hair color and style, beard yes/no, glasses yes/no, skin tone, eye color — Jake to fill in\]. Until filled, use neutral defaults and mark them in a code comment.

**Poses** (one SVG file per pose in `img/agent/`, same canvas size and anchor point so they swap cleanly)

- `idle` — standing, slight bob animation
- `talk` — mouth open, for alternating while text types
- `point` — arm out, directing her attention
- `happy` — big smile, fist pump
- `worried` — brow furrowed, used when talking about the frozen heart

**Build notes**

- Draw each pose as a hand-written SVG with named groups (`#head`, `#eyes`, `#mouth`, `#cape`) so CSS can animate blinking and cape flutter.
- The first SVGs are a working draft. Jake may replace them with commissioned or hand-drawn art later, so keep every page referencing poses by file name only.

## Roadmap

Only Phase 1 is being built now. The later phases are listed so Phase 1 doesn't paint the project into a corner. Don't build them until Jake hands over their spec.

1. **Phase 1 — Gate and frozen login.** Landing page with a button, fake lock screen, the failed password, the time rift, the agent appears and talks.
2. **Phase 2 — Security questions.** Three questions about the relationship, checked on the server against salted hashes, with tiered hints.
3. **Phases 3+ — Memory puzzles.** Each one recovers a memory and thaws part of the heart. Rewards (letters, photos, voice memos) are encrypted with keys derived from the answers.
4. **Finale.** The heart fully thaws, Jake returns, the final letter.

**Design for later phases now**

- Keep the dialogue box and agent sprite as reusable partials; every phase uses them.
- Plan for server-side progress tracking in a session, so later stages can't be reached by typing a URL.
- A heart-thaw meter will likely appear in later phases; leave room in the layout's top corner.
