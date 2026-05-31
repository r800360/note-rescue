from pathlib import Path
from datetime import datetime
import json

from .paths import PROJECT_ROOT, VAULT_DIR, CATEGORIES_PATH, DATA_DIR
from .status import get_notepadpp_status, get_risk_level

README_PATH = PROJECT_ROOT / "README.md"

START_MARKER = "<!-- AUTO-GENERATED:START -->"
END_MARKER = "<!-- AUTO-GENERATED:END -->"


def count_vault_notes_by_category() -> dict[str, int]:
    counts = {}

    if not VAULT_DIR.exists():
        return counts

    for category_dir in VAULT_DIR.iterdir():
        if category_dir.is_dir():
            counts[category_dir.name] = len(list(category_dir.rglob("*.md")))

    return dict(sorted(counts.items()))


def load_categories() -> dict:
    if not CATEGORIES_PATH.exists():
        return {}

    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_state_summary() -> dict:
    state_path = DATA_DIR / "state.json"

    if not state_path.exists():
        return {
            "state_exists": False,
            "known_imported_hashes": 0,
            "updated_at": "N/A",
        }

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    return {
        "state_exists": True,
        "known_imported_hashes": len(state.get("imported_hashes", {})),
        "updated_at": state.get("updated_at", "N/A"),
    }


