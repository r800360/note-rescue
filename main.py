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
    cmd_find,
    cmd_todos,
    cmd_todos_apply,
    cmd_todo_dismiss,
    cmd_status,
    cmd_sync,
    cmd_doctor,
    cmd_rebuild_state,
    cmd_cleanup_report,
    cmd_smoke_test,
    cmd_update_readme,
    cmd_reset,
    cmd_open,
    cmd_recent,
    cmd_today,
    cmd_go,
    cmd_scholar,
    cmd_privacy_check,
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
    search_parser.add_argument("--open", action="store_true", help="Open the top result.")
    search_parser.add_argument(
        "--with-app",
        choices=["default", "notepad++", "vscode"],
        default="default",
        help="App to open results with.",
    )
    search_parser.set_defaults(func=cmd_search)

    find_parser = subparsers.add_parser(
        "find",
        help="Search notes and open the top result (lazy-friendly alias).",
    )
    find_parser.add_argument("query", type=str)
    find_parser.add_argument("--limit", type=int, default=10)
    find_parser.add_argument("--no-open", action="store_true", help="Don't open the top result.")
    find_parser.add_argument(
        "--pick",
        action="store_true",
        help="Show top matches and let you pick which to open.",
    )
    find_parser.add_argument(
        "--with-app",
        choices=["default", "notepad++", "vscode"],
        default="notepad++",
    )
    find_parser.set_defaults(func=cmd_find)

    inbox_parser = subparsers.add_parser(
        "inbox",
        help="Open vault/Inbox/ in your editor (lazy shortcut).",
    )
    inbox_parser.add_argument(
        "--with-app",
        choices=["default", "notepad++", "vscode", "explorer"],
        default="default",
    )
    inbox_parser.set_defaults(func=cmd_open, target="inbox")

    todos_parser = subparsers.add_parser(
        "todos", help="Extract TODOs from imported notes."
    )
    todos_parser.add_argument("--open", action="store_true", help="Open global_todos.md after extraction.")
    todos_parser.set_defaults(func=cmd_todos)

    todos_apply_parser = subparsers.add_parser(
        "todos-apply",
        help="Permanently dismiss checked items (- [x]) from global_todos.md and refresh the list.",
    )
    todos_apply_parser.add_argument("--open", action="store_true", help="Open global_todos.md after refresh.")
    todos_apply_parser.set_defaults(func=cmd_todos_apply)

    todo_dismiss_parser = subparsers.add_parser(
        "todo-dismiss",
        help="Permanently dismiss one TODO by text (stops it reappearing after sync).",
    )
    todo_dismiss_parser.add_argument("text", type=str, help="TODO text to dismiss (quote if multiple words).")
    todo_dismiss_parser.set_defaults(func=cmd_todo_dismiss)

    status_parser = subparsers.add_parser("status", help="Show Notepad++ and vault health status.")
    status_parser.set_defaults(func=cmd_status)

    sync_parser = subparsers.add_parser(
        "sync",
        help="Back up, import new notes only, extract TODOs, and generate cleanup report.",
    )
    sync_parser.add_argument("--no-notify", action="store_true", help="Skip Windows toast notification.")
    sync_parser.set_defaults(func=cmd_sync)

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Diagnose whether Notepad++ is accumulating too many unsaved tabs.",
    )
    doctor_parser.set_defaults(func=cmd_doctor)

    reset_parser = subparsers.add_parser(
        "reset",
        help="Safely reset Notepad++ session (dry-run by default).",
    )
    reset_parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform the reset (closes Notepad++ if --kill-notepadpp).",
    )
    reset_parser.add_argument(
        "--kill-notepadpp",
        action="store_true",
        help="Force-close Notepad++ before resetting.",
    )
    reset_parser.add_argument(
        "--force",
        action="store_true",
        help="Skip safety checks (use only if you know notes are already in vault/).",
    )
    reset_parser.set_defaults(func=cmd_reset)

    open_parser = subparsers.add_parser(
        "open",
        help="Open vault, inbox, or todos in your editor / Explorer.",
    )
    open_parser.add_argument(
        "target",
        choices=["vault", "inbox", "todos", "todo"],
        help="What to open.",
    )
    open_parser.add_argument(
        "--with-app",
        choices=["default", "notepad++", "vscode", "explorer"],
        default="default",
    )
    open_parser.set_defaults(func=cmd_open)

    recent_parser = subparsers.add_parser(
        "recent",
        help="Show notes imported in the last few days.",
    )
    recent_parser.add_argument("--days", type=int, default=None)
    recent_parser.add_argument("--limit", type=int, default=20)
    recent_parser.add_argument("--open", action="store_true", help="Open the most recent note.")
    recent_parser.set_defaults(func=cmd_recent)

    today_parser = subparsers.add_parser(
        "today",
        help="Show notes imported today.",
    )
    today_parser.add_argument("--limit", type=int, default=50)
    today_parser.set_defaults(func=cmd_today)

    go_parser = subparsers.add_parser(
        "go",
        help="Lazy dashboard — status, todos, and quick commands at a glance.",
    )
    go_parser.add_argument("--open-todos", action="store_true", help="Also open global_todos.md.")
    go_parser.set_defaults(func=cmd_go)

    scholar_parser = subparsers.add_parser(
        "scholar",
        help="PATHS scholar profiles, meeting prep, and handoff summaries.",
    )
    scholar_sub = scholar_parser.add_subparsers(dest="scholar_action", required=True)

    scholar_list = scholar_sub.add_parser("list", help="List your 8 scholars.")
    scholar_list.set_defaults(func=cmd_scholar, scholar_action="list")

    scholar_show = scholar_sub.add_parser("show", help="Full profile for a meeting.")
    scholar_show.add_argument("name", type=str, help="Scholar display name from your local config.")
    scholar_show.add_argument("--topic", type=str, default="", help="Specific topic to search vault for.")
    scholar_show.add_argument("--open-notes", action="store_true", help="Open top related vault note.")
    scholar_show.set_defaults(func=cmd_scholar, scholar_action="show")

    scholar_handoff = scholar_sub.add_parser(
        "handoff",
        help="Paragraph handoff summary for spreadsheet (one or all scholars).",
    )
    scholar_handoff.add_argument("name", type=str, nargs="?", default="", help="One scholar, or omit for all 8.")
    scholar_handoff.add_argument(
        "--output",
        type=str,
        default="",
        help="Save to file (.md or .csv for spreadsheet paste).",
    )
    scholar_handoff.set_defaults(func=cmd_scholar, scholar_action="handoff")

    rebuild_state_parser = subparsers.add_parser(
        "rebuild-state",
        help="Rebuild persistent import state from existing vault notes.",
    )
    rebuild_state_parser.set_defaults(func=cmd_rebuild_state)

    cleanup_report_parser = subparsers.add_parser(
        "cleanup-report",
        help="Generate a non-destructive cleanup report.",
    )
    cleanup_report_parser.set_defaults(func=cmd_cleanup_report)

    smoke_test_parser = subparsers.add_parser(
        "smoke-test",
        help="Run a basic project health smoke test.",
    )
    smoke_test_parser.set_defaults(func=cmd_smoke_test)

    update_readme_parser = subparsers.add_parser(
        "update-readme",
        help="Update the auto-generated README section.",
    )
    update_readme_parser.set_defaults(func=cmd_update_readme)

    privacy_parser = subparsers.add_parser(
        "privacy-check",
        help="Scan tracked files for private data before pushing to public GitHub.",
    )
    privacy_parser.set_defaults(func=cmd_privacy_check)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "find":
        args.open = not args.no_open

    if args.command == "sync" and args.no_notify:
        args.notify = False

    args.func(args)


if __name__ == "__main__":
    main()
