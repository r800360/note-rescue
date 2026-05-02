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
from .status import get_notepadpp_status, get_risk_level
from .readme_updater import update_readme

console = Console()


def cmd_backup(args):
    backup_path = backup_notepadpp()
    console.print(
        Panel.fit(
            f"Backed up Notepad++ files to:\n[bold green]{backup_path}[/bold green]",
            title="Backup Complete",
        )
    )


def cmd_import(args):
    index = import_notes()

    console.print(
        Panel.fit(
            "\n".join(
                [
                    f"Files seen: {index['total_files_seen']}",
                    f"Imported: {index['imported_count']}",
                    f"Skipped empty: {index['skipped_empty']}",
                    f"Skipped duplicates: {index['skipped_duplicates']}",
                ]
            ),
            title="Import Complete",
        )
    )

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
        table.add_row(str(result["score"]), result["path"], result["snippet"])

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
        "",
    ]

    for path, todo in todo_rows:
        rel = path.relative_to(VAULT_DIR)
        lines.append(f"- [ ] {todo}")
        lines.append(f"  - Source: `{rel}`")

    output_path.write_text("\n".join(lines), encoding="utf-8")

    console.print(
        Panel.fit(
            f"Extracted {len(todo_rows)} TODOs into:\n[bold green]{output_path}[/bold green]",
            title="TODO Extraction Complete",
        )
    )


def cmd_status(args):
    status = get_notepadpp_status()
    risk, message = get_risk_level(status["active_backup_files"])

    table = Table(title="Notepad++ / note-rescue Status")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Risk level", risk)
    table.add_row("Message", message)
    table.add_row("Active Notepad++ backup files", str(status["active_backup_files"]))
    table.add_row("Nonempty backup files", str(status["nonempty_backup_files"]))
    table.add_row("Empty backup files", str(status["empty_backup_files"]))
    table.add_row("Backup folder size", f"{status['backup_size_mb']} MB")
    table.add_row("Vault Markdown notes", str(status["vault_notes"]))
    table.add_row("Known imported hashes", str(status["known_imported_hashes"]))
    table.add_row("Notepad++ backup dir", status["backup_dir"])
    table.add_row("Session file exists", str(status["session_exists"]))

    console.print(table)


def cmd_sync(args):
    """
    Future-proof command:
    backup + import + todos.
    With persistent deduplication, this can be run repeatedly.
    """
    console.print("[bold cyan]Step 1/3: Backing up Notepad++...[/bold cyan]")
    backup_path = backup_notepadpp()

    console.print(f"[green]Backup saved to:[/green] {backup_path}")

    console.print("[bold cyan]Step 2/3: Importing new notes...[/bold cyan]")
    index = import_notes()

    console.print(
        Panel.fit(
            "\n".join(
                [
                    f"Files seen: {index['total_files_seen']}",
                    f"Newly imported: {index['imported_count']}",
                    f"Skipped empty: {index['skipped_empty']}",
                    f"Skipped duplicates/already imported: {index['skipped_duplicates']}",
                ]
            ),
            title="Sync Import Complete",
        )
    )

    console.print("[bold cyan]Step 3/3: Extracting TODOs...[/bold cyan]")
    cmd_todos(args)

    console.print("[bold green]Sync complete.[/bold green]")

    try:
        readme_path = update_readme()
        console.print(f"[green]README updated:[/green] {readme_path}")
    except Exception as exc:
        console.print(f"[yellow]README update skipped:[/yellow] {exc}")


def cmd_doctor(args):
    status = get_notepadpp_status()
    risk, message = get_risk_level(status["active_backup_files"])

    console.print(
        Panel.fit(
            f"Risk level: [bold]{risk}[/bold]\n{message}",
            title="Notepad++ Health Check",
        )
    )

    if risk in {"LOW", "MODERATE"}:
        console.print("[green]No urgent action needed.[/green]")
        console.print("Recommended habit: run `python main.py sync` weekly.")
        return

    if risk == "HIGH":
        console.print("[yellow]Recommended action:[/yellow]")
        console.print("1. Run `python main.py sync`")
        console.print("2. Review `vault/TODO/global_todos.md`")
        console.print("3. Manually close unnecessary Notepad++ tabs")
        return

    if risk in {"VERY HIGH", "EMERGENCY"}:
        console.print("[red]Recommended action:[/red]")
        console.print("1. Run `python main.py sync`")
        console.print("2. Confirm important notes exist in `vault/`")
        console.print("3. Close Notepad++")
        console.print("4. Rename the active Notepad++ session and backup folder")
        console.print("")
        console.print("Safe reset commands:")
        console.print(r"taskkill /F /IM notepad++.exe")
        console.print(r'cd "$env:APPDATA\Notepad++"')
        console.print(r"Rename-Item session.xml session_rescued_auto.xml")
        console.print(r"Rename-Item backup backup_rescued_auto")
        console.print(r"mkdir backup")


def cmd_update_readme(args):
    readme_path = update_readme()

    console.print(
        Panel.fit(
            f"Updated README auto-generated section:\n[bold green]{readme_path}[/bold green]",
            title="README Updated",
        )
    )
