from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .paths import CONFIG_DIR, PROJECT_ROOT, VAULT_DIR

SCHOLARS_LOCAL_PATH = CONFIG_DIR / "scholars.local.json"

PRIVATE_PATHS = [
    CONFIG_DIR / "scholars.local.json",
    CONFIG_DIR / "scholars.json",
    CONFIG_DIR / "secrets.local.json",
    CONFIG_DIR / "site.profile.public.json",
    PROJECT_ROOT / "vault",
    PROJECT_ROOT / "data" / "scholars",
    PROJECT_ROOT / "data" / "chat_corrections.json",
]

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PID_PATTERN = re.compile(r"\bA\d{8}\b")


def git_tracked_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    return [PROJECT_ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()]


def git_ignored(path: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return path.name.endswith(".local.json")


def scan_text_for_leaks(text: str) -> list[str]:
    issues = []
    emails = EMAIL_PATTERN.findall(text)
    if emails:
        issues.append(f"found email(s): {', '.join(sorted(set(emails))[:3])}")

    pids = PID_PATTERN.findall(text)
    if pids:
        issues.append(f"found PID(s): {', '.join(sorted(set(pids))[:3])}")

    return issues


def run_privacy_check() -> dict:
    results = {
        "passed": True,
        "issues": [],
        "warnings": [],
        "tracked_file_count": 0,
    }

    for private in PRIVATE_PATHS:
        if private.exists() and not git_ignored(private):
            results["passed"] = False
            results["issues"].append(f"Private path exists but is NOT gitignored: {private.relative_to(PROJECT_ROOT)}")

    tracked = git_tracked_files()
    results["tracked_file_count"] = len(tracked)

    for path in tracked:
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".py", ".md", ".json", ".ps1", ".cmd", ".txt", ".csv"}:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel = path.relative_to(PROJECT_ROOT)
        if rel.as_posix().startswith("config/scholars.") and rel.name != "scholars.example.json":
            results["passed"] = False
            results["issues"].append(f"Scholar config must not be tracked: {rel}")
            continue

        leaks = scan_text_for_leaks(text)
        if leaks and "scholars.example.json" not in str(rel):
            results["passed"] = False
            results["issues"].append(f"{rel}: {'; '.join(leaks)}")

    if not SCHOLARS_LOCAL_PATH.exists():
        results["warnings"].append(
            "config/scholars.local.json not found locally (OK for public clone; copy from scholars.example.json)."
        )

    if VAULT_DIR.exists() and not git_ignored(VAULT_DIR):
        results["passed"] = False
        results["issues"].append("vault/ exists but is NOT gitignored")

    return results
