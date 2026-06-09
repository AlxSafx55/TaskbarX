#!/usr/bin/env python3
"""TikTok AI Growth Intelligence System — CLI Entry Point.

Usage:
  python run.py setup       → Ersteinrichtung (API-Key, Nischen, Timezone)
  python run.py run         → Sofortige Analyse + Bericht öffnen
  python run.py schedule    → Täglichen Scheduler starten
  python run.py guide       → Upload-Guide für ein Video
  python run.py livestream  → Livestream-Diagnose anzeigen
  python run.py status      → System-Status anzeigen
  python run.py profile     → Profil-Optimierung generieren
"""
import sys
import os
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

CONFIG_PATH = Path(__file__).parent / "config" / "settings.yaml"


@click.group()
def cli():
    """🤖 TikTok AI Growth Intelligence System"""
    console.print(Panel.fit(
        "[bold purple]TikTok AI Growth Intelligence[/bold purple] v1.0\n"
        "[dim]Täglich. Automatisiert. Für dich.[/dim]",
        border_style="purple",
    ))


@cli.command()
def run():
    """Sofortige Analyse starten und Bericht öffnen."""
    from tiktok_intelligence.core.pipeline import AnalysisPipeline
    try:
        pipeline = AnalysisPipeline(str(CONFIG_PATH))
        pipeline.run()
    except FileNotFoundError as e:
        console.print(f"[red]❌ {e}[/red]")
        console.print("[yellow]Führe zuerst 'python run.py setup' aus.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Fehler: {e}[/red]")
        raise


