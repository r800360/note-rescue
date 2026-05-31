from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .paths import DATA_DIR

CORRECTIONS_PATH = DATA_DIR / "chat_corrections.json"
MAX_CORRECTIONS = 200


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_corrections() -> list[dict[str, Any]]:
    if not CORRECTIONS_PATH.exists():
        return []

    try:
        with open(CORRECTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    return []


def save_corrections(rows: list[dict[str, Any]]) -> None:
    _ensure_data_dir()
    trimmed = rows[-MAX_CORRECTIONS:]
    with open(CORRECTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)


def add_correction(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        raise ValueError("Correction text cannot be empty.")

    row = {
        "text": text,
        "added_at": datetime.now().isoformat(timespec="seconds"),
    }
    rows = load_corrections()
    rows.append(row)
    save_corrections(rows)
    return row


def format_corrections_for_prompt(limit: int = 40) -> str:
    rows = load_corrections()
    if not rows:
        return ""

    lines = [
        "The user added these clarifications about their messy or shorthand notes. "
        "Treat these as authoritative when they apply:",
    ]
    for row in rows[-limit:]:
        lines.append(f"- {row['text']}")
    return "\n".join(lines)
