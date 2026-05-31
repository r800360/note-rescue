"""Search rescued notes — prompts in a visible window, opens best match."""
import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "launchers"))

from console_utils import attach_console, pause

attach_console("note-rescue Find Notes")
os.chdir(ROOT)

from note_rescue.cli import cmd_find

print("=" * 56)
print("  note-rescue — search your rescued Notepad++ notes")
print("=" * 56)
print()
print("Tips: use words from the meeting, project, or class name.")
print("Example: student travel funds")
print()

try:
    while True:
        query = input("Search (Enter to quit): ").strip()
        if not query:
            break

        print()
        cmd_find(
            SimpleNamespace(
                query=query,
                limit=10,
                open=True,
                with_app="notepad++",
                no_open=False,
            )
        )
        print()
        again = input("Search again? (Y/n): ").strip().lower()
        if again in {"n", "no"}:
            break
        print()
except Exception as exc:
    print(f"\nError: {exc}", file=sys.stderr)
finally:
    pause()
