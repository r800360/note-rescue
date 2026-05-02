from pathlib import Path
import shutil
from datetime import datetime

from .paths import (
    RAW_BACKUPS_DIR,
    get_notepadpp_backup_dir,
    get_notepadpp_session_file,
)


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def backup_notepadpp() -> Path:
    """
    Copies Notepad++ backup folder and session.xml into data/raw_backups.
    This is intentionally non-destructive.
    """
    src_backup_dir = get_notepadpp_backup_dir()
    src_session_file = get_notepadpp_session_file()

    if not src_backup_dir.exists():
        raise FileNotFoundError(f"Notepad++ backup dir not found: {src_backup_dir}")

    backup_root = RAW_BACKUPS_DIR / f"notepadpp_backup_{timestamp()}"
    backup_root.mkdir(parents=True, exist_ok=True)

    dst_backup_dir = backup_root / "backup"
    shutil.copytree(src_backup_dir, dst_backup_dir)

    if src_session_file.exists():
        shutil.copy2(src_session_file, backup_root / "session.xml")

    return backup_root