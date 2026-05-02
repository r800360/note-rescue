from pathlib import Path
import json
from datetime import datetime

from .paths import DATA_DIR

STATE_PATH = DATA_DIR / "state.json"


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {
            "imported_hashes": {},
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def has_imported_hash(digest: str) -> bool:
    state = load_state()
    return digest in state.get("imported_hashes", {})


def mark_hash_imported(digest: str, markdown_file: str, original_file: str) -> None:
    state = load_state()

    if "imported_hashes" not in state:
        state["imported_hashes"] = {}

    state["imported_hashes"][digest] = {
        "markdown_file": markdown_file,
        "original_file": original_file,
        "imported_at": datetime.now().isoformat(timespec="seconds"),
    }

    save_state(state)