@cli.command()
def schedule():
    """Täglichen Scheduler starten (läuft dauerhaft)."""
    from tiktok_intelligence.core.pipeline import AnalysisPipeline
    from tiktok_intelligence.scheduler.daily_job import DailyScheduler

    try:
        pipeline = AnalysisPipeline(str(CONFIG_PATH))
        config = pipeline.config

        def run_job():
            console.print("\n[bold purple]⏰ Geplanter täglicher Run startet...[/bold purple]")
            pipeline.run(open_browser=config.auto_open_report)

        scheduler = DailyScheduler(
            run_fn=run_job,
            run_time=config.daily_run_time,
            timezone=config.timezone,
        )
        scheduler.start()
    except KeyboardInterrupt:
        console.print("\n[yellow]Scheduler gestoppt.[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("concept", required=False)
@click.option("--niche", default="", help="Nischen-ID (z.B. ai-rap)")
def guide(concept: str, niche: str):
    """Upload-Guide für ein konkretes Video generieren."""
    if not concept:
        concept = click.prompt("Beschreibe dein nächstes Video-Konzept")
    if not niche:
        niche = click.prompt("Deine Nische (z.B. ai-rap, ai-visuals, ai-prompts)", default="ai-rap")

    from tiktok_intelligence.core.pipeline import AnalysisPipeline
    pipeline = AnalysisPipeline(str(CONFIG_PATH))

    console.print(f"\n[cyan]📋 Erstelle Upload-Guide für: '{concept}'[/cyan]")
    upload = pipeline.insights_gen._upload_guide()

    table = Table(title=f"Upload-Guide: {concept}", border_style="purple")
    table.add_column("Bereich", style="cyan", width=20)
    table.add_column("Empfehlung", style="white")
    for key, value in upload.items():
        table.add_row(key.replace("_", " ").title(), value[:200] + "..." if len(value) > 200 else value)

    console.print(table)


@cli.command()
def livestream():
    """Livestream-Diagnose anzeigen."""
    from tiktok_intelligence.core.pipeline import AnalysisPipeline
    from tiktok_intelligence.analyzers.livestream_analyzer import LiveStreamAnalyzer

    pipeline = AnalysisPipeline(str(CONFIG_PATH))
    config = pipeline.config
    analyzer = LiveStreamAnalyzer()
    diagnosis = analyzer.diagnose(
        follower_count=config.follower_count,
        avg_viewers=config.live.current_avg_viewers,
        duration_hours=config.live.typical_duration_hours,
        start_times=config.live.typical_start_times,
    )

    console.print(Panel(
        f"[bold]Viewer/Follower-Rate: [yellow]{diagnosis.current_ratio_pct}%[/yellow][/bold]\n"
        f"Status: [red]{diagnosis.benchmark_label}[/red]\n"
        f"Optimale Dauer: {diagnosis.optimal_duration_minutes} Minuten",
        title="🔴 Livestream-Analyse",
        border_style="red",
    ))

    console.print("\n[bold red]Ursachen:[/bold red]")
    for cause in diagnosis.root_causes:
        console.print(f"  ⚠️  {cause}")

    console.print("\n[bold green]Aktionsplan:[/bold green]")
    for action in diagnosis.action_plan:
        console.print(f"  {action}")

    console.print("\n[bold cyan]Beste Live-Zeiten:[/bold cyan]")
    for t in diagnosis.best_live_times:
        console.print(f"  📅 {t}")

    console.print("\n[bold purple]Opening-Hooks (erste 30 Sekunden):[/bold purple]")
    for hook in diagnosis.opening_hooks:
        console.print(f'  💬 "{hook}"')


@cli.command()
def profile():
    """Profil-Optimierungsempfehlungen generieren."""
    from tiktok_intelligence.core.pipeline import AnalysisPipeline
    pipeline = AnalysisPipeline(str(CONFIG_PATH))
    console.print("\n[cyan]👤 Generiere Profil-Optimierung...[/cyan]")
    advice = pipeline.insights_gen._profile_advice()
    console.print(Panel(advice, title="👤 Profil-Optimierung", border_style="cyan"))


@cli.command()
def status():
    """System-Status und letzte Reports anzeigen."""
    from tiktok_intelligence.core.pipeline import AnalysisPipeline
    try:
        pipeline = AnalysisPipeline(str(CONFIG_PATH))
        config = pipeline.config
        latest = pipeline.cache.get_latest_report()

        table = Table(title="System-Status", border_style="purple")
        table.add_column("Info", style="cyan")
        table.add_column("Wert", style="white")
        table.add_row("TikTok-User", config.tiktok_username)
        table.add_row("Follower", str(config.follower_count))
        table.add_row("Nischen", ", ".join(n.id for n in config.niches))
        table.add_row("Täglicher Run", config.daily_run_time + " Uhr " + config.timezone)
        table.add_row("Claude API", "✅ Aktiv" if config.anthropic_api_key else "❌ Kein Key")
        table.add_row("RapidAPI", "✅ Aktiv" if config.rapidapi_key else "📱 Demo-Modus")
        table.add_row("Letzter Report", latest or "Noch kein Report")

        console.print(table)
    except Exception as e:
        console.print(f"[yellow]⚠️  {e}[/yellow]")


@cli.command()
def setup():
    """Interaktive Ersteinrichtung starten."""
    console.print(Panel.fit(
        "[bold]Willkommen beim TikTok AI Growth Intelligence Setup![/bold]\n\n"
        "Du wirst durch die Einrichtung geführt.\n"
        "Alle Einstellungen werden in config/settings.yaml gespeichert.",
        border_style="green",
    ))

    # Check if config exists
    if CONFIG_PATH.exists():
        overwrite = click.confirm("⚠️  settings.yaml existiert bereits. Überschreiben?", default=False)
        if not overwrite:
            console.print("[yellow]Setup abgebrochen. Bearbeite config/settings.yaml manuell.[/yellow]")
            return

    console.print("\n[bold cyan]Schritt 1/4: Anthropic API-Key[/bold cyan]")
    console.print("[dim]Hole deinen Key unter: https://console.anthropic.com (kostenlos starten)[/dim]")
    api_key = click.prompt("API-Key eingeben (oder Enter für Demo-Modus)", default="")

    console.print("\n[bold cyan]Schritt 2/4: Dein TikTok-Username[/bold cyan]")
    username = click.prompt("TikTok @Username", default="@deinhandle")

    console.print("\n[bold cyan]Schritt 3/4: Follower-Anzahl[/bold cyan]")
    followers = click.prompt("Aktuelle Follower-Anzahl", default=100, type=int)

    console.print("\n[bold cyan]Schritt 4/4: Täglicher Report-Zeitpunkt[/bold cyan]")
    run_time = click.prompt("Wann soll der Report erstellt werden? (HH:MM)", default="07:00")

    # Update settings.yaml
    import yaml
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)

    settings["api_keys"]["anthropic"] = api_key
    settings["tiktok"]["username"] = username
    settings["user"]["follower_count"] = followers
    settings["schedule"]["daily_run_time"] = run_time

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(settings, f, allow_unicode=True, default_flow_style=False)

    console.print("\n[bold green]✅ Setup abgeschlossen![/bold green]")
    console.print(f"[cyan]Konfiguration gespeichert: {CONFIG_PATH}[/cyan]")
    console.print("\nNächste Schritte:")
    console.print("  1. [yellow]python run.py run[/yellow]         → Erste Analyse starten")
    console.print("  2. [yellow]python run.py schedule[/yellow]    → Tägliche Automatisierung")
    console.print("  3. [yellow]python run.py livestream[/yellow]  → Live-Stream analysieren")

    if click.confirm("\nJetzt sofort erste Analyse starten?", default=True):
        from tiktok_intelligence.core.pipeline import AnalysisPipeline
        pipeline = AnalysisPipeline(str(CONFIG_PATH))
        pipeline.run()


if __name__ == "__main__":
    cli()
