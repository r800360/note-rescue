# note-rescue

A local-first tool that rescues Notepad++ unsaved tabs into a searchable Markdown vault — without deleting anything.

Notepad++ is a great scratchpad, but thousands of open unsaved tabs can slow it down or stop it from starting. **note-rescue** backs up your session, imports new notes into organized folders, extracts TODOs, and gives you one-click search and reset — so you can keep scribbling in Notepad++ and let automation handle the rest.

Non-destructive by default: backups are copied, sessions are renamed (not deleted), and imports skip duplicates across runs.

> **Quick reference:** [WORKFLOWS.md](WORKFLOWS.md) — one page of “I want X → run Y” for every common task.  
> **Private vs public:** `ask.cmd` stays on your machine. `site.cmd` builds content for the web — review before deploy.

---

## Lazy user quick start

If you want almost zero maintenance:

### One-time setup

```powershell
cd C:\Users\YOU\Documents\note-rescue
.\setup.ps1
```

Creates the virtual environment, installs dependencies, and optionally registers a **daily 9 PM sync** Windows task.

### Daily life (do almost nothing)

1. **Take notes in Notepad++** — unsaved tabs are fine.
2. **At 9 PM**, Windows runs sync automatically. You get a toast with how many notes were rescued, tab count, and risk level.
3. When Notepad++ feels slow again, double-click **`reset-npp.cmd`** — sync first, then a fresh session. Old session files are renamed with a timestamp.

### Double-click launchers (Windows)

Pin these to your taskbar or desktop if you like:

| File | When to use it |
|---|---|
| `go.cmd` | “How am I doing?” — risk, TODO count, last sync |
| `sync-now.cmd` | Rescue notes **now** (don’t wait for 9 PM) |
| `find-notes.cmd` | Search vault, pick a result, open in Notepad++ |
| `todos.cmd` | Refresh and open your TODO list (`todos.cmd apply` after checking items off) |
| `reset-npp.cmd` | Sync + clean Notepad++ session |
| `doctor.cmd` | Quick health check |
| `inbox.cmd` | Open `vault/Inbox/` |
| `privacy-check.cmd` | Before pushing this repo to public GitHub |
| `scholar.cmd` | scholar meeting prep (optional; needs local config) |
| `ask.cmd` | Ask AI about your rescued notes (local vault search) |
| `site.cmd` | Build a reviewed public personal website |

### Command-line shortcuts

```powershell
python main.py go                          # dashboard
python main.py workflows                   # quick-reference guide
python main.py find "student travel funds"   # search + open (add --pick to choose)
python main.py sync                        # backup + import + todos
python main.py doctor                      # health check
python main.py open todos                  # global TODO file
python main.py today                       # notes rescued today
python main.py recent                      # last 7 days
python main.py inbox                       # open Inbox
python main.py ask "what was I working on?"  # AI answers from your vault
```

**Auto-reset:** when you have **100+** unsaved tabs and sync has already imported everything new, sync can automatically reset Notepad++ (see `config/settings.json`).

---

## What it does

- Backs up `%APPDATA%\Notepad++\backup` and `session.xml`
- Imports unsaved backup files into `vault/` as Markdown with YAML frontmatter
- **Persistent deduplication** via `data/state.json` (rebuilt from vault on each sync)
- Keyword-based classification (`config/categories.json`)
- Global TODO extraction to `vault/TODO/global_todos.md` (with dismiss / check-off workflow)
- **Search** with phrase ranking and all-terms boosting
- **Safe session reset** (`reset` / `reset-npp.cmd`)
- **Windows toasts** after sync
- Scheduled daily sync, smoke test, privacy check, cleanup reports
- Optional **scholar** profiles and handoff summaries (`config/scholars.json`)

Optional **AI ask** (`ask.cmd`): searches your vault, sends the best-matching excerpts to OpenAI, and answers in plain English — useful when keyword search is not enough and you need a quick summary of what you wrote.

---

## Ask your notes (AI vault search)

For “what was I doing about X?” when you do not remember which file it is in:

### One-time API key setup

