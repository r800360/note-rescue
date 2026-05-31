from pathlib import Path
from datetime import datetime
import os
import re
from types import SimpleNamespace

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .backup import backup_notepadpp
from .importer import import_notes
from .search import search_notes
from .paths import VAULT_DIR, DATA_DIR
from .todo_extractor import extract_todos
from .dismissed_todos import is_dismissed, dismiss_todo, dismiss_many, dismissed_count
from .status import get_notepadpp_status, get_risk_level
from .state import rebuild_state_from_vault, load_state, save_state
from .cleanup import generate_cleanup_report
from .smoke_test import run_smoke_test
from .readme_updater import update_readme
from .session_reset import apply_reset, plan_reset, verify_safe_to_reset
from .notify import show_toast
from .open_utils import open_path, open_vault_target
from .recent import list_recent_notes, list_today_notes
from .settings import load_settings
from .scholars import (
    list_scholar_configs,
    load_scholar_profile,
    resolve_scholar,
    format_profile_text,
    build_handoff_paragraph,
    load_scholars_config,
)

console = Console()


def _record_sync(imported_count: int) -> None:
    state = load_state()
    state["last_sync_at"] = datetime.now().isoformat(timespec="seconds")
    state["last_sync_imported"] = imported_count
    save_state(state)


def _maybe_auto_reset(imported_count: int) -> dict | None:
    settings = load_settings()
    if not settings.get("auto_reset_after_sync"):
        return None

    threshold = int(settings.get("auto_reset_threshold", 100))
    status = get_notepadpp_status()
    active = status["active_backup_files"]

    if active < threshold:
        return None

    if imported_count > 0:
        return None

    safe, issues = verify_safe_to_reset(require_recent_backup=True)
    if not safe:
        return {"attempted": False, "reason": "; ".join(issues)}

    result = apply_reset(force=False, kill_first=False)
    return {"attempted": True, **result}


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
        console.print("Try fewer or different words, or run [cyan]python main.py recent[/cyan].")
        return

    interactive = getattr(args, "pick", False) or os.environ.get("NOTE_RESCUE_LAUNCHER") == "1"
    show = min(len(results), 5 if interactive else len(results))

    if interactive:
        console.print(f"\n[bold]Top matches for:[/bold] {args.query}\n")
        for i, result in enumerate(results[:show], 1):
            tag = " [green](exact phrase)[/green]" if result.get("phrase_match") else ""
            title = result.get("title", "")[:60]
            console.print(f"  [bold cyan]{i}.[/bold cyan] {title}{tag}")
            console.print(f"     [dim]{result['rel_path']}[/dim]")
            console.print(f"     {result['snippet']}\n")
    else:
        table = Table(title=f"Search Results for: {args.query}")
        table.add_column("#", justify="right")
        table.add_column("Title")
        table.add_column("Path")
        table.add_column("Snippet")

        for i, result in enumerate(results, 1):
            table.add_row(
                str(i),
                result.get("title", "")[:40],
                result["rel_path"],
                result["snippet"],
            )

        console.print(table)

    if not getattr(args, "open", False) or not results:
        return

    choice = 0
    if interactive:
        raw = input(f"Open which result? [1-{show}, Enter=1]: ").strip()
        if raw:
            try:
                choice = int(raw) - 1
            except ValueError:
                choice = 0
        choice = max(0, min(choice, show - 1))
    else:
        choice = 0

    target = getattr(args, "with_app", "default")
    picked = Path(results[choice]["path"])
    rel = picked.relative_to(VAULT_DIR) if VAULT_DIR in picked.parents else picked.name
    open_path(picked, target=target)
    console.print("")
    console.print(f"[bold green]Opened in Notepad++:[/bold green] {rel}")
    console.print("[dim]Check your taskbar if the window is behind other apps.[/dim]")


def cmd_find(args):
    """Search with friendlier output; opens top result when --open is set."""
    args.open = getattr(args, "open", True)
    cmd_search(args)


