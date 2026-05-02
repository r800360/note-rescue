# note-rescue

A local-first rescue and organization tool for recovering large Notepad++ unsaved-tab sessions into real Markdown files.

This project was created to solve a specific recurring productivity problem:

> Notepad++ becomes slow or unusable because thousands of unsaved tabs accumulate over time, but those tabs contain important notes, TODOs, project fragments, school work, debugging logs, and personal reminders that should not be lost.

`note-rescue` safely backs up the Notepad++ session, imports unsaved backup files into a structured Markdown vault, classifies notes into rough categories, extracts TODOs, and provides basic search.

The project is intentionally non-destructive by default.

---

## Current status

The current version supports:

- Backing up Notepad++ unsaved-tab data
- Importing Notepad++ backup files into Markdown notes
- Deduplicating notes within one import run
- Skipping empty notes
- Categorizing notes using keyword-based rules
- Extracting TODOs into a global TODO file
- Searching imported notes from the command line

It does **not yet** support:

- Persistent deduplication across multiple import runs
- Semantic/vector search
- Web UI dashboard
- Automatic Notepad++ cleanup
- Automatic deletion of old Notepad++ backup files
- Full note merging/summarization

---

## Why this exists

Notepad++ is useful as a scratchpad, but it is not a long-term knowledge management system. If hundreds or thousands of unsaved tabs are left open, Notepad++ can become slow to start or fail to open reliably.

This project turns those fragile unsaved tabs into real Markdown files that can be opened, searched, backed up, and organized using tools such as:

- VSCode
- Obsidian
- Notepad++
- Windows Search
- Git, if used carefully with private data
- Any plain-text editor

The intended workflow is:

```text
Notepad++ unsaved tabs
        ↓
note-rescue backup/import
        ↓
Markdown vault
        ↓
VSCode / Obsidian / organized folders
        ↓
fast search + TODO extraction + cleanup
```

---

## Recommended Python version

Use Python 3.12 if available.

Python 3.11 is also fine.

Avoid Python 3.13 for now unless all dependencies install correctly, because newer Python versions can sometimes have package compatibility issues.

Check your Python version:

```powershell
python --version
```

or:

```powershell
py --version
```

Recommended virtual environment creation:

```powershell
py -3.12 -m venv .venv
```

If Python 3.12 is unavailable, use:

```powershell
py -3.11 -m venv .venv
```

---

## Project structure

Recommended structure:

```text
note-rescue/
├── README.md
├── requirements.txt
├── main.py
├── config/
│   └── categories.json
├── data/
│   ├── raw_backups/
│   ├── exported_notes/
│   ├── indexes/
│   └── reports/
├── src/
│   └── note_rescue/
│       ├── __init__.py
│       ├── paths.py
│       ├── backup.py
│       ├── importer.py
│       ├── classifier.py
│       ├── todo_extractor.py
│       ├── search.py
│       └── cli.py
└── vault/
    ├── Inbox/
    ├── ChatGPT/
    ├── School/
    ├── Projects/
    ├── TESC/
    ├── AISC/
    ├── Research/
    ├── Personal/
    ├── Tech_Debugging/
    ├── TODO/
    └── Archive/
```

---

## Setup

From PowerShell:

```powershell
cd C:\Users\bsach\Documents\note-rescue
```

Create the virtual environment:

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

If activation is blocked by PowerShell execution policy, use:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Requirements

Current `requirements.txt`:

```text
rich==13.9.4
```

`rich` is used for nicer terminal output.

---

## Main commands

Run commands from the project root:

```powershell
cd C:\Users\bsach\Documents\note-rescue
.\.venv\Scripts\Activate.ps1
```

### 1. Back up Notepad++

```powershell
python main.py backup
```

This copies Notepad++'s backup folder and session file into:

```text
data/raw_backups/
```

Example output:

```text
Backup Complete
Backed up Notepad++ files to:
C:\Users\bsach\Documents\note-rescue\data\raw_backups\notepadpp_backup_2026-05-02_11-44-59
```

This command is non-destructive.

It does not delete, rename, or modify Notepad++ files.

---

### 2. Import notes

```powershell
python main.py import
```

