from pathlib import Path
from datetime import datetime
import os

from .paths import (
    get_notepadpp_backup_dir,
    get_notepadpp_session_file,
    VAULT_DIR,
    DATA_DIR,
)
from .state import load_state


def get_notepadpp_status() -> dict:
    backup_dir = get_notepadpp_backup_dir()
    session_file = get_notepadpp_session_file()

    backup_files = []
    total_size = 0
    nonempty_files = 0
    empty_files = 0

    if backup_dir.exists():
        for path in backup_dir.rglob("*"):
            if path.is_file():
                backup_files.append(path)
                size = path.stat().st_size
                total_size += size

                if size == 0:
                    empty_files += 1
                else:
                    nonempty_files += 1

    vault_notes = list(VAULT_DIR.rglob("*.md")) if VAULT_DIR.exists() else []

    state = load_state()
    imported_count = len(state.get("imported_hashes", {}))

    return {
        "backup_dir": str(backup_dir),
        "session_file": str(session_file),
        "session_exists": session_file.exists(),
        "active_backup_files": len(backup_files),
        "nonempty_backup_files": nonempty_files,
        "empty_backup_files": empty_files,
        "backup_size_mb": round(total_size / (1024 * 1024), 2),
        "vault_notes": len(vault_notes),
        "known_imported_hashes": imported_count,
        "checked_at": datetime.now().isoformat(timespec="seconds"),
    }


def get_risk_level(active_backup_files: int) -> tuple[str, str]:
    if active_backup_files < 50:
        return "LOW", "Healthy. Notepad++ session size is currently manageable."

    if active_backup_files < 150:
        return (
            "MODERATE",
            "You are accumulating unsaved tabs. Consider running sync soon.",
        )

    if active_backup_files < 300:
        return "HIGH", "Notepad++ may start slowing down. Run sync and clean tabs."

    if active_backup_files < 1000:
        return "VERY HIGH", "You are approaching another serious Notepad++ buildup."

    return (
        "EMERGENCY",
        "Notepad++ is likely to become slow or fail to start. Back up, sync, and reset soon.",
    )
