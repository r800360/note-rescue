# note-rescue — workflow quick reference

One page: **what you want → what to run.** Pin `go.cmd` for status; open this file when you are not sure which launcher to use.

---

## Daily (almost nothing)

| Goal | Run |
|------|-----|
| Check status, TODOs, next steps | **`go.cmd`** |
| Rescue notes now (don't wait for scheduled sync) | **`sync-now.cmd`** |
| Find a note and open it | **`find-notes.cmd`** |
| Ask a plain-English question about your notes | **`ask.cmd`** |
| Notepad++ feels slow / too many tabs | **`reset-npp.cmd`** (syncs first, then fresh session) |

Scheduled sync runs automatically if you registered it during setup. You get a Windows toast when it finishes.

---

## TODO cleanup (3 steps — finish all three)

1. **`todos.cmd`** — refreshes the list and opens it in Notepad++
2. Change `- [ ]` to `- [x]` for done or irrelevant items, **save**
3. **`todos.cmd apply`** — permanently removes checked items

If you skip step 3, checked items stay in the file and reappear on the dashboard.

---

## Find something specific

| Situation | Run |
|-----------|-----|
| You remember a keyword or phrase | **`find-notes.cmd`** or `python main.py find "your words"` |
| You know the topic but not which file | **`ask.cmd`** — e.g. `What did I write about travel funds?` |
| Notes from today | `python main.py today` |
| Notes from the last week | `python main.py recent` |
| Browse uncategorized notes | **`inbox.cmd`** |

**ask.cmd special commands** (inside the ask window):

- `correct: I meant …` — fix shorthand the AI misread
- `corrections` — list saved clarifications
- `open` — open the top source note from the last answer

---

## Notepad++ health

| Situation | Run |
|-----------|-----|
| Quick check | **`doctor.cmd`** or **`go.cmd`** |
| Rescue + import new notes | **`sync-now.cmd`** |
| Fresh Notepad++ session (notes stay in vault/) | **`reset-npp.cmd`** |

**Important:** Sync **copies** notes into `vault/` — it does **not** close your open Notepad++ tabs. Use `reset-npp.cmd` when you want a clean session.

Auto-reset: when you have **100+** tabs and sync has imported everything new, sync may reset Notepad++ automatically (`config/settings.json`).

---

## Personal website (public — review before deploy)

| Step | Run |
|------|-----|
| Menu for the full pipeline | **`site.cmd`** |
| First-time profile setup | `site.cmd` → **1**, then edit `config/site.profile.public.json` |
| Draft from vault notes | `site.cmd` → **2** |
| Review the draft JSON | `site.cmd` → **3** (opens latest `site/drafts/draft-*.json`) |
| Publish + build | `site.cmd` → **4** |
| Privacy scan before upload | `site.cmd` → **5** |
| Preview in browser | `site.cmd` → **6** |

**Private vs public**

| Tool | Scope |
|------|--------|
| **`ask.cmd`** | **Private** — local vault only, never published |
| **`site.cmd`** | **Public** — only upload `site/dist/` after you review the draft and `site review` passes |

Details: [site/README.md](site/README.md)

---

## Before pushing this repo to GitHub

1. **`privacy-check.cmd`** — scan tracked files for emails, phones, keys
2. Never commit `vault/`, `data/`, or `config/secrets.local.json`

---

## Optional: scholar meeting prep

1. Run `setup-scholars.ps1` once
2. **`scholar.cmd`** or `python main.py scholar show "Name" --topic "…"`

---

## Command-line equivalents

All launchers map to `python main.py <command>` from the project root:

```powershell
python main.py go              # dashboard
python main.py workflows       # this guide in the terminal
python main.py sync            # backup + import + TODOs
python main.py find "query"    # search + open top hit
python main.py ask "question"  # AI answers from vault
python main.py todos --open    # same as todos.cmd
python main.py todos-apply     # same as todos.cmd apply
python main.py reset --apply   # reset (reset-npp.cmd also syncs first)
```

---

## When something goes wrong

| Problem | Fix |
|---------|-----|
| Scheduled sync failed | Check logs in `data/logs/sync_*.log` |
| Notepad++ slow after sync | Run **`reset-npp.cmd`** — import does not clear open tabs |
| Search too many results | Use more specific words, or `find --pick` to choose |
| ask.cmd says no API key | Copy `config/secrets.example.json` → `config/secrets.local.json` |
| ModuleNotFoundError | Run commands from the folder that contains `main.py` |

Full troubleshooting: [README.md](README.md#troubleshooting)