This reads Notepad++ unsaved backup files, skips empty notes, removes duplicates within the current run, classifies notes, and writes Markdown files into:

```text
vault/
```

Example output:

```text
Import Complete
Files seen: 2510
Imported: 1970
Skipped empty: 533
Skipped duplicates: 7
```

Example category output:

```text
Category        Count
AISC             29
ChatGPT          15
Inbox           694
Personal        132
Projects        338
Research         99
School          450
TESC            181
Tech_Debugging   32
```

Important:

The current importer deduplicates notes within one import run only. It does not yet check whether the same notes were imported in a previous run.

So avoid running `import` repeatedly until persistent deduplication is added.

---

### 3. Extract TODOs

```powershell
python main.py todos
```

This scans the Markdown vault and writes extracted TODOs to:

```text
vault/TODO/global_todos.md
```

Example output:

```text
TODO Extraction Complete
Extracted 42 TODOs into:
C:\Users\bsach\Documents\note-rescue\vault\TODO\global_todos.md
```

TODO patterns currently recognized include lines like:

```text
TODO: finish assignment
Todo - email professor
todo update project plan
Action item: submit reimbursement
Need to call Dell support
Remember to back up WSL projects
- [ ] clean Notepad++ session
```

---

### 4. Search notes

```powershell
python main.py search "Dell freezing"
```

Other examples:

```powershell
python main.py search "CSE 252D"
python main.py search "student travel funds"
python main.py search "Notepad++"
python main.py search "loma reverse mode"
python main.py search "Costco pizza"
```

You can limit results:

```powershell
python main.py search "Dell freezing" --limit 5
```

Current search is simple keyword counting. It is useful but not perfect.

For example, searching:

```text
Dell freezing
```

may return notes that contain `Dell`, notes that contain `freezing`, or notes that contain both. Future versions should rank notes containing all query terms higher.

---

## Auto-generated project reference

<!-- AUTO-GENERATED:START -->

> This section is automatically generated. Do not edit this section by hand.

Last updated: `2026-05-02T15:38:35`

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

### Current Notepad++ health snapshot

| Metric | Value |
|---|---:|
| Risk level | `LOW` |
| Active Notepad++ backup files | `2` |
| Nonempty backup files | `1` |
| Empty backup files | `1` |
| Backup folder size | `0.0 MB` |
| Vault Markdown notes | `1973` |
| Known imported hashes | `1972` |

Health note: **Healthy. Notepad++ session size is manageable.**

### Vault note counts by category

| Category | Notes |
|---|---:|
| `AISC` | `29` |
| `Archive` | `0` |
| `ChatGPT` | `15` |
| `Inbox` | `694` |
| `Personal` | `132` |
| `Projects` | `339` |
| `Research` | `99` |
| `School` | `451` |
| `TESC` | `181` |
| `TODO` | `1` |
| `Tech_Debugging` | `32` |

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
| Known imported hashes | `1972` |
| State last updated | `2026-05-02T15:38:34` |

<!-- AUTO-GENERATED:END -->

## Recommended emergency rescue workflow

Use this when Notepad++ is overloaded and will not start properly.

### Step 1: Run backup

```powershell
python main.py backup
```

### Step 2: Run import

```powershell
python main.py import
```

### Step 3: Extract TODOs

```powershell
python main.py todos
```

### Step 4: Check the vault

Open the vault in VSCode:

```powershell
code C:\Users\bsach\Documents\note-rescue\vault
```

Or open it in File Explorer:

```powershell
explorer C:\Users\bsach\Documents\note-rescue\vault
```

Check these folders first:

```text
vault/Inbox/
vault/School/
vault/Projects/
vault/TESC/
vault/Tech_Debugging/
vault/TODO/global_todos.md
```

### Step 5: Reset Notepad++ active session safely

Only do this after confirming that `backup` and `import` worked.

Close Notepad++:

```powershell
taskkill /F /IM notepad++.exe
```

Go to the Notepad++ configuration folder:

```powershell
cd "$env:APPDATA\Notepad++"
```

Rename the active session:

```powershell
Rename-Item session.xml session_rescued_2026-05-02.xml
```

Rename the active backup folder:

```powershell
Rename-Item backup backup_rescued_2026-05-02
```

