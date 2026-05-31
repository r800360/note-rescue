from __future__ import annotations

import json
from typing import Any

from .paths import CONFIG_DIR

SETTINGS_PATH = CONFIG_DIR / "settings.json"

DEFAULTS: dict[str, Any] = {
    "auto_reset_threshold": 100,
    "auto_reset_after_sync": True,
    "notify_after_sync": True,
    "default_open_target": "notepad++",
    "recent_days_default": 7,
    "sync_schedule_hour": 21,
}


def load_settings() -> dict[str, Any]:
    settings = dict(DEFAULTS)

    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                settings.update(loaded)
        except Exception:
            pass

    return settings