def cmd_todos(args):
    todo_rows = []
    skipped_dismissed = 0

    for path in VAULT_DIR.rglob("*.md"):
        if path.name == "global_todos.md":
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        todos = extract_todos(text)

        for todo in todos:
            if is_dismissed(todo):
                skipped_dismissed += 1
                continue
            todo_rows.append((path, todo))

    todo_dir = VAULT_DIR / "TODO"
    todo_dir.mkdir(parents=True, exist_ok=True)

    output_path = todo_dir / "global_todos.md"

    lines = [
        "# Global TODOs",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Lazy cleanup: change `- [ ]` to `- [x]` for done/irrelevant, save, then run `todos.cmd apply`",
        "",
    ]

    for path, todo in todo_rows:
        rel = path.relative_to(VAULT_DIR)
        lines.append(f"- [ ] {todo}")
        lines.append(f"  - Source: `{rel}`")

    output_path.write_text("\n".join(lines), encoding="utf-8")

    summary = f"Extracted {len(todo_rows)} TODOs into:\n[bold green]{output_path}[/bold green]"
    if skipped_dismissed:
        summary += f"\nSkipped {skipped_dismissed} dismissed items"

    console.print(
        Panel.fit(
            summary,
            title="TODO Extraction Complete",
        )
    )

    if getattr(args, "open", False):
        open_path(output_path)
        console.print("[green]Opened global_todos.md[/green]")


def cmd_todos_apply(args):
    """Read checkmarks from global_todos.md and permanently dismiss them."""
    output_path = VAULT_DIR / "TODO" / "global_todos.md"

    if not output_path.exists():
        console.print("[yellow]No global_todos.md yet. Run `python main.py todos` first.[/yellow]")
        return

    text = output_path.read_text(encoding="utf-8", errors="ignore")
    to_dismiss = []

    for line in text.splitlines():
        match = re.match(r"^\s*-\s*\[x\]\s+(.+)$", line, flags=re.IGNORECASE)
        if match:
            to_dismiss.append(match.group(1).strip())

    if not to_dismiss:
        console.print("[yellow]No checked items (`- [x]`) found in global_todos.md.[/yellow]")
        console.print("Open todos, change `- [ ]` to `- [x]` on items to remove, save, then run apply again.")
        return

    count = dismiss_many(to_dismiss, reason="checked in global_todos")
    console.print(f"[green]Dismissed {count} item(s).[/green] Regenerating list...")
    cmd_todos(SimpleNamespace(open=getattr(args, "open", False)))


def cmd_todo_dismiss(args):
    dismiss_todo(args.text, reason="manual")
    console.print(f"[green]Dismissed:[/green] {args.text}")
    console.print(f"Total dismissed: {dismissed_count()}")


def cmd_status(args):
    status = get_notepadpp_status()
    risk, message = get_risk_level(status["active_backup_files"])
    state = load_state()

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
    table.add_row("Last sync", str(state.get("last_sync_at", "never")))
    table.add_row("Notepad++ backup dir", status["backup_dir"])
    table.add_row("Session file exists", str(status["session_exists"]))

    console.print(table)


def cmd_rebuild_state(args):
    result = rebuild_state_from_vault()

    console.print(Panel.fit(
        "\n".join([
            f"State path: {result['state_path']}",
            f"Scanned vault notes: {result['scanned_notes']}",
            f"Notes with sha256 metadata: {result['notes_with_hash']}",
            f"Known imported hashes: {result['known_imported_hashes']}",
            f"New hashes rebuilt from vault: {result['rebuilt_count']}",
        ]),
        title="State Rebuilt"
    ))