```powershell
copy config\secrets.example.json config\secrets.local.json
# Edit secrets.local.json and paste your OpenAI API key (this file is gitignored)
```

Or set `OPENAI_API_KEY` in your environment. Never commit `config/secrets.local.json`.

### Daily use (lazy)

1. Double-click **`ask.cmd`**.
2. Type a question in plain English, e.g. `What did I write about student travel funds?`
3. Read the answer; source note paths are listed under it.

**Fix shorthand the AI misread:** in the ask window, type:

```text
correct: When I wrote "TESC funds" I meant the travel scholarship deadline
```

Or from the command line:

```powershell
python main.py ask correct "When I wrote TESC I meant travel scholarship"
python main.py ask corrections   # list saved clarifications
```

Corrections are stored in `data/chat_corrections.json` (gitignored) and included in future answers.

**Open the source note:** after an answer, type `open` in the ask window, or run `python main.py ask "your question" --open`.

How it works: your question is matched against the vault using the same search as `find`, then the top note excerpts plus your corrections go to OpenAI (`gpt-4o-mini` by default). Answers only use what is in those excerpts — if nothing matches, it will say so honestly.

---

## Personal website (hiring + UCSD intro, privacy-safe)

You **can** use note-rescue to help build a public site about you (projects, values, quotes, reading list, math/physics/engineering/CS breadth) — but **not** by publishing your vault or raw `ask` answers.

| Tool | Private or public? |
|------|-------------------|
| `ask.cmd` | **Private** — memory helper only |
| `site.cmd` | **Public** — drafts with redaction rules, you review before deploy |

**Golden rule:** Only upload `site/dist/` after you read the draft and `site review` passes.

### Lazy workflow

1. Double-click **`site.cmd`** → choose **1** (first-time setup).
2. Edit `config/site.profile.public.json` (name, tagline, GitHub/LinkedIn — only what you want on the web).
3. Optionally copy resume blurbs or project summaries into `site/sources/` as `.md` files.
4. **Draft from notes:** `site.cmd` → **2**, or `python main.py site draft projects`.
5. **Review draft:** `site.cmd` → **3** — opens `site/drafts/draft-*.json`; delete anything too personal.
6. **Publish + build:** `site.cmd` → **4**, or `python main.py site publish` then `site build`.
7. **Review:** `site.cmd` → **5** — blocks emails, phone numbers, and UCSD PIDs in the built site.
8. Upload **only** `site/dist/` to GitHub Pages, Netlify, etc.

The template is a lightweight single page (light/dark theme, cards for projects and reading). Use `ask` when you need to *search* what you wrote; use `site draft` when you need *publishable* copy.

Details: [site/README.md](site/README.md)

---

## Configuration

`config/settings.json`:

| Key | Default | Meaning |
|---|---|---|
| `auto_reset_threshold` | `100` | Tab count before auto-reset is considered |
| `auto_reset_after_sync` | `true` | Reset after sync when threshold met and nothing new to import |
| `notify_after_sync` | `true` | Windows toast after sync |
| `default_open_target` | `notepad++` | Default app for `open` / `find` |
| `recent_days_default` | `7` | Window for `recent` command |
| `sync_schedule_hour` | `21` | Hour for scheduled task (9 PM) |

`config/secrets.local.json` (gitignored, copy from `secrets.example.json`):

| Key | Default | Meaning |
|---|---|---|
| `openai_api_key` | (required for ask) | Your OpenAI API key |
| `openai_model` | `gpt-4o-mini` | Chat model |
| `chat_max_notes` | `10` | Max vault notes sent as context |
| `chat_max_chars_per_note` | `6000` | Truncate each note excerpt |

---

## Project layout

```text
note-rescue/
├── main.py                 # CLI entry
├── setup.ps1               # one-time setup
├── *.cmd                   # double-click launchers
├── config/
│   ├── categories.json
│   ├── settings.json
│   ├── scholars.example.json
│   └── secrets.example.json   # copy to secrets.local.json (gitignored)
├── data/                   # backups, state, reports (gitignored)
├── vault/                  # rescued Markdown notes (gitignored by default)
└── src/note_rescue/        # Python package
```

