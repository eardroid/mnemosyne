"""Mnemosyne live dashboard — real-time memory security monitor."""

import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure the project root is on sys.path so `python mnemosyne/dashboard.py` works.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from mnemosyne.ledger import Ledger


def _build_stats_row(stats: dict) -> Columns:
    """Three side-by-side stat panels."""
    total = Panel(
        f"[bold white]{stats['total_all']}[/bold white]",
        title="Total operations",
        border_style="white",
        expand=True,
    )
    stored = Panel(
        f"[bold green]{stats['total_stored']}[/bold green]",
        title="Stored",
        border_style="green",
        expand=True,
    )
    blocked = Panel(
        f"[bold red]{stats['total_blocked']}[/bold red]",
        title="Blocked",
        border_style="red",
        expand=True,
    )
    return Columns([total, stored, blocked], equal=True, expand=True)


def _build_log_table(rows: list[dict]) -> Table:
    """Recent-events table with colour-coded status."""
    table = Table(
        title="Mnemosyne — Memory Security Monitor",
        box=box.ROUNDED,
        expand=True,
        border_style="cyan",
    )
    table.add_column("Time", style="dim", width=20)
    table.add_column("Source", width=10)
    table.add_column("Trust", width=8)
    table.add_column("Status", width=9)
    table.add_column("Flags", width=32)
    table.add_column("Preview")

    for row in rows:
        status = row["status"]
        status_style = "bold green" if status == "STORED" else "bold red"

        flags_raw = row["flags_found"] or "—"
        flags_display = flags_raw[:30] + "…" if len(flags_raw) > 30 else flags_raw

        preview = row["content"][:55] + "..." if len(row["content"]) > 55 else row["content"]

        table.add_row(
            row["timestamp"][:19],
            row["source"],
            row["trust_level"],
            f"[{status_style}]{status}[/{status_style}]",
            flags_display,
            preview,
        )

    if not rows:
        table.add_row("—", "—", "—", "—", "—", "[dim]No events recorded yet[/dim]")

    return table


def _build_footer() -> Panel:
    """Timestamp panel showing last refresh time."""
    now = datetime.now().strftime("%H:%M:%S")
    return Panel(
        f"[dim]Last refreshed: {now}[/dim]",
        border_style="dim",
        expand=True,
    )


def show_dashboard() -> None:
    """Launch the live-refreshing security dashboard."""
    ledger = Ledger()
    console = Console()

    console.print(
        Panel(
            "[bold cyan]Mnemosyne Dashboard[/bold cyan]  —  press Ctrl+C to stop",
            border_style="cyan",
            expand=False,
        )
    )

    try:
        with Live(console=console, refresh_per_second=1, screen=False) as live:
            while True:
                stats = ledger.get_stats()
                recent = ledger.get_recent(20)

                from rich.console import Group

                display = Group(
                    _build_stats_row(stats),
                    _build_log_table(recent),
                    _build_footer(),
                )
                live.update(display)
                time.sleep(3)
    except KeyboardInterrupt:
        console.print(
            Panel(
                "[bold yellow]Dashboard stopped.[/bold yellow]",
                border_style="yellow",
                expand=False,
            )
        )


if __name__ == "__main__":
    show_dashboard()
