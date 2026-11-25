# KrushComics

Source for [krushcomics.com](https://krushcomics.com), a personal site built with Django. It holds
reviews and blog posts, a portfolio of development projects, and security work (CTF write-ups for
now). The look is a dark, terminal-style theme set in JetBrains Mono Nerd Font.

All content is managed through the Django admin. A small token-authenticated REST API at
`/api/v1/` exposes thoughts and projects and can create new ones.

## Features

- **Home**: banner artwork with a terminal-style `whoami` / `ls` intro, plus horizontally scrolling
  carousels of the latest thoughts and projects.
- **About / About This Site**: profile page and a page on how the site is built and hosted, both
  editable from the admin.
- **Thoughts**: reviews (rated 0–10, shown as 2:3 poster cards) and posts, shown together as one
  "thoughts" feed. Archive pages for posts, reviews or both, with search and 12-per-page pagination.
- **Projects**: project cards with GitHub links and planned additions, plus a paginated archive.
- **Security**: CTF write-ups grouped by event, with category, difficulty, tools used, a
  Markdown-rendered walkthrough and lessons learned. Write-ups stay hidden until published (staff
  can preview drafts). Labs and Research are placeholder pages for now.
- **Admin**: the stock Django admin with KrushComics styling and the site navbar on top.
- **REST API**: public read endpoints, and create endpoints that need an admin token.

## Tech stack

| Layer       | Tools                                                             |
| ----------- | ----------------------------------------------------------------- |
| Application | Python, Django 6.1, Django REST Framework, SQLite                 |
| Content     | Pillow (image uploads), Markdown (write-ups)                      |
| Static      | WhiteNoise (compressed, hashed static files)                      |
| Config      | python-dotenv (`.env` file)                                       |
| Production  | Oracle Cloud (Ubuntu), Gunicorn, Caddy (HTTPS + reverse proxy), Cloudflare DNS |
| CI/CD       | GitHub Actions with a self-hosted deployment runner               |

## Project structure

```
krushcomics/     Project settings, root URLconf, API URL router, WSGI/ASGI
core/            Home, About and About This Site pages; SiteProfile and AboutSitePage models;
                 site-wide templates (base, navbar), CSS, fonts, icons and banner images;
                 API auth check
thoughts/        Review and Post models, thoughts feed/archive/detail pages, thoughts API
projects/        Project model, projects list/archive/detail pages, projects API
security/        CTF and WriteUp models, security hub, write-up pages, safe Markdown filter
templates/admin/ Admin override (base_site.html) that adds the site navbar and admin.css
.github/         Production CI/CD workflow
```

Shared UI components and color tokens live in `core/static/core/css/site.css`. Each app's
stylesheet only adds what is specific to that app.

## Local development

**Requirements:** Python 3.12+ (CI runs 3.12).

1. Create and activate a virtual environment, then install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Gunicorn is only installed on non-Windows platforms. Use `runserver` locally.

2. Copy the example environment file and set a secret key:

   ```bash
   cp .env.example .env
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. Set up the database and an admin user:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Run the development server:

   ```bash
   python manage.py runserver
   ```

   The site runs at http://127.0.0.1:8000/ and the admin at http://127.0.0.1:8000/admin/. Content
   such as the profile, About This Site text, thoughts, projects, CTFs and write-ups is added from
   the admin.

### Environment variables

| Variable                | Default                     | Description                                             |
| ----------------------- | --------------------------- | ------------------------------------------------------- |
| `DJANGO_SECRET_KEY`     | **required**                | Django secret key. Startup fails without it.            |
| `DJANGO_DEBUG`          | `False`                     | `True` enables debug mode and local media serving.      |
| `DJANGO_ALLOWED_HOSTS`  | `127.0.0.1,localhost`       | Comma-separated host names.                             |
| `DJANGO_DATABASE_PATH`  | `<project>/db.sqlite3`      | SQLite file path. A relative path is resolved from the project root. |
| `DJANGO_MEDIA_ROOT`     | `<project>/media`           | Where uploaded images are stored.                       |

When `DEBUG` is off, session and CSRF cookies are marked secure, and Django trusts
`X-Forwarded-Proto: https` from the reverse proxy. Uploaded media is only served by Django in debug
mode. In production the web server serves it.

## Pages

| URL                                         | Page                                          |
| ------------------------------------------- | --------------------------------------------- |
| `/`                                         | Home                                          |
| `/about/`                                   | About me                                      |
| `/about-this-site/`                         | How the site is built and hosted              |
| `/thoughts/`                                | Thoughts hub                                  |
| `/thoughts/archive/<posts\|reviews\|all>/`  | Archive with search (`?q=`) and pagination    |
| `/thoughts/review/<id>/`                    | Single review                                 |
| `/thoughts/post/<id>/`                      | Single post                                   |
| `/projects/`                                | Projects hub                                  |
| `/projects/archive/`                        | All projects, paginated                       |
| `/projects/<id>/`                           | Single project                                |
| `/security/`                                | Security hub                                  |
| `/security/writeups/`                       | Published write-ups with search (`?q=`)       |
| `/security/writeups/<ctf-slug>/`            | One CTF event and its write-ups               |
| `/security/writeups/<ctf-slug>/<slug>/`     | Single write-up                               |
| `/security/labs/`, `/security/research/`    | Coming-soon placeholders                      |
| `/admin/`                                   | Django admin                                  |

## REST API

Base path: `/api/v1/`. Authentication uses DRF tokens, sent as `Authorization: Token <key>`. To
create a token for a user:

```bash
python manage.py drf_create_token <username>
```

| Method | Endpoint                        | Auth                     | Description                                     |
| ------ | ------------------------------- | ------------------------ | ----------------------------------------------- |
| GET    | `auth/check/`                   | Any valid token          | Returns the token owner's id, username and staff flags |
| GET    | `thoughts/`                     | Public                   | All reviews and posts, newest first             |
| GET    | `thoughts/<review\|post>/<id>/` | Public                   | Single review or post                           |
| POST   | `thoughts/posts/`               | Staff token              | Create a post: `{"title", "body"}`              |
| POST   | `thoughts/reviews/`             | Staff token              | Create a review: `{"title", "body", "rating"}` (0–10, at most one decimal place) |
| GET    | `projects/`                     | Public                   | All projects, newest first                      |
| POST   | `projects/`                     | Staff token              | Create a project: `{"title", "description", "github_url"}` (must be an `https://github.com/...` URL) |
| GET    | `projects/<id>/`                | Public                   | Single project                                  |

List responses look like `{"count": n, "results": [...]}`. Thought objects include `id`, `type`,
`title`, `created_at` and, for reviews, `rating`. Project objects include `id`, `title`,
`description` and `github_url`. Validation errors return `400` with an `{"errors": {...}}` object.

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/thoughts/posts/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello", "body": "First post from the API."}'
```

## Content notes

- **Thoughts:** `Review` and `Post` used to live in separate `reviews` and `posts` apps. They were
  moved into `thoughts` and still use their original tables (`reviews_review`, `posts_post`), so
  existing rows, permissions and admin history were kept.
- **Write-ups:** a write-up is not visible until **published** is checked, because most CTFs forbid
  sharing solutions while the event is running. `published_at` is set automatically the first time a
  write-up is published. Write-up slugs only need to be unique within a CTF.
- **Markdown:** write-up bodies and lessons learned are rendered with a restricted Markdown filter
  (`security/templatetags/security_markdown.py`). Raw HTML is escaped, and links or images that
  don't use `http(s)://`, `mailto:`, `/` or `#` have their URLs removed.
- **Adding Security sections:** future Labs or Research models can join the Security carousel by
  giving them a `kind` attribute, a `published_at` field and `get_absolute_url()`, then adding them
  to `security/services.py`.

## Testing

```bash
python manage.py test
```

Tests cover the API (authentication, thought list/detail, post creation), the security models,
pages, draft visibility and the Markdown sanitizer.

## Deployment

Every push to `main` (or a manual run) starts `.github/workflows/deploy-production.yml`:

1. **CI** (GitHub-hosted, Python 3.12): installs dependencies, runs `manage.py check`, fails if
   any migrations are missing, applies migrations to a throwaway SQLite database, and runs the tests.
2. **Deploy** (self-hosted runner on the Oracle Cloud production server): runs only if CI passed,
   and calls `sudo -n /usr/local/sbin/deploy-krushcomics` on the server.

In production, requests go **Cloudflare DNS → Caddy** (HTTPS, reverse proxy) **→ Gunicorn →
Django**. Static files are collected into `productionfiles/` and served by WhiteNoise.

## License

The bundled JetBrains Mono Nerd Font subsets are licensed under the SIL Open Font License 1.1 (see
`core/static/core/fonts/OFL.txt`).
