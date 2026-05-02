import sys
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from note_rescue.cli import (
    cmd_backup,
    cmd_import,
    cmd_search,
    cmd_todos,
    cmd_status,
    cmd_sync,
    cmd_doctor,
    cmd_rebuild_state,
    cmd_cleanup_report,
    cmd_smoke_test,
    cmd_update_readme,
)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="note-rescue",
        description="Rescue, organize, classify, and search Notepad++ unsaved notes.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser(
        "backup", help="Back up Notepad++ session and unsaved files."
    )
    backup_parser.set_defaults(func=cmd_backup)

    import_parser = subparsers.add_parser(
        "import", help="Import Notepad++ unsaved files into Markdown vault."
    )
    import_parser.set_defaults(func=cmd_import)

    search_parser = subparsers.add_parser("search", help="Search imported notes.")
    search_parser.add_argument("query", type=str)
    search_parser.add_argument("--limit", type=int, default=20)
    search_parser.set_defaults(func=cmd_search)

    todos_parser = subparsers.add_parser(
        "todos", help="Extract TODOs from imported notes."
    )
    todos_parser.set_defaults(func=cmd_todos)

    status_parser = subparsers.add_parser("status", help="Show Notepad++ and vault health status.")
    status_parser.set_defaults(func=cmd_status)

    sync_parser = subparsers.add_parser(
        "sync",
        help="Back up, import new notes only, extract TODOs, and generate cleanup report."
    )
    sync_parser.set_defaults(func=cmd_sync)

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Diagnose whether Notepad++ is accumulating too many unsaved tabs."
    )
    doctor_parser.set_defaults(func=cmd_doctor)

    rebuild_state_parser = subparsers.add_parser(
        "rebuild-state",
        help="Rebuild persistent import state from existing vault notes."
    )
    rebuild_state_parser.set_defaults(func=cmd_rebuild_state)

    cleanup_report_parser = subparsers.add_parser(
        "cleanup-report",
        help="Generate a non-destructive cleanup report."
    )
    cleanup_report_parser.set_defaults(func=cmd_cleanup_report)

    smoke_test_parser = subparsers.add_parser(
        "smoke-test",
        help="Run a basic project health smoke test."
    )
    smoke_test_parser.set_defaults(func=cmd_smoke_test)

    update_readme_parser = subparsers.add_parser(
        "update-readme",
        help="Update the auto-generated README section."
    )
    update_readme_parser.set_defaults(func=cmd_update_readme)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
