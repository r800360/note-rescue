"""Workflow helpers — next-step prompts and quick-reference text for the dashboard."""

from __future__ import annotations

import re
from pathlib import Path

from .paths import VAULT_DIR, PROJECT_ROOT
from .settings import load_settings
from .site_content import latest_draft_path
from .state import load_state
from .status import get_notepadpp_status, get_risk_level

WORKFLOWS_PATH = PROJECT_ROOT / "WORKFLOWS.md"
TODO_PATH = VAULT_DIR / "TODO" / "global_todos.md"


def count_open_todos(todo_path: Path = TODO_PATH) -> int:
    if not todo_path.exists():
        return 0
    text = todo_path.read_text(encoding="utf-8", errors="ignore")
    return text.count("- [ ]")


def count_checked_todos_pending_apply(todo_path: Path = TODO_PATH) -> int:
    """Checked items still in global_todos.md — user needs todos.cmd apply."""
    if not todo_path.exists():
        return 0
    text = todo_path.read_text(encoding="utf-8", errors="ignore")
    return len(re.findall(r"^\s*-\s*\[x\]", text, flags=re.IGNORECASE | re.MULTILINE))


def count_inbox_notes() -> int:
    inbox = VAULT_DIR / "Inbox"
    if not inbox.exists():
        return 0
    return len(list(inbox.rglob("*.md")))


def get_next_actions() -> list[str]:
    """Prioritized, actionable next steps for the dashboard."""
    status = get_notepadpp_status()
    risk, _ = get_risk_level(status["active_backup_files"])
    settings = load_settings()
    threshold = int(settings.get("auto_reset_threshold", 100))
    active = status["active_backup_files"]

    actions: list[str] = []

    checked = count_checked_todos_pending_apply()
    if checked:
        actions.append(
            f"{checked} checked TODO(s) waiting - run [cyan]todos.cmd apply[/cyan] to finish cleanup"
        )

    if active >= threshold:
        actions.append(
            f"{active} unsaved tabs (at or above {threshold}) - run [cyan]reset-npp.cmd[/cyan] after sync"
        )
    elif risk in {"HIGH", "VERY HIGH", "EMERGENCY"}:
        actions.append("[cyan]sync-now.cmd[/cyan] - rescue notes before Notepad++ slows down")
    elif active >= 50 and risk == "MODERATE":
        actions.append(
            f"{active} unsaved tabs building up - [cyan]sync-now.cmd[/cyan] when convenient"
        )
    elif active >= 30:
        state = load_state()
        if state.get("last_sync_at"):
            actions.append(
                f"Import saves notes to vault; it does not close Notepad++ tabs ({active} still open) - "
                "[cyan]reset-npp.cmd[/cyan] when you want a fresh session"
            )

    inbox = count_inbox_notes()
    vault_total = status["vault_notes"]
    if vault_total and inbox / vault_total >= 0.3 and inbox >= 50:
        actions.append(
            f"{inbox} notes in Inbox - run [cyan]find-notes.cmd[/cyan] or [cyan]ask.cmd[/cyan] to locate what you need"
        )

    draft = latest_draft_path()
    if draft and draft.exists():
        actions.append(
            f"Site draft ready for review - [cyan]site.cmd[/cyan] option 3, or open [dim]{draft.name}[/dim]"
        )

    open_todos = count_open_todos()
    if open_todos and not checked:
        actions.append(
            f"{open_todos} open TODO(s) - [cyan]todos.cmd[/cyan] to review (check off, then apply)"
        )

    return actions


def format_next_actions_panel() -> str | None:
    actions = get_next_actions()
    if not actions:
        return None

    lines = ["[bold]Next steps:[/bold]"]
    for i, action in enumerate(actions[:5], 1):
        lines.append(f"  {i}. {action}")
    return "\n".join(lines)