Create a fresh empty backup folder:

```powershell
mkdir backup
```

Now open Notepad++ normally.

It should no longer attempt to load the old thousands-tab session.

---

## One-shot Notepad++ reset command

Use only after confirming your notes were backed up and imported.

```powershell
taskkill /F /IM notepad++.exe

cd "$env:APPDATA\Notepad++"

if (Test-Path session.xml) {
    Rename-Item session.xml session_rescued_2026-05-02.xml
}

if (Test-Path backup) {
    Rename-Item backup backup_rescued_2026-05-02
}

mkdir backup
```

This does not delete the old session. It renames it so Notepad++ starts cleanly.

---

## Where Notepad++ stores unsaved tabs

Usually:

```text
%APPDATA%\Notepad++\backup
```

Expanded example:

```text
C:\Users\bsach\AppData\Roaming\Notepad++\backup
```

The session file is usually:

```text
%APPDATA%\Notepad++\session.xml
```

Expanded example:

```text
C:\Users\bsach\AppData\Roaming\Notepad++\session.xml
```

`note-rescue` reads from these locations.

---

## Where rescued notes go

Markdown notes are written to:

```text
vault/
```

Example:

```text
vault/Tech_Debugging/2026-05-02_dell-inspiron-freezing-sleep-notepad-problem_ab12cd34ef.md
vault/School/2026-05-02_cse-252d-project-plan_123456abcd.md
vault/TESC/2026-05-02_student-travel-funds-email_9876fedcba.md
```

Each generated note includes YAML-style frontmatter:

```yaml
---
source: "notepad++ unsaved backup"
original_file: "C:\\Users\\bsach\\AppData\\Roaming\\Notepad++\\backup\\..."
imported_at: "2026-05-02T11:44:59"
category: "Tech_Debugging"
sha256: "..."
todo_count: "2"
classifier_scores: {"ChatGPT": 0, "School": 1, "Projects": 0}
---
```

This metadata makes later cleanup, deduplication, and search easier.

---

## Category system

Categories are configured in:

```text
config/categories.json
```

Example categories:

```text
ChatGPT
School
Projects
TESC
AISC
Research
Tech_Debugging
Personal
Inbox
```

`Inbox` is the fallback category.

If a note does not strongly match any category, it goes to:

```text
vault/Inbox/
```

This is expected. The classifier is intentionally conservative and simple.

---

## Suggested cleanup strategy

After importing, do not try to clean everything at once.

Use this order:

### 1. Check `TODO/global_todos.md`

Start here because it contains actionable items.

```text
vault/TODO/global_todos.md
```

### 2. Check high-value categories

Recommended first pass:

```text
vault/School/
vault/Projects/
vault/TESC/
vault/Tech_Debugging/
```

### 3. Leave `Inbox` for later

`Inbox` may be large. That is okay.

You can process it gradually.

Suggested rule:

```text
Each day, clean 10–20 Inbox notes.
```

### 4. Archive instead of deleting

When unsure, move notes to:

```text
vault/Archive/
```

rather than deleting them.

---

## Recommended daily workflow going forward

The goal is to stop rebuilding another 2000-tab Notepad++ session.

Suggested workflow:

```text
Quick thought → vault/Inbox/
Task → vault/TODO/global_todos.md or a project-specific TODO
School → vault/School/
Project notes → vault/Projects/
Laptop/debugging → vault/Tech_Debugging/
TESC admin → vault/TESC/
AISC admin → vault/AISC/
Long-term old note → vault/Archive/
```

Use Notepad++ only as a short-term scratchpad.

A good rule:

```text
Never let Notepad++ exceed 50 unsaved tabs.
```

Even better:

```text
At the end of each day, save or discard scratch tabs.
```

---

## Recommended `.gitignore`

If you use Git, do not accidentally commit private notes or raw backups unless you are intentionally using a private encrypted workflow.

Recommended `.gitignore`:

```gitignore
.venv/
__pycache__/
*.pyc

data/raw_backups/
data/indexes/
data/reports/

# Usually keep private:
vault/
```

If you want to track the code but not your notes, keep `vault/` ignored.

If you want to version your notes, use a private repo and consider excluding sensitive folders.

