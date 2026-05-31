from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .paths import VAULT_DIR


def parse_imported_at(text: str) -> datetime | None:
    match = re.search(
        r'^imported_at:\s*"?(\d{4}-\d{2}-\d{2}T[\d:]+)"?\s*$',
        text,
        flags=re.MULTILINE,
    )
    if not match:
        return None

    try:
        return datetime.fromisoformat(match.group(1))
    except ValueError:
        return None


def parse_category(text: str) -> str:
    match = re.search(r'^category:\s*"?([^"\n]+)"?\s*$', text, flags=re.MULTILINE)
    return match.group(1).strip() if match else "Unknown"


def note_title(path: Path) -> str:
    stem = path.stem
    parts = stem.split("_", 2)
    if len(parts) >= 2:
        return parts[1].replace("-", " ")
    return stem


def list_recent_notes(days: int = 7, limit: int = 30) -> list[dict[str, Any]]:
    if not VAULT_DIR.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    notes: list[dict[str, Any]] = []

    for path in VAULT_DIR.rglob("*.md"):
        if path.name == "global_todos.md":
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        imported_at = parse_imported_at(text)
        if imported_at is None:
            continue

        if imported_at < cutoff:
            continue

        notes.append(
            {
                "path": str(path),
                "rel_path": str(path.relative_to(VAULT_DIR)),
                "title": note_title(path),
                "category": parse_category(text),
                "imported_at": imported_at.isoformat(timespec="seconds"),
                "imported_dt": imported_at,
            }
        )

    notes.sort(key=lambda n: n["imported_dt"], reverse=True)
    return notes[:limit]


def list_today_notes(limit: int = 50) -> list[dict[str, Any]]:
    today = datetime.now().date()
    recent = list_recent_notes(days=2, limit=500)
    today_notes = [n for n in recent if n["imported_dt"].date() == today]
    return today_notes[:limit]
