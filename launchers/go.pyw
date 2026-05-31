"""Launch note-rescue dashboard in a visible window."""
import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "launchers"))

from console_utils import attach_console, pause

attach_console("note-rescue Dashboard")
os.chdir(ROOT)

from note_rescue.cli import cmd_go

try:
    cmd_go(SimpleNamespace(open_todos=False))
except Exception as exc:
    print(f"\nError: {exc}", file=sys.stderr)
finally:
    pause()
