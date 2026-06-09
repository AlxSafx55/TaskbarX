"""APScheduler-based daily job runner."""
from __future__ import annotations
import webbrowser
from datetime import datetime

from rich.console import Console

console = Console()


class DailyScheduler:
    def __init__(self, run_fn, run_time: str = "07:00", timezone: str = "Europe/Berlin"):
        from apscheduler.schedulers.blocking import BlockingScheduler
        hour, minute = map(int, run_time.split(":"))
        self.scheduler = BlockingScheduler(timezone=timezone)
        self.scheduler.add_job(
            run_fn,
            "cron",
            hour=hour,
            minute=minute,
            id="daily_tiktok_analysis",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

    def start(self) -> None:
        next_run = self.scheduler.get_job("daily_tiktok_analysis").next_run_time
        console.print(f"\n[bold green]✅ Scheduler gestartet![/bold green]")
        console.print(f"[cyan]Nächster automatischer Run: {next_run.strftime('%d.%m.%Y um %H:%M Uhr')}[/cyan]")
        console.print("[dim]Lasse dieses Terminal geöffnet oder minimiere es. Strg+C zum Stoppen.[/dim]\n")
        self.scheduler.start()
