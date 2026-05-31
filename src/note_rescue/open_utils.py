from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from .paths import VAULT_DIR


def open_path(path: Path, target: str = "default") -> None:
    """
    Open a file or folder on Windows.

    target:
      - default: OS default app
      - notepad++: Notepad++ if found, else default
      - vscode: VS Code if found, else default
      - explorer: File Explorer (folders only)
    """
    path = Path(path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    if target == "explorer" and path.is_dir():
        os.startfile(path)  # type: ignore[attr-defined]
        return

    if target == "notepad++":
        npp = find_notepadpp_exe()
        if npp and path.is_file():
            subprocess.Popen([npp, str(path)])
            return

    if target == "vscode":
        code = shutil.which("code")
        if code:
            subprocess.Popen([code, str(path)])
            return

    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", str(path)])


def find_notepadpp_exe() -> str | None:
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Notepad++" / "notepad++.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "Notepad++"
        / "notepad++.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Notepad++" / "notepad++.exe",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return shutil.which("notepad++")


def open_vault_target(name: str, target: str = "default") -> Path:
    mapping = {
        "vault": VAULT_DIR,
        "inbox": VAULT_DIR / "Inbox",
        "todos": VAULT_DIR / "TODO" / "global_todos.md",
        "todo": VAULT_DIR / "TODO" / "global_todos.md",
    }

    key = name.lower().strip()
    if key not in mapping:
        raise ValueError(f"Unknown target: {name}. Use: {', '.join(mapping)}")

    path = mapping[key]
    if key in {"todos", "todo"} and not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Global TODOs\n\nRun `python main.py todos` first.\n", encoding="utf-8")

    if key == "vault":
        open_path(path, target="explorer" if target == "default" else target)
    else:
        open_path(path, target=target)

    return path