Vault categories include `Inbox`, `School`, `Projects`, `TESC`, `AISC`, `Research`, `Personal`, `Tech_Debugging`, `ChatGPT`, `TODO`, and `Archive`. Unmatched notes land in **Inbox**.

---

## Manual setup (if you skip setup.ps1)

Python **3.12** or **3.11** recommended.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py smoke-test
```

Register the daily task:

```powershell
.\schedule_task_daily.ps1
```

---

## Core commands

Run from the project root with the venv activated (or use `.venv\Scripts\python.exe` directly).

| Command | Purpose |
|---|---|
| `sync` | Backup → import new only → TODOs → cleanup report → refresh README stats |
| `backup` | Copy Notepad++ backup folder and session only |
| `import` | Import backups into `vault/` |
| `todos` | Regenerate `vault/TODO/global_todos.md` |
| `todos-apply` | Permanently dismiss `- [x]` items from global TODOs |
| `search` / `find` | Search vault (`find` opens top hit; `--pick` to choose) |
| `reset` | Preview or apply safe Notepad++ session reset |
| `status` / `doctor` / `go` | Health and lazy dashboard |
| `recent` / `today` | Recently imported notes |
| `open vault\|inbox\|todos` | Open in Notepad++, VS Code, or Explorer |
| `privacy-check` | Scan tracked files before a public push |
| `ask "question"` | Ask OpenAI about your vault (needs `secrets.local.json`) |
| `ask correct "..."` | Save a clarification for messy notes |
| `ask corrections` | List saved clarifications |

Example import output:

```text
Files seen: 2510
Imported: 1970
Skipped empty: 533
Skipped duplicates: 7
```

Each note file includes frontmatter (`source`, `imported_at`, `category`, `sha256`, etc.) for dedup and search.

---

## TODO workflow (lazy cleanup)

1. Run `todos.cmd` (or `python main.py todos --open`).
2. In Notepad++, change `- [ ]` to `- [x]` for done or irrelevant items.
3. Run `todos.cmd apply` (or `python main.py todos-apply`).
4. Checked items are dismissed permanently and won’t reappear after sync.

---

## Resetting Notepad++

**Easiest:** `reset-npp.cmd` (sync + reset with `--kill-notepadpp`).

**CLI:**

```powershell
python main.py reset              # preview
python main.py reset --apply --kill-notepadpp
```

Renames `session.xml` and `backup/` with a timestamp, then creates a fresh empty `backup/` folder.

---

## Where files live

| Location | Contents |
|---|---|
| `%APPDATA%\Notepad++\backup` | Unsaved tab backups (source) |
| `%APPDATA%\Notepad++\session.xml` | Open session |
| `data/raw_backups/` | Copied backups per run |
| `vault/` | Rescued `.md` notes |
| `data/state.json` | Import dedup hashes |

---

## Safety

1. Run `backup` or `sync` before resetting Notepad++.
2. Confirm notes appear under `vault/` and search works.
3. Do **not** commit `vault/` or `data/raw_backups/` to a **public** repo without reviewing contents.
4. Use `privacy-check.cmd` before pushing.

---

## Troubleshooting

**`ModuleNotFoundError: note_rescue`** — Run `python main.py …` from the project root (where `main.py` lives), not `python -m src.main`.

**PowerShell won’t activate venv** — `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then retry.

**Notepad++ still slow after import** — Import copies notes to `vault/`; it does not close open tabs. Use `reset-npp.cmd` or `python main.py reset --apply`.

**Scheduled sync failed** — Check `data/logs/sync_*.log` for the error message.

**Not sure which launcher to use** — Double-click `workflows.cmd` or run `python main.py workflows`.

**Search feels broad** — Use more specific words or `find --pick`. Phrase matches and all-term hits rank highest.

---

## Philosophy

> Don’t ask a busy person to manually organize thousands of notes before they can be productive again.

Rescue first, classify roughly, extract obvious action items, search immediately, clean gradually.

---

## Auto-generated project reference

<!-- AUTO-GENERATED:START -->

> This section is automatically generated. Do not edit this section by hand.

Last updated: `2026-05-31T12:47:59`

### Available CLI commands

