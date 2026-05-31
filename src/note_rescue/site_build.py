from __future__ import annotations

import json
import shutil
from pathlib import Path

from .open_utils import open_path
from .site_content import load_json_file, load_profile, merge_content, save_public_content
from .site_paths import CONTENT_PUBLIC, SITE_DIST_DIR, SITE_TEMPLATE_DIR, ensure_site_dirs
from .site_redact import scan_for_leaks


def review_public_text(text: str) -> list[str]:
    return scan_for_leaks(text)


def build_site() -> Path:
    ensure_site_dirs()

    if not SITE_TEMPLATE_DIR.exists():
        raise RuntimeError(f"Missing site template at {SITE_TEMPLATE_DIR}")

    profile = load_profile()
    draft = load_json_file(CONTENT_PUBLIC)
    if not draft:
        from .site_content import latest_draft_path

        latest = latest_draft_path()
        if latest:
            draft = load_json_file(latest)

    content = merge_content(profile, draft)
    save_public_content(content)

    if SITE_DIST_DIR.exists():
        shutil.rmtree(SITE_DIST_DIR)
    shutil.copytree(SITE_TEMPLATE_DIR, SITE_DIST_DIR)

    (SITE_DIST_DIR / "content.json").write_text(
        json.dumps(content, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return SITE_DIST_DIR / "index.html"


def open_built_site() -> Path:
    index = SITE_DIST_DIR / "index.html"
    if not index.exists():
        raise RuntimeError("Run `python main.py site build` first.")
    open_path(index, target="default")
    return index
