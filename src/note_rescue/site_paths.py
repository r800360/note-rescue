from __future__ import annotations

from pathlib import Path

from .paths import CONFIG_DIR, PROJECT_ROOT

SITE_DIR = PROJECT_ROOT / "site"
SITE_TEMPLATE_DIR = SITE_DIR / "template"
SITE_DRAFTS_DIR = SITE_DIR / "drafts"
SITE_SOURCES_DIR = SITE_DIR / "sources"
SITE_PUBLIC_DIR = SITE_DIR / "public"
SITE_DIST_DIR = SITE_DIR / "dist"

PROFILE_EXAMPLE = CONFIG_DIR / "site.profile.example.json"
PROFILE_PUBLIC = CONFIG_DIR / "site.profile.public.json"
CONTENT_PUBLIC = SITE_PUBLIC_DIR / "content.json"


def ensure_site_dirs() -> None:
    for path in (SITE_DRAFTS_DIR, SITE_SOURCES_DIR, SITE_PUBLIC_DIR, SITE_DIST_DIR):
        path.mkdir(parents=True, exist_ok=True)