def generate_auto_section() -> str:
    status = get_notepadpp_status()
    risk, risk_message = get_risk_level(status["active_backup_files"])
    category_counts = count_vault_notes_by_category()
    categories = load_categories()
    state_summary = get_state_summary()

    lines = []

    lines.append(START_MARKER)
    lines.append("")
    lines.append(
        "> This section is automatically generated. Do not edit this section by hand."
    )
    lines.append("")
    lines.append(f"Last updated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append("")

    lines.append("### Available CLI commands")
    lines.append("")
    lines.append("| Command | Purpose |")
    lines.append("|---|---|")
    lines.append(
        "| `python main.py backup` | Back up Notepad++ session and unsaved backup files. |"
    )
    lines.append(
        "| `python main.py import` | Import Notepad++ backup files into the Markdown vault. |"
    )
    lines.append(
        "| `python main.py todos` | Extract TODOs from the vault into `vault/TODO/global_todos.md`. |"
    )
    lines.append(
        '| `python main.py search "query"` | Search imported Markdown notes. |'
    )
    lines.append(
        "| `python main.py status` | Show Notepad++ and vault health status. |"
    )
    lines.append(
        "| `python main.py sync` | Back up, import new notes, and extract TODOs. |"
    )
    lines.append(
        "| `python main.py doctor` | Diagnose whether Notepad++ is accumulating too many unsaved tabs. |"
    )
    lines.append(
        "| `python main.py update-readme` | Refresh this auto-generated README section. |"
    )
    lines.append(
        "| `python main.py go` | Lazy dashboard — status, todos, quick commands. |"
    )
    lines.append(
        '| `python main.py find "query"` | Search and open top result in Notepad++. |'
    )
    lines.append(
        "| `python main.py reset [--apply]` | Preview or perform safe Notepad++ session reset. |"
    )
    lines.append(
        "| `python main.py open todos` | Open global TODO list. |"
    )
    lines.append(
        "| `python main.py recent` | Notes imported in the last 7 days. |"
    )
    lines.append(
        "| `python main.py today` | Notes imported today. |"
    )
    lines.append(
        "| `python main.py inbox` | Open `vault/Inbox/` in your editor. |"
    )
    lines.append(
        "| `python main.py todos-apply` | Dismiss checked `- [x]` items from global TODOs. |"
    )
    lines.append(
        "| `python main.py cleanup-report` | Generate a non-destructive cleanup report. |"
    )
    lines.append(
        "| `python main.py rebuild-state` | Rebuild import dedup state from vault frontmatter. |"
    )
    lines.append(
        "| `python main.py smoke-test` | Basic project health checks. |"
    )
    lines.append(
        "| `python main.py privacy-check` | Scan tracked files before a public git push. |"
    )
    lines.append(
        "| `python main.py scholar list` | List PATHS scholars (local config). |"
    )
    lines.append(
        '| `python main.py ask "question"` | Ask OpenAI about your vault notes (needs local API key). |'
    )
    lines.append(
        '| `python main.py ask correct "..."` | Save a clarification for messy/shorthand notes. |'
    )
    lines.append(
        "| `python main.py site draft` | Draft public site content from vault (review before deploy). |"
    )
    lines.append(
        "| `python main.py site build` | Build static site to `site/dist/`. |"
    )
    lines.append("")
    lines.append("### Double-click launchers (Windows)")
    lines.append("")
    lines.append("| File | What it does |")
    lines.append("|---|---|")
    lines.append("| `go.cmd` | Dashboard |")
    lines.append("| `sync-now.cmd` | Run sync now |")
    lines.append("| `find-notes.cmd` | Interactive search |")
    lines.append("| `todos.cmd` | Refresh + open TODOs (`todos.cmd apply` to clear checked items) |")
    lines.append("| `reset-npp.cmd` | Sync then reset Notepad++ session |")
    lines.append("| `doctor.cmd` | Health check |")
    lines.append("| `inbox.cmd` | Open Inbox |")
    lines.append("| `privacy-check.cmd` | Pre-push privacy scan |")
    lines.append("| `scholar.cmd` | Scholar meeting prep |")
    lines.append("| `ask.cmd` | Ask questions about your notes (AI) |")
    lines.append("| `site.cmd` | Draft & build public personal site |")
    lines.append("")

    lines.append("### Current Notepad++ health snapshot")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Risk level | `{risk}` |")
    lines.append(
        f"| Active Notepad++ backup files | `{status['active_backup_files']}` |"
    )
    lines.append(f"| Nonempty backup files | `{status['nonempty_backup_files']}` |")
    lines.append(f"| Empty backup files | `{status['empty_backup_files']}` |")
    lines.append(f"| Backup folder size | `{status['backup_size_mb']} MB` |")
    lines.append(f"| Vault Markdown notes | `{status['vault_notes']}` |")
    lines.append(f"| Known imported hashes | `{status['known_imported_hashes']}` |")
    lines.append("")
    lines.append(f"Health note: **{risk_message}**")
    lines.append("")

    lines.append("### Vault note counts by category")
    lines.append("")
    lines.append("| Category | Notes |")
    lines.append("|---|---:|")

    if category_counts:
        for category, count in category_counts.items():
            lines.append(f"| `{category}` | `{count}` |")
    else:
        lines.append("| N/A | `0` |")

    lines.append("")

    lines.append("### Configured classification categories")
    lines.append("")
    lines.append("| Category | Keyword count |")
    lines.append("|---|---:|")

    if categories:
        for category, keywords in sorted(categories.items()):
            lines.append(f"| `{category}` | `{len(keywords)}` |")
    else:
        lines.append("| N/A | `0` |")

    lines.append("")

    lines.append("### Persistent import state")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| State file exists | `{state_summary['state_exists']}` |")
    lines.append(
        f"| Known imported hashes | `{state_summary['known_imported_hashes']}` |"
    )
    lines.append(f"| State last updated | `{state_summary['updated_at']}` |")
    lines.append("")

    lines.append(END_MARKER)

    return "\n".join(lines)


def update_readme() -> Path:
    if not README_PATH.exists():
        README_PATH.write_text(
            "# note-rescue\n\n"
            "A local-first rescue and organization tool for Notepad++ notes.\n\n"
            "## Auto-generated project reference\n\n"
            f"{START_MARKER}\n"
            f"This section is automatically updated.\n"
            f"{END_MARKER}\n",
            encoding="utf-8",
        )

    old_text = README_PATH.read_text(encoding="utf-8")
    new_section = generate_auto_section()

    if START_MARKER not in old_text or END_MARKER not in old_text:
        old_text += (
            "\n\n## Auto-generated project reference\n\n"
            f"{START_MARKER}\n"
            "This section is automatically updated.\n"
            f"{END_MARKER}\n"
        )

    start = old_text.index(START_MARKER)
    end = old_text.index(END_MARKER) + len(END_MARKER)

    new_text = old_text[:start] + new_section + old_text[end:]

    README_PATH.write_text(new_text, encoding="utf-8")

    return README_PATH
