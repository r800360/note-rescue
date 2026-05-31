# Personal site (privacy-safe)

This folder is for a **public** personal website built from curated content — not your raw Notepad++ vault.

## Golden rule

**Never deploy `vault/` or LLM drafts without reviewing them.** Only `site/dist/` after `site review` passes.

## Lazy workflow

1. **One-time:** `python main.py site init` — copies `config/site.profile.example.json` → `config/site.profile.public.json` (edit your name, links, tone).

2. **Optional:** Drop public-safe `.md` snippets into `site/sources/` (resume bullets, project blurbs you wrote for LinkedIn).

3. **Draft from notes:** `python main.py site draft` (or `site draft projects` / `values` / `reading`).

4. **Review** the JSON in `site/drafts/draft-*.json` — delete anything too personal.

5. **Publish locally:** `python main.py site publish` — merges profile + latest draft → `site/public/content.json`.

6. **Build:** `python main.py site build` → opens `site/dist/index.html`.

7. **Safety check:** `python main.py site review` — must pass before uploading to GitHub Pages / Netlify.

8. Upload **only** the contents of `site/dist/`.

## Using `ask` vs `site`

| Tool | Use for |
|------|---------|
| `ask.cmd` | Private memory — "what did I write about X?" |
| `site draft` | Public website copy — strict redaction rules |

Do not paste `ask` answers straight onto the web.

## Hosting

Any static host works: GitHub Pages, Cloudflare Pages, Netlify. Point the site root at `site/dist/`.
