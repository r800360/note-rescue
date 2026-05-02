import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import argparse

from note_rescue.cli import (
    cmd_backup,
    cmd_import,
    cmd_search,
    cmd_todos,
)

def build_parser():
    parser = argparse.ArgumentParser(
        prog="note-rescue",
        description="Rescue, organize, classify, and search Notepad++ unsaved notes."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser("backup", help="Back up Notepad++ session and unsaved files.")
    backup_parser.set_defaults(func=cmd_backup)

    import_parser = subparsers.add_parser("import", help="Import Notepad++ unsaved files into Markdown vault.")
    import_parser.set_defaults(func=cmd_import)

    search_parser = subparsers.add_parser("search", help="Search imported notes.")
    search_parser.add_argument("query", type=str)
    search_parser.add_argument("--limit", type=int, default=20)
    search_parser.set_defaults(func=cmd_search)

    todos_parser = subparsers.add_parser("todos", help="Extract TODOs from imported notes.")
    todos_parser.set_defaults(func=cmd_todos)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()