"""Main analysis pipeline: collect → analyze → AI → report."""
from __future__ import annotations
import webbrowser
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config_manager import ConfigManager, AppConfig
from .data_cache import DataCache
from ..collectors.trend_collector import TrendCollector
from ..analyzers.viral_analyzer import ViralAnalyzer
from ..analyzers.hashtag_optimizer import HashtagOptimizer
from ..analyzers.livestream_analyzer import LiveStreamAnalyzer
from ..ai_engine.claude_client import ClaudeClient
from ..ai_engine.insights_generator import InsightsGenerator
from ..reporters.html_reporter import HTMLReporter

console = Console()

BASE_DIR = Path(__file__).parent.parent.parent


class AnalysisPipeline:
    def __init__(self, config_path: str | None = None):
        cfg_manager = ConfigManager(config_path)
        self.config: AppConfig = cfg_manager.load()
        warnings = cfg_manager.validate(self.config)
        for w in warnings:
            console.print(f"[yellow]⚠️  {w}[/yellow]")

        output_dir = BASE_DIR / self.config.output_dir.lstrip("./")
        cache_path = str(BASE_DIR / "data" / "cache" / "cache.db")

        self.cache = DataCache(cache_path)
        self.collector = TrendCollector(self.config.rapidapi_key, self.cache)
        self.viral_analyzer = ViralAnalyzer()
        self.hashtag_optimizer = HashtagOptimizer()
        self.livestream_analyzer = LiveStreamAnalyzer()
        self.claude = ClaudeClient(self.config.anthropic_api_key, self.config.claude_model)
        self.insights_gen = InsightsGenerator(self.claude, self.config)
        self.reporter = HTMLReporter(str(output_dir))

    def run(self, open_browser: bool | None = None) -> str:
        open_b = open_browser if open_browser is not None else self.config.auto_open_report
        console.rule("[bold purple]TikTok Intelligence — Analyse startet[/bold purple]")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:

            task = progress.add_task("📡 Sammle TikTok-Trenddaten...", total=None)
            viral_patterns = {}
            hashtag_bundles = {}

            for niche in self.config.niches:
                progress.update(task, description=f"📡 Nische: {niche.display_name}...")
                trending_tags = self.collector.get_trending_hashtags(
                    niche.hashtag_seeds, limit=12
                )
                videos = []
                for tag in niche.hashtag_seeds[:3]:
                    videos.extend(
                        self.collector.get_viral_videos(tag, niche.id, limit=8)
                    )
                videos = sorted(videos, key=lambda v: v.views, reverse=True)[:20]
                viral_patterns[niche.id] = self.viral_analyzer.analyze(
                    videos, niche.id, niche.display_name
                )
                hashtag_bundles[niche.id] = self.hashtag_optimizer.build_bundles(
                    niche.id, trending_tags
                )

            progress.update(task, description="🔴 Analysiere Livestream-Daten...")
            live_diagnosis = self.livestream_analyzer.diagnose(
                follower_count=self.config.follower_count,
                avg_viewers=self.config.live.current_avg_viewers,
                duration_hours=self.config.live.typical_duration_hours,
                start_times=self.config.live.typical_start_times,
            )

            progress.update(task, description="🤖 Claude KI generiert Insights...")
            insights = self.insights_gen.generate_full_insights(
                viral_patterns, hashtag_bundles, live_diagnosis
            )

            progress.update(task, description="📄 Erstelle HTML-Bericht...")
            report_path = self.reporter.generate(
                self.config, viral_patterns, hashtag_bundles, live_diagnosis, insights
            )
            self.cache.save_report(report_path)

        console.print(f"\n[bold green]✅ Analyse abgeschlossen![/bold green]")
        console.print(f"[cyan]📄 Bericht: {report_path}[/cyan]")
        console.print(f"[dim]KI-Kosten: {insights.cost_estimate}[/dim]")

        if open_b:
            webbrowser.open(f"file://{Path(report_path).resolve()}")
            console.print("[green]🌐 Bericht wurde im Browser geöffnet.[/green]")

        return report_path