| Command | Purpose |
|---|---|
| `python main.py backup` | Back up Notepad++ session and unsaved backup files. |
| `python main.py import` | Import Notepad++ backup files into the Markdown vault. |
| `python main.py todos` | Extract TODOs from the vault into `vault/TODO/global_todos.md`. |
| `python main.py search "query"` | Search imported Markdown notes. |
| `python main.py status` | Show Notepad++ and vault health status. |
| `python main.py sync` | Back up, import new notes, and extract TODOs. |
| `python main.py doctor` | Diagnose whether Notepad++ is accumulating too many unsaved tabs. |
| `python main.py update-readme` | Refresh this auto-generated README section. |
| `python main.py go` | Lazy dashboard — status, todos, next steps. |
| `python main.py workflows [--open]` | One-page workflow quick reference. |
| `python main.py find "query"` | Search and open top result in Notepad++. |
| `python main.py reset [--apply]` | Preview or perform safe Notepad++ session reset. |
| `python main.py open todos` | Open global TODO list. |
| `python main.py recent` | Notes imported in the last 7 days. |
| `python main.py today` | Notes imported today. |
| `python main.py inbox` | Open `vault/Inbox/` in your editor. |
| `python main.py todos-apply` | Dismiss checked `- [x]` items from global TODOs. |
| `python main.py cleanup-report` | Generate a non-destructive cleanup report. |
| `python main.py rebuild-state` | Rebuild import dedup state from vault frontmatter. |
| `python main.py smoke-test` | Basic project health checks. |
| `python main.py privacy-check` | Scan tracked files before a public git push. |
| `python main.py scholar list` | List PATHS scholars (local config). |
| `python main.py ask "question"` | Ask OpenAI about your vault notes (needs local API key). |
| `python main.py ask correct "..."` | Save a clarification for messy/shorthand notes. |
| `python main.py site draft` | Draft public site content from vault (review before deploy). |
| `python main.py site build` | Build static site to `site/dist/`. |

### Double-click launchers (Windows)

| File | What it does |
|---|---|
| `go.cmd` | Dashboard + next steps |
| `workflows.cmd` | Open workflow quick-reference guide |
| `sync-now.cmd` | Run sync now |
| `find-notes.cmd` | Interactive search |
| `todos.cmd` | Refresh + open TODOs (`todos.cmd apply` to clear checked items) |
| `reset-npp.cmd` | Sync then reset Notepad++ session |
| `doctor.cmd` | Health check |
| `inbox.cmd` | Open Inbox |
| `privacy-check.cmd` | Pre-push privacy scan |
| `scholar.cmd` | Scholar meeting prep |
| `ask.cmd` | Ask questions about your notes (AI) |
| `site.cmd` | Draft & build public personal site |

### Current Notepad++ health snapshot

| Metric | Value |
|---|---:|
| Risk level | `LOW` |
| Active Notepad++ backup files | `0` |
| Nonempty backup files | `0` |
| Empty backup files | `0` |
| Backup folder size | `0.0 MB` |
| Vault Markdown notes | `2091` |
| Known imported hashes | `2090` |

Health note: **Healthy. Notepad++ session size is manageable.**

### Vault note counts by category

| Category | Notes |
|---|---:|
| `AISC` | `29` |
| `Archive` | `0` |
| `ChatGPT` | `16` |
| `Inbox` | `722` |
| `Personal` | `136` |
| `Projects` | `364` |
| `Research` | `126` |
| `School` | `475` |
| `TESC` | `189` |
| `TODO` | `1` |
| `Tech_Debugging` | `33` |

### Configured classification categories

| Category | Keyword count |
|---|---:|
| `AISC` | `5` |
| `ChatGPT` | `6` |
| `Personal` | `8` |
| `Projects` | `12` |
| `Research` | `11` |
| `School` | `10` |
| `TESC` | `7` |
| `Tech_Debugging` | `13` |

### Persistent import state

| Metric | Value |
|---|---:|
| State file exists | `True` |
| Known imported hashes | `2090` |
| State last updated | `2026-05-31T12:47:58` |

<!-- AUTO-GENERATED:END -->