def cmd_sync(args):
    """
    Safe recurring command:
    backup + import new notes only + todos + cleanup report.
    """
    settings = load_settings()
    notify = getattr(args, "notify", None)
    if notify is None:
        notify = settings.get("notify_after_sync", True)

    console.print("[bold cyan]Step 0/4: Rebuilding state from existing vault...[/bold cyan]")
    rebuild = rebuild_state_from_vault()
    console.print(f"[green]Known imported hashes:[/green] {rebuild['known_imported_hashes']}")

    console.print("[bold cyan]Step 1/4: Backing up Notepad++...[/bold cyan]")
    backup_path = backup_notepadpp()
    console.print(f"[green]Backup saved to:[/green] {backup_path}")

    console.print("[bold cyan]Step 2/4: Importing new notes only...[/bold cyan]")
    index = import_notes()
    imported = index["imported_count"]

    console.print(Panel.fit(
        "\n".join([
            f"Files seen: {index['total_files_seen']}",
            f"Newly imported: {imported}",
            f"Skipped empty: {index['skipped_empty']}",
            f"Skipped duplicates/already imported: {index['skipped_duplicates']}",
        ]),
        title="Sync Import Complete"
    ))

    console.print("[bold cyan]Step 3/4: Extracting TODOs...[/bold cyan]")
    cmd_todos(args)

    console.print("[bold cyan]Step 4/4: Generating cleanup report...[/bold cyan]")
    report_path = generate_cleanup_report()
    console.print(f"[green]Cleanup report:[/green] {report_path}")

    try:
        readme_path = update_readme()
        console.print(f"[green]README updated:[/green] {readme_path}")
    except Exception as exc:
        console.print(f"[yellow]README update skipped:[/yellow] {exc}")

    _record_sync(imported)

    auto_reset = _maybe_auto_reset(imported)
    reset_msg = ""
    if auto_reset:
        if auto_reset.get("attempted") and auto_reset.get("success"):
            reset_msg = f" Auto-reset Notepad++ session ({auto_reset.get('stamp', '')})."
            for action in auto_reset.get("actions_taken", []):
                console.print(f"[green]{action}[/green]")
        elif auto_reset.get("attempted") and not auto_reset.get("success"):
            console.print(f"[yellow]Auto-reset skipped:[/yellow] {'; '.join(auto_reset.get('issues', []))}")
            console.print("Run [cyan]python main.py reset --apply[/cyan] when Notepad++ is closed.")
        elif not auto_reset.get("attempted"):
            console.print(f"[dim]Auto-reset not run: {auto_reset.get('reason', '')}[/dim]")

    console.print("[bold green]Sync complete.[/bold green]")

    status = get_notepadpp_status()
    risk, _ = get_risk_level(status["active_backup_files"])

    if notify:
        toast_body = f"{imported} new notes imported. {status['active_backup_files']} tabs open ({risk})."
        if reset_msg:
            toast_body += reset_msg
        show_toast("note-rescue sync done", toast_body)


def cmd_doctor(args):
    status = get_notepadpp_status()
    risk, message = get_risk_level(status["active_backup_files"])
    settings = load_settings()
    threshold = int(settings.get("auto_reset_threshold", 100))

    console.print(Panel.fit(
        f"Risk level: [bold]{risk}[/bold]\n{message}\n\n"
        f"Active tabs: {status['active_backup_files']} | Vault notes: {status['vault_notes']}",
        title="Notepad++ Health Check"
    ))

    if risk in {"LOW", "MODERATE"}:
        console.print("[green]No urgent action needed.[/green]")
        console.print("Your 9 PM daily sync handles rescue automatically.")
        if status["active_backup_files"] >= 50:
            console.print(f"[dim]Tip: auto-reset kicks in at {threshold} tabs after sync imports everything.[/dim]")
        return

    console.print("[yellow]Recommended:[/yellow] run [cyan]python main.py sync[/cyan]")

    if status["active_backup_files"] >= threshold:
        console.print("Then run [cyan]python main.py reset --apply[/cyan] to give Notepad++ a fresh session.")
        console.print("Preview first with [cyan]python main.py reset[/cyan] (dry-run).")
    elif risk == "HIGH":
        console.print("Review [cyan]vault/TODO/global_todos.md[/cyan] and close scratch tabs you no longer need.")


def cmd_reset(args):
    plan = plan_reset()

    table = Table(title="Notepad++ Reset Plan")
    table.add_column("Step")
    table.add_column("Detail")

    for i, step in enumerate(plan["actions"], 1):
        if step["action"] == "rename":
            table.add_row(str(i), f"Rename {Path(step['from']).name} -> {Path(step['to']).name}")
        else:
            table.add_row(str(i), f"Create fresh {Path(step['path']).name}/ folder")

    console.print(table)

    console.print(
        f"Active backup files: {plan['active_backup_files']} | "
        f"Vault notes: {plan['vault_notes']} | "
        f"Notepad++ running: {plan['notepadpp_running']}"
    )

    safe, issues = verify_safe_to_reset(require_recent_backup=not getattr(args, "force", False))
    if issues:
        for issue in issues:
            console.print(f"[yellow]Warning: {issue}[/yellow]")

    if not getattr(args, "apply", False):
        console.print("\n[bold]Dry run only.[/bold] To apply: [cyan]python main.py reset --apply[/cyan]")
        if plan["notepadpp_running"]:
            console.print("Close Notepad++ first, or add [cyan]--kill-notepadpp[/cyan]")
        return

    if not safe and not getattr(args, "force", False):
        console.print("[red]Reset blocked.[/red] Run sync first, or use [cyan]--force[/cyan] to override.")
        return

    kill = getattr(args, "kill_notepadpp", False) or plan["notepadpp_running"]
    result = apply_reset(force=getattr(args, "force", False), kill_first=kill)

    if result["success"]:
        console.print(Panel.fit(
            "\n".join(result["actions_taken"]) or "Reset complete.",
            title="Notepad++ Reset Complete",
        ))
        console.print("[green]Reopen Notepad++ — it should start with a clean session.[/green]")
        show_toast("Notepad++ reset", "Fresh session ready. Your notes are safe in vault/.")
    else:
        console.print("[red]Reset failed:[/red]")
        for issue in result.get("issues", []):
            console.print(f"  • {issue}")


