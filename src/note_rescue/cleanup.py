from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
import hashlib

from .paths import VAULT_DIR, REPORTS_DIR


def normalized_note_body(text: str) -> str:
    """
    Removes generated frontmatter before hashing, so duplicate reports compare note bodies.
    """
    stripped = text.strip()

    if stripped.startswith("---"):
        parts = stripped.split("---", 2)
        if len(parts) == 3:
            return parts[2].strip()

    return stripped


def generate_cleanup_report() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    all_notes = list(VAULT_DIR.rglob("*.md")) if VAULT_DIR.exists() else []

    by_body_hash = defaultdict(list)
    tiny_notes = []
    large_notes = []

    for path in all_notes:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        body = normalized_note_body(text)
        size = path.stat().st_size

        if len(body.strip()) < 80:
            tiny_notes.append(path)

        if size > 100_000:
            large_notes.append((path, size))

        digest = hashlib.sha256(body.encode("utf-8", errors="ignore")).hexdigest()
        by_body_hash[digest].append(path)

    duplicate_groups = [paths for paths in by_body_hash.values() if len(paths) > 1]

    out = REPORTS_DIR / f"cleanup_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"

    lines = []
    lines.append("# note-rescue Cleanup Report")
    lines.append("")
    lines.append(f"Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total Markdown notes: `{len(all_notes)}`")
    lines.append(f"- Duplicate content groups: `{len(duplicate_groups)}`")
    lines.append(f"- Tiny notes under 80 body characters: `{len(tiny_notes)}`")
    lines.append(f"- Large notes over 100 KB: `{len(large_notes)}`")
    lines.append("")
    lines.append("This report is non-destructive. It does not delete or move files.")
    lines.append("")

    lines.append("## Duplicate content groups")
    lines.append("")

    if not duplicate_groups:
        lines.append("No exact duplicate note bodies found.")
    else:
        for i, group in enumerate(duplicate_groups, start=1):
            lines.append(f"### Duplicate group {i}")
            lines.append("")
            for path in group:
                rel = path.relative_to(VAULT_DIR) if path.is_relative_to(VAULT_DIR) else path
                lines.append(f"- `{rel}`")
            lines.append("")

    lines.append("")
    lines.append("## Tiny notes")
    lines.append("")

    if not tiny_notes:
        lines.append("No tiny notes found.")
    else:
        for path in tiny_notes[:200]:
            rel = path.relative_to(VAULT_DIR) if path.is_relative_to(VAULT_DIR) else path
            lines.append(f"- `{rel}`")

        if len(tiny_notes) > 200:
            lines.append(f"- ...and `{len(tiny_notes) - 200}` more.")

    lines.append("")
    lines.append("## Large notes")
    lines.append("")

    if not large_notes:
        lines.append("No large notes found.")
    else:
        for path, size in sorted(large_notes, key=lambda x: x[1], reverse=True)[:100]:
            rel = path.relative_to(VAULT_DIR) if path.is_relative_to(VAULT_DIR) else path
            lines.append(f"- `{rel}` — `{round(size / 1024, 2)} KB`")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out