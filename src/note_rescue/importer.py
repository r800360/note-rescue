from pathlib import Path
from datetime import datetime
import hashlib
import json
import shutil

from .paths import (
    EXPORTED_NOTES_DIR,
    INDEXES_DIR,
    VAULT_DIR,
    get_notepadpp_backup_dir,
)
from .classifier import classify_text, make_safe_filename
from .todo_extractor import extract_todos
from .state import has_imported_hash, mark_hash_imported, rebuild_state_from_vault


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def read_text_file(path: Path) -> str:
    """
    Try common encodings for Notepad++ backup files.
    """
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]

    for enc in encodings:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue

    return path.read_text(errors="ignore")


def find_notepadpp_backup_files() -> list[Path]:
    backup_dir = get_notepadpp_backup_dir()
    if not backup_dir.exists():
        raise FileNotFoundError(f"Notepad++ backup dir not found: {backup_dir}")

    return [p for p in backup_dir.rglob("*") if p.is_file()]


def import_notes() -> dict:
    """
    Converts Notepad++ backup files into Markdown notes in vault/.
    Non-destructive: does not delete or modify Notepad++ files.
    """
    rebuild_state_from_vault()

    files = find_notepadpp_backup_files()

    seen_hashes = set()
    imported = []
    skipped_empty = 0
    skipped_duplicates = 0

    today = datetime.now().strftime("%Y-%m-%d")

    for path in files:
        text = read_text_file(path).strip()

        if not text:
            skipped_empty += 1
            continue

        digest = hash_text(text)

        if digest in seen_hashes:
            skipped_duplicates += 1
            continue

        if has_imported_hash(digest):
            skipped_duplicates += 1
            continue

        seen_hashes.add(digest)

        category, scores = classify_text(text)
        safe_title = make_safe_filename(text, fallback=path.stem)
        short_hash = digest[:10]

        target_dir = VAULT_DIR / category
        target_dir.mkdir(parents=True, exist_ok=True)

        md_path = target_dir / f"{today}_{safe_title}_{short_hash}.md"

        todos = extract_todos(text)

        frontmatter = {
            "source": "notepad++ unsaved backup",
            "original_file": str(path),
            "imported_at": datetime.now().isoformat(timespec="seconds"),
            "category": category,
            "sha256": digest,
            "todo_count": len(todos),
            "classifier_scores": scores,
        }

        md_content = make_markdown_note(text, frontmatter, todos)

        md_path.write_text(md_content, encoding="utf-8")

        mark_hash_imported(
            digest=digest,
            markdown_file=str(md_path),
            original_file=str(path),
        )

        imported.append(
            {
                "original_file": str(path),
                "markdown_file": str(md_path),
                "category": category,
                "sha256": digest,
                "todo_count": len(todos),
            }
        )

    index = {
        "imported_at": datetime.now().isoformat(timespec="seconds"),
        "total_files_seen": len(files),
        "imported_count": len(imported),
        "skipped_empty": skipped_empty,
        "skipped_duplicates": skipped_duplicates,
        "notes": imported,
    }

    INDEXES_DIR.mkdir(parents=True, exist_ok=True)
    index_path = (
        INDEXES_DIR
        / f"import_index_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    )
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    return index


def make_markdown_note(text: str, frontmatter: dict, todos: list[str]) -> str:
    fm_lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, dict):
            fm_lines.append(f"{key}: {json.dumps(value)}")
        else:
            safe_value = str(value).replace("\n", " ")
            fm_lines.append(f"{key}: {json.dumps(safe_value)}")
    fm_lines.append("---")

    todo_section = ""

    if todos:
        todo_section = "\n\n## Extracted TODOs\n\n"
        for todo in todos:
            todo_section += f"- [ ] {todo}\n"

    return "\n".join(fm_lines) + "\n\n" + text + todo_section + "\n"