def cmd_open(args):
    target = getattr(args, "with_app", load_settings().get("default_open_target", "default"))
    path = open_vault_target(args.target, target=target)
    console.print(f"[green]Opened:[/green] {path}")


def cmd_recent(args):
    settings = load_settings()
    days = getattr(args, "days", None) or settings.get("recent_days_default", 7)
    limit = getattr(args, "limit", 20)
    notes = list_recent_notes(days=days, limit=limit)

    if not notes:
        console.print(f"[yellow]No notes imported in the last {days} days.[/yellow]")
        return

    table = Table(title=f"Notes Imported (last {days} days)")
    table.add_column("When")
    table.add_column("Category")
    table.add_column("Title")
    table.add_column("Path")

    for note in notes:
        when = note["imported_dt"].strftime("%Y-%m-%d %H:%M")
        table.add_row(when, note["category"], note["title"][:50], note["rel_path"])

    console.print(table)

    if getattr(args, "open", False) and notes:
        open_path(Path(notes[0]["path"]))
        console.print(f"[green]Opened most recent:[/green] {notes[0]['title']}")


def cmd_today(args):
    notes = list_today_notes(limit=getattr(args, "limit", 50))

    if not notes:
        console.print("[yellow]No notes imported today yet.[/yellow]")
        console.print("Your 9 PM sync will rescue today's Notepad++ tabs automatically.")
        return

    table = Table(title=f"Today's Imported Notes ({len(notes)})")
    table.add_column("Time")
    table.add_column("Category")
    table.add_column("Title")

    for note in notes:
        when = note["imported_dt"].strftime("%H:%M")
        table.add_row(when, note["category"], note["title"][:60])

    console.print(table)


def cmd_go(args):
    """Lazy dashboard — everything you need at a glance."""
    status = get_notepadpp_status()
    risk, message = get_risk_level(status["active_backup_files"])
    state = load_state()
    settings = load_settings()
    threshold = int(settings.get("auto_reset_threshold", 100))

    today = list_today_notes(limit=100)
    recent = list_recent_notes(days=7, limit=100)

    todo_path = VAULT_DIR / "TODO" / "global_todos.md"
    todo_count = 0
    if todo_path.exists():
        todo_count = todo_path.read_text(encoding="utf-8", errors="ignore").count("- [ ]")

    inbox_count = len(list((VAULT_DIR / "Inbox").rglob("*.md"))) if (VAULT_DIR / "Inbox").exists() else 0

    risk_color = {"LOW": "green", "MODERATE": "yellow", "HIGH": "yellow", "VERY HIGH": "red", "EMERGENCY": "red"}.get(risk, "white")

    lines = [
        f"[bold]Risk:[/bold] [{risk_color}]{risk}[/{risk_color}] - {status['active_backup_files']} unsaved tabs",
        f"[bold]Vault:[/bold] {status['vault_notes']} notes ({inbox_count} in Inbox)",
        f"[bold]TODOs:[/bold] {todo_count} open items",
        f"[bold]Today:[/bold] {len(today)} notes rescued | [bold]This week:[/bold] {len(recent)} notes",
        f"[bold]Last sync:[/bold] {state.get('last_sync_at', 'never')}",
        "",
    ]

    if status["active_backup_files"] >= threshold:
        lines.append(f"[yellow]Action: {status['active_backup_files']} tabs >= {threshold} threshold. Run: python main.py reset --apply[/yellow]")
    elif risk in {"HIGH", "VERY HIGH", "EMERGENCY"}:
        lines.append("[yellow]Action: Run python main.py sync[/yellow]")
    else:
        lines.append("[green]You're fine. 9 PM sync handles the rest.[/green]")

    lines.extend([
        "",
        "[bold]Quick commands:[/bold]",
        '  python main.py find "meeting notes"     # search + open top result',
        "  python main.py open todos               # open your TODO list",
        "  todos.cmd                               # refresh + open TODOs (lazy)",
        "  python main.py recent                   # see what was rescued lately",
        "  python main.py reset --apply            # fresh Notepad++ session",
    ])

    console.print(Panel("\n".join(lines), title="note-rescue", border_style="cyan"))

    if getattr(args, "open_todos", False) and todo_path.exists():
        open_path(todo_path)


