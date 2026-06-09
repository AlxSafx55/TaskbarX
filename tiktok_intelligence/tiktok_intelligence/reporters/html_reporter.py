"""Generates the daily HTML report from collected data and AI insights."""
from __future__ import annotations
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ..analyzers.viral_analyzer import ViralPatterns
from ..analyzers.hashtag_optimizer import HashtagBundle
from ..analyzers.livestream_analyzer import LiveDiagnosis
from ..ai_engine.insights_generator import DailyInsights
from ..core.config_manager import AppConfig


class HTMLReporter:
    def __init__(self, output_dir: str = "./data/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        template_dir = Path(__file__).parent / "templates"
        self.jinja = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)

    def generate(
        self,
        config: AppConfig,
        viral_patterns: dict[str, ViralPatterns],
        hashtag_bundles: dict[str, list[HashtagBundle]],
        live_diagnosis: LiveDiagnosis,
        insights: DailyInsights,
    ) -> str:
        template = self.jinja.get_template("daily_report.html")

        # Build per-niche context
        niches_ctx = []
        for niche in config.niches:
            patterns = viral_patterns.get(niche.id)
            if not patterns:
                continue
            niches_ctx.append({
                "id": niche.id,
                "display_name": niche.display_name,
                "patterns": patterns,
                "analysis": insights.niche_analyses.get(niche.id, ""),
                "ideas": insights.content_ideas.get(niche.id, []),
                "bundles": hashtag_bundles.get(niche.id, []),
            })

        # Global trending (first niche data as proxy)
        first_patterns = next(iter(viral_patterns.values()), None)
        global_hashtags_raw = []
        if first_patterns:
            global_hashtags_raw = [
                type("H", (), {"tag": t})() for t in first_patterns.top_hashtags
            ]

        # Trending sounds from first niche
        trending_sounds_raw = []
        for s in (first_patterns.top_sounds if first_patterns else []):
            trending_sounds_raw.append(type("S", (), {"name": s, "usage_count": 0})())

        optimal_duration = "15–35"
        if first_patterns:
            d = first_patterns.duration
            optimal_duration = f"{d.optimal_min_seconds}–{d.optimal_max_seconds}"

        calendar_lines = insights.content_calendar.split("\n") if insights.content_calendar else []

        total_videos = sum(p.sample_count for p in viral_patterns.values())
        api_status = "✅ Echte TikTok-Daten" if config.rapidapi_key else "📱 Demo-Modus (kein RapidAPI-Key)"
        if config.anthropic_api_key:
            api_status += " · 🤖 Claude KI aktiv"
        else:
            api_status += " · ⚠️ KI-Demo (kein Anthropic-Key)"

        next_run = (datetime.now() + timedelta(hours=24)).strftime("%d.%m.%Y %H:%M Uhr")

        html = template.render(
            date=insights.date,
            tiktok_username=config.tiktok_username,
            follower_count=config.follower_count,
            niches=niches_ctx,
            niche_count=len(niches_ctx),
            total_videos_analyzed=total_videos,
            global_hashtags=global_hashtags_raw,
            trending_sounds=trending_sounds_raw,
            optimal_duration=optimal_duration,
            live_diagnosis=live_diagnosis,
            live_advice=insights.livestream_advice,
            upload_guide=insights.upload_guide,
            calendar_lines=calendar_lines,
            trend_opportunities=insights.trend_opportunities,
            profile_advice=insights.profile_advice,
            brand_protection=insights.brand_protection,
            prompt_recommendations=insights.prompt_recommendations,
            growth_roadmap=insights.growth_roadmap_text,
            cost_estimate=insights.cost_estimate,
            api_status=api_status,
            next_run=next_run,
        )

        date_str = datetime.now().strftime("%Y-%m-%d")
        out_path = self.output_dir / f"{date_str}_daily_report.html"
        out_path.write_text(html, encoding="utf-8")
        return str(out_path)
