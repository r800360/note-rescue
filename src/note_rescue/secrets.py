from __future__ import annotations

import json
import os
from typing import Any

from .paths import CONFIG_DIR

SECRETS_PATH = CONFIG_DIR / "secrets.local.json"
SECRETS_EXAMPLE_PATH = CONFIG_DIR / "secrets.example.json"

CHAT_DEFAULTS: dict[str, Any] = {
    "openai_model": "gpt-4o-mini",
    "chat_max_notes": 10,
    "chat_max_chars_per_note": 6000,
}


def load_secrets() -> dict[str, Any]:
    """Load private API settings from gitignored config/secrets.local.json."""
    secrets = dict(CHAT_DEFAULTS)

    if SECRETS_PATH.exists():
        try:
            with open(SECRETS_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                secrets.update(loaded)
        except Exception:
            pass

    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        secrets["openai_api_key"] = env_key

    return secrets


def get_openai_api_key() -> str:
    key = str(load_secrets().get("openai_api_key", "")).strip()
    return key


def secrets_setup_hint() -> str:
    return (
        f"Copy {SECRETS_EXAMPLE_PATH.name} to {SECRETS_PATH.name} "
        f"and set openai_api_key, or set OPENAI_API_KEY in your environment."
    )