---

## Safety warnings

### Do not delete Notepad++ backups immediately

First confirm:

1. `python main.py backup` completed
2. `python main.py import` completed
3. Rescued notes exist in `vault/`
4. Important notes are searchable
5. `data/raw_backups/` contains a full backup

Only then consider resetting the Notepad++ active session.

### Avoid repeatedly running import

The current importer does not yet persistently deduplicate across separate import runs.

If you run:

```powershell
python main.py import
```

multiple times, it may create duplicate Markdown notes in `vault/`.

This should be fixed in a future version.

### Do not commit raw backups publicly

The raw backup folder may contain personal, academic, financial, logistical, or sensitive notes.

Never upload it to a public GitHub repository.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'note_rescue'`

This usually means Python cannot find the `src/note_rescue` package.

The simple fix used in this project is to keep `main.py` in the project root and insert `src/` into `sys.path`.

Your structure should look like:

```text
note-rescue/
├── main.py
└── src/
    └── note_rescue/
```

Run:

```powershell
python main.py backup
```

Do not run:

```powershell
python -m src.main backup
```

unless the project has been packaged differently.

---

### PowerShell cannot activate venv

If this fails:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then try again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### Notepad++ still opens slowly after import

Importing notes does not automatically reset Notepad++.

You still need to rename the active Notepad++ session and backup folder:

```powershell
taskkill /F /IM notepad++.exe
cd "$env:APPDATA\Notepad++"
Rename-Item session.xml session_rescued_2026-05-02.xml
Rename-Item backup backup_rescued_2026-05-02
mkdir backup
```

Then reopen Notepad++.

---

### Search results seem unrelated

Current search is basic. It counts individual query terms.

So a query like:

```text
Dell freezing
```

may return notes that contain only `Dell` or only `freezing`.

Future improvements should include:

- ranking notes containing all query terms higher
- exact phrase matching
- BM25 search
- SQLite FTS5 search
- semantic embeddings

---

## Development roadmap

Recommended next improvements:

### Phase 1: Reliability

- Add persistent deduplication across runs
- Add `status` command
- Add `report` command
- Add dry-run mode for import
- Add better handling of file encodings
- Add safer reset command that prints exactly what it will rename

### Phase 2: Better search

- Require all search terms by default
- Add phrase search
- Add SQLite FTS5 index
- Add category filters
- Add date filters
- Add fuzzy search

Example future command:

```powershell
python main.py search "Dell freezing" --category Tech_Debugging --all-terms
```

### Phase 3: Organization tools

- Add `review-inbox` command
- Add `move` command
- Add automatic title improvement
- Add note summaries
- Add project-specific TODO extraction
- Add duplicate cluster reports

### Phase 4: Dashboard

Build a local web UI with:

- inbox review
- search
- category filters
- TODO dashboard
- duplicate detection
- recent imports
- cleanup progress

Possible stack:

```text
FastAPI backend
SQLite index
React or simple HTML frontend
```

### Phase 5: AI-assisted cleanup

Optional future features:

- local LLM summarization
- embedding search
- note clustering
- action-item extraction
- automatic project grouping
- stale-note detection

---

## Current successful rescue example

A successful run looked like:

```text
Files seen: 2510
Imported: 1970
Skipped empty: 533
Skipped duplicates: 7
```

Category breakdown:

```text
AISC             29
ChatGPT          15
Inbox           694
Personal        132
Projects        338
Research         99
School          450
TESC            181
Tech_Debugging   32
```

TODO extraction:

```text
Extracted 42 TODOs into:
vault/TODO/global_todos.md
```

This means the important rescue phase succeeded.

The next priority is to reset Notepad++'s active session so it no longer tries to reopen thousands of unsaved tabs.

---

## Philosophy

This project is designed around a simple principle:

> Do not ask a busy person to manually organize thousands of notes before they can become productive again.

Instead:

1. Rescue everything.
2. Convert it to durable plain text.
3. Classify roughly.
4. Extract obvious action items.
5. Make search available.
6. Clean gradually.

The goal is not perfect organization immediately.

The goal is to make the notes safe, searchable, and no longer capable of breaking Notepad++ or slowing down the computer.
