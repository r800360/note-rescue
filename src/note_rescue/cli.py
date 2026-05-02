from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .backup import backup_notepadpp
from .importer import import_notes
from .search import search_notes
from .paths import VAULT_DIR
from .todo_extractor import extract_todos


console = Console()


def cmd_backup(args):
    backup_path = backup_notepadpp()
    console.print(Panel.fit(
        f"Backed up Notepad++ files to:\n[bold green]{backup_path}[/bold green]",
        title="Backup Complete"
    ))


def cmd_import(args):
    index = import_notes()

    console.print(Panel.fit(
        "\n".join([
            f"Files seen: {index['total_files_seen']}",
            f"Imported: {index['imported_count']}",
            f"Skipped empty: {index['skipped_empty']}",
            f"Skipped duplicates: {index['skipped_duplicates']}",
        ]),
        title="Import Complete"
    ))

    by_category = {}

    for note in index["notes"]:
        by_category[note["category"]] = by_category.get(note["category"], 0) + 1

    table = Table(title="Imported Notes by Category")
    table.add_column("Category")
    table.add_column("Count", justify="right")

    for category, count in sorted(by_category.items()):
        table.add_row(category, str(count))

    console.print(table)


def cmd_search(args):
    results = search_notes(args.query, limit=args.limit)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(title=f"Search Results for: {args.query}")
    table.add_column("Score", justify="right")
    table.add_column("Path")
    table.add_column("Snippet")

    for result in results:
        table.add_row(
            str(result["score"]),
            result["path"],
            result["snippet"]
        )

    console.print(table)


def cmd_todos(args):
    todo_rows = []

    for path in VAULT_DIR.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        todos = extract_todos(text)

        for todo in todos:
            todo_rows.append((path, todo))

    todo_dir = VAULT_DIR / "TODO"
    todo_dir.mkdir(parents=True, exist_ok=True)

    output_path = todo_dir / "global_todos.md"

    lines = [
        "# Global TODOs",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        ""
    ]

    for path, todo in todo_rows:
        rel = path.relative_to(VAULT_DIR)
        lines.append(f"- [ ] {todo}")
        lines.append(f"  - Source: `{rel}`")

    output_path.write_text("\n".join(lines), encoding="utf-8")

    console.print(Panel.fit(
        f"Extracted {len(todo_rows)} TODOs into:\n[bold green]{output_path}[/bold green]",
        title="TODO Extraction Complete"
    ))