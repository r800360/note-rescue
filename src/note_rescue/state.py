from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict

from .paths import DATA_DIR, VAULT_DIR

STATE_PATH = DATA_DIR / "state.json"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def default_state() -> Dict[str, Any]:
    return {
        "version": 1,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "imported_hashes": {},
        "state_rebuilt_from_vault_at": None,
    }


def load_state() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return default_state()

    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        return default_state()

    if not isinstance(state, dict):
        return default_state()

    state.setdefault("version", 1)
    state.setdefault("created_at", now_iso())
    state.setdefault("updated_at", now_iso())
    state.setdefault("imported_hashes", {})
    state.setdefault("state_rebuilt_from_vault_at", None)

    return state


def save_state(state: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_iso()

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def has_imported_hash(digest: str) -> bool:
    digest = digest.lower()
    state = load_state()
    return digest in state.get("imported_hashes", {})


def mark_hash_imported(
    digest: str,
    markdown_file: str,
    original_file: str = "",
) -> None:
    digest = digest.lower()
    state = load_state()
    state.setdefault("imported_hashes", {})

    state["imported_hashes"][digest] = {
        "markdown_file": markdown_file,
        "original_file": original_file,
        "imported_at": now_iso(),
    }

    save_state(state)


def extract_sha256_from_markdown(text: str) -> str | None:
    """
    Reads sha256 from generated Markdown frontmatter.

    Supports lines like:
      sha256: "abc..."
      sha256: abc...
    """
    match = re.search(
        r'^sha256:\s*"?([a-fA-F0-9]{64})"?\s*$',
        text,
        flags=re.MULTILINE,
    )

    if not match:
        return None

    return match.group(1).lower()


def rebuild_state_from_vault() -> Dict[str, Any]:
    """
    Important for your current situation.

    You already imported many notes before persistent deduplication was guaranteed.
    This scans vault/*.md, reads sha256 frontmatter, and records those hashes so
    future scheduled syncs do not duplicate your already-imported notes.
    """
    state = load_state()
    state.setdefault("imported_hashes", {})

    rebuilt_count = 0
    scanned_notes = 0
    notes_with_hash = 0

    if VAULT_DIR.exists():
        for path in VAULT_DIR.rglob("*.md"):
            scanned_notes += 1

            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            digest = extract_sha256_from_markdown(text)

            if not digest:
                continue

            notes_with_hash += 1

            if digest not in state["imported_hashes"]:
                state["imported_hashes"][digest] = {
                    "markdown_file": str(path),
                    "original_file": "",
                    "imported_at": "rebuilt_from_existing_vault",
                }
                rebuilt_count += 1

    state["state_rebuilt_from_vault_at"] = now_iso()
    save_state(state)

    return {
        "state_path": str(STATE_PATH),
        "scanned_notes": scanned_notes,
        "notes_with_hash": notes_with_hash,
        "known_imported_hashes": len(state.get("imported_hashes", {})),
        "rebuilt_count": rebuilt_count,
    }