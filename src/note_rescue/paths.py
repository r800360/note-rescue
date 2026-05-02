from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_BACKUPS_DIR = DATA_DIR / "raw_backups"
EXPORTED_NOTES_DIR = DATA_DIR / "exported_notes"
INDEXES_DIR = DATA_DIR / "indexes"
REPORTS_DIR = DATA_DIR / "reports"

VAULT_DIR = PROJECT_ROOT / "vault"
CONFIG_DIR = PROJECT_ROOT / "config"
CATEGORIES_PATH = CONFIG_DIR / "categories.json"


def get_notepadpp_backup_dir() -> Path:
    """
    Default Notepad++ backup directory for unsaved tabs.
    Usually:
      C:\\Users\\<user>\\AppData\\Roaming\\Notepad++\\backup
    """
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not found.")

    return Path(appdata) / "Notepad++" / "backup"


def get_notepadpp_session_file() -> Path:
    """
    Default Notepad++ session file.
    """
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not found.")

    return Path(appdata) / "Notepad++" / "session.xml"