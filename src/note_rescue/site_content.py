from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .site_paths import (
    CONTENT_PUBLIC,
    PROFILE_EXAMPLE,
    PROFILE_PUBLIC,
    SITE_DRAFTS_DIR,
    SITE_SOURCES_DIR,
    ensure_site_dirs,
)
from .site_redact import redact_text

DEFAULT_CONTENT: dict[str, Any] = {
    "name": "",
    "tagline": "",
    "location_public": "",
    "email_public": "",
    "about": "",
    "values": [],
    "quotes": [],
    "projects": [],
    "reading": [],
    "interests": [],
    "links": [],
    "draft_notes": [],
}


def load_profile() -> dict[str, Any]:
    path = PROFILE_PUBLIC if PROFILE_PUBLIC.exists() else PROFILE_EXAMPLE
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def latest_draft_path() -> Path | None:
    if not SITE_DRAFTS_DIR.exists():
        return None
    drafts = sorted(SITE_DRAFTS_DIR.glob("draft-*.json"), reverse=True)
    return drafts[0] if drafts else None


def load_source_snippets(max_chars: int = 12000) -> str:
    if not SITE_SOURCES_DIR.exists():
        return ""

    parts: list[str] = []
    total = 0
    for path in sorted(SITE_SOURCES_DIR.rglob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception:
            continue
        if not text:
            continue
        chunk = f"--- {path.name} ---\n{text[:4000]}"
        if total + len(chunk) > max_chars:
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n\n".join(parts)


def merge_content(profile: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    merged = dict(DEFAULT_CONTENT)

    for key in DEFAULT_CONTENT:
        if key in draft and draft[key]:
            merged[key] = draft[key]

    if profile.get("name"):
        merged["name"] = profile["name"]
    if profile.get("tagline"):
        merged["tagline"] = profile["tagline"]
    if profile.get("location_public"):
        merged["location_public"] = profile["location_public"]
    if profile.get("links"):
        merged["links"] = profile["links"]
    if profile.get("email_public"):
        merged["email_public"] = profile["email_public"]

    return merged


def save_public_content(content: dict[str, Any]) -> Path:
    ensure_site_dirs()
    text = json.dumps(content, indent=2, ensure_ascii=False)
    text = redact_text(text)
    CONTENT_PUBLIC.write_text(text, encoding="utf-8")
    return CONTENT_PUBLIC


def save_draft(content: dict[str, Any]) -> Path:
    ensure_site_dirs()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = SITE_DRAFTS_DIR / f"draft-{stamp}.json"
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