def cmd_cleanup_report(args):
    report_path = generate_cleanup_report()

    console.print(Panel.fit(
        f"Generated cleanup report:\n[bold green]{report_path}[/bold green]",
        title="Cleanup Report Complete"
    ))


def cmd_smoke_test(args):
    results = run_smoke_test()

    table = Table(title="note-rescue Smoke Test")
    table.add_column("Check")
    table.add_column("Result")

    for key, value in results.items():
        table.add_row(key, str(value))

    console.print(table)

    if results.get("passed"):
        console.print("[bold green]Smoke test passed.[/bold green]")
    else:
        console.print("[bold red]Smoke test failed. Review the table above.[/bold red]")


def cmd_update_readme(args):
    readme_path = update_readme()

    console.print(Panel.fit(
        f"Updated README auto-generated section:\n[bold green]{readme_path}[/bold green]",
        title="README Updated"
    ))


def cmd_scholar(args):
    action = args.scholar_action

    if action == "list":
        table = Table(title="PATHS Scholars (2025-26)")
        table.add_column("#", justify="right")
        table.add_column("Name")
        table.add_column("Full name")

        for i, scholar in enumerate(list_scholar_configs(), 1):
            table.add_row(str(i), scholar.display_name, scholar.full_name)

        console.print(table)
        console.print("\nMeeting: [cyan]scholar.cmd[/cyan] or [cyan]python main.py scholar show NAME[/cyan]")
        return

    if action == "handoff":
        if args.name:
            resolved = resolve_scholar(args.name)
            if not resolved:
                console.print(f"[red]Scholar not found:[/red] {args.name}")
                return
            scholars = [resolved]
        else:
            scholars = list_scholar_configs()

        rows = []
        for scholar in scholars:
            profile = load_scholar_profile(scholar.display_name, include_vault=False)
            if not profile:
                continue
            paragraph = build_handoff_paragraph(profile)
            rows.append((profile.config.display_name, paragraph))

        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            if args.output.endswith(".csv"):
                import csv
                with open(out, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Scholar", "Handoff Summary"])
                    writer.writerows(rows)
            else:
                lines = [f"# PATHS Handoff Summaries ({load_scholars_config().get('academic_year', '')})", ""]
                for name, paragraph in rows:
                    lines.append(f"## {name}")
                    lines.append("")
                    lines.append(paragraph)
                    lines.append("")
                out.write_text("\n".join(lines), encoding="utf-8")
            console.print(f"[green]Wrote {len(rows)} handoff summaries to:[/green] {out}")

        for name, paragraph in rows:
            console.print(Panel(paragraph, title=name, border_style="cyan"))
        return

    # show / meeting
    if not args.name:
        console.print("[yellow]Provide a scholar name. Example: python main.py scholar show \"Scholar One\"[/yellow]")
        return

    profile = load_scholar_profile(args.name, include_vault=True)
    if not profile:
        console.print(f"[red]Scholar not found:[/red] {args.name}")
        console.print("Try: python main.py scholar list")
        return

    topic = getattr(args, "topic", "") or ""
    text = format_profile_text(profile, topic=topic)
    console.print(text)

    if getattr(args, "open_notes", False) and profile.vault_hits:
        open_path(Path(profile.vault_hits[0]["path"]))
        console.print("[green]Opened top related vault note in Notepad++[/green]")


def cmd_privacy_check(args):
    from .privacy import run_privacy_check

    results = run_privacy_check()

    if results["issues"]:
        console.print("[bold red]Privacy check FAILED[/bold red]")
        for issue in results["issues"]:
            console.print(f"  [red]- {issue}[/red]")
    else:
        console.print("[bold green]Privacy check passed[/bold green] for tracked files.")

    for warning in results["warnings"]:
        console.print(f"  [yellow]Note: {warning}[/yellow]")

    console.print(f"Tracked files scanned: {results['tracked_file_count']}")

    if not results["passed"]:
        console.print("\nFix issues before pushing to a public GitHub repo.")
