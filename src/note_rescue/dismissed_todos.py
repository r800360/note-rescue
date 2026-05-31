from __future__ import annotations

import json
import re
from datetime import datetime

from .paths import DATA_DIR

DISMISSED_PATH = DATA_DIR / "dismissed_todos.json"


def normalize_todo(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def load_dismissed() -> dict:
    if not DISMISSED_PATH.exists():
        return {"dismissed": {}}

    try:
        with open(DISMISSED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {"dismissed": {}}

    if not isinstance(data, dict):
        return {"dismissed": {}}

    data.setdefault("dismissed", {})
    return data


def save_dismissed(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    with open(DISMISSED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def is_dismissed(todo_text: str) -> bool:
    key = normalize_todo(todo_text)
    return key in load_dismissed().get("dismissed", {})


def dismiss_todo(todo_text: str, reason: str = "dismissed") -> bool:
    key = normalize_todo(todo_text)
    if not key:
        return False

    data = load_dismissed()
    data["dismissed"][key] = {
        "text": todo_text.strip(),
        "reason": reason,
        "dismissed_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_dismissed(data)
    return True


def dismiss_many(todo_texts: list[str], reason: str = "dismissed") -> int:
    count = 0
    for text in todo_texts:
        if dismiss_todo(text, reason=reason):
            count += 1
    return count


def dismissed_count() -> int:
    return len(load_dismissed().get("dismissed", {}))
