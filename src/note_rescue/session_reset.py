from __future__ import annotations

import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

from .paths import RAW_BACKUPS_DIR, get_notepadpp_backup_dir, get_notepadpp_session_file
from .status import get_notepadpp_status


def get_notepadpp_data_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not found.")
    return Path(appdata) / "Notepad++"


def is_notepadpp_running() -> bool:
    if os.name != "nt":
        return False

    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq notepad++.exe"],
        capture_output=True,
        text=True,
    )
    return "notepad++.exe" in result.stdout.lower()


def kill_notepadpp() -> bool:
    if not is_notepadpp_running():
        return True

    result = subprocess.run(
        ["taskkill", "/F", "/IM", "notepad++.exe"],
        capture_output=True,
        text=True,
    )
    time.sleep(1)
    return result.returncode == 0 and not is_notepadpp_running()


def has_recent_project_backup(max_age_hours: int = 48) -> tuple[bool, str | None]:
    if not RAW_BACKUPS_DIR.exists():
        return False, None

    backups = sorted(RAW_BACKUPS_DIR.glob("notepadpp_backup_*"), reverse=True)
    if not backups:
        return False, None

    latest = backups[0]
    age = datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)
    if age <= timedelta(hours=max_age_hours):
        return True, str(latest)

    return False, str(latest)


def plan_reset() -> dict:
    data_dir = get_notepadpp_data_dir()
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    status = get_notepadpp_status()

    session_file = get_notepadpp_session_file()
    backup_dir = get_notepadpp_backup_dir()

    actions = []

    if session_file.exists():
        actions.append(
            {
                "action": "rename",
                "from": str(session_file),
                "to": str(data_dir / f"session_rescued_{stamp}.xml"),
            }
        )

    if backup_dir.exists():
        actions.append(
            {
                "action": "rename",
                "from": str(backup_dir),
                "to": str(data_dir / f"backup_rescued_{stamp}"),
            }
        )

    actions.append(
        {
            "action": "mkdir",
            "path": str(backup_dir),
        }
    )

    return {
        "data_dir": str(data_dir),
        "stamp": stamp,
        "notepadpp_running": is_notepadpp_running(),
        "active_backup_files": status["active_backup_files"],
        "vault_notes": status["vault_notes"],
        "actions": actions,
    }


def verify_safe_to_reset(require_recent_backup: bool = True) -> tuple[bool, list[str]]:
    issues: list[str] = []
    status = get_notepadpp_status()

    if status["vault_notes"] == 0:
        issues.append("Vault has no imported notes. Run `python main.py sync` first.")

    if require_recent_backup:
        ok, latest = has_recent_project_backup()
        if not ok:
            if latest:
                issues.append(
                    f"No recent project backup (latest: {latest}). Run `python main.py sync` first."
                )
            else:
                issues.append("No project backup found. Run `python main.py sync` first.")

    if status["active_backup_files"] == 0 and not get_notepadpp_session_file().exists():
        issues.append("Nothing to reset — Notepad++ session and backup folder are already clean.")

    return len(issues) == 0, issues


def apply_reset(force: bool = False, kill_first: bool = True) -> dict:
    safe, issues = verify_safe_to_reset(require_recent_backup=not force)
    if not safe and not force:
        return {"success": False, "issues": issues, "actions_taken": []}

    plan = plan_reset()
    if not plan["actions"]:
        return {"success": False, "issues": ["Nothing to reset."], "actions_taken": []}

    if plan["notepadpp_running"]:
        if not kill_first:
            return {
                "success": False,
                "issues": ["Notepad++ is running. Close it or use --kill-notepadpp."],
                "actions_taken": [],
            }
        if not kill_notepadpp():
            return {
                "success": False,
                "issues": ["Could not close Notepad++. Close it manually and retry."],
                "actions_taken": [],
            }

    actions_taken = []

    for step in plan["actions"]:
        if step["action"] == "rename":
            src = Path(step["from"])
            dst = Path(step["to"])
            if src.exists():
                if dst.exists():
                    dst = dst.with_name(dst.stem + "_dup" + dst.suffix)
                src.rename(dst)
                actions_taken.append(f"Renamed {src.name} -> {dst.name}")
        elif step["action"] == "mkdir":
            path = Path(step["path"])
            path.mkdir(parents=True, exist_ok=True)
            actions_taken.append(f"Created fresh {path.name}/ folder")

    return {
        "success": True,
        "issues": issues if force else [],
        "actions_taken": actions_taken,
        "stamp": plan["stamp"],
    }
