"""Configuration loader and validator."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class NicheConfig:
    id: str
    display_name: str
    description: str
    production_hours_per_video: float
    hashtag_seeds: list[str]
    style_keywords: list[str]
    character_description: str = ""


@dataclass
class LiveConfig:
    typical_start_times: list[str]
    typical_duration_hours: float
    current_avg_viewers: float
    goals: list[str]


@dataclass
class AppConfig:
    anthropic_api_key: str
    rapidapi_key: str
    tiktok_username: str
    timezone: str
    follower_count: int
    avg_live_viewers: float
    niches: list[NicheConfig]
    live: LiveConfig
    claude_model: str
    daily_run_time: str
    auto_open_report: bool
    output_dir: str
    viral_threshold_views: int
    growth_milestones: list[dict]
    raw: dict


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
        self.config_path = Path(config_path)

    def load(self) -> AppConfig:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config-Datei nicht gefunden: {self.config_path}\n"
                "Bitte führe zuerst 'python run.py setup' aus."
            )
        with open(self.config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        api_key = (
            os.environ.get("ANTHROPIC_API_KEY")
            or raw.get("api_keys", {}).get("anthropic", "")
        )
        rapidapi_key = (
            os.environ.get("RAPIDAPI_KEY")
            or raw.get("api_keys", {}).get("rapidapi", "")
        )

        niches = [
            NicheConfig(
                id=n["id"],
                display_name=n["display_name"],
                description=n.get("description", ""),
                production_hours_per_video=float(n.get("production_hours_per_video", 4)),
                hashtag_seeds=n.get("hashtag_seeds", []),
                style_keywords=n.get("style_keywords", []),
                character_description=n.get("character_description", ""),
            )
            for n in raw.get("niches", [])
        ]

        live_raw = raw.get("live_streaming", {})
        live = LiveConfig(
            typical_start_times=live_raw.get("typical_start_times", ["20:00"]),
            typical_duration_hours=float(live_raw.get("typical_duration_hours", 2)),
            current_avg_viewers=float(live_raw.get("current_avg_viewers", 3.5)),
            goals=live_raw.get("goals", []),
        )

        return AppConfig(
            anthropic_api_key=api_key,
            rapidapi_key=rapidapi_key,
            tiktok_username=raw.get("tiktok", {}).get("username", ""),
            timezone=raw.get("user", {}).get("timezone", "Europe/Berlin"),
            follower_count=int(raw.get("user", {}).get("follower_count", 100)),
            avg_live_viewers=float(raw.get("user", {}).get("avg_live_viewers", 3.5)),
            niches=niches,
            live=live,
            claude_model=raw.get("claude", {}).get("model", "claude-sonnet-4-6"),
            daily_run_time=raw.get("schedule", {}).get("daily_run_time", "07:00"),
            auto_open_report=raw.get("reports", {}).get("open_in_browser", True),
            output_dir=raw.get("reports", {}).get("output_dir", "./data/reports"),
            viral_threshold_views=int(
                raw.get("analysis", {}).get("viral_threshold_views", 50000)
            ),
            growth_milestones=raw.get("growth_roadmap", {}).get("milestones", []),
            raw=raw,
        )

    def validate(self, config: AppConfig) -> list[str]:
        warnings = []
        if not config.anthropic_api_key:
            warnings.append("Kein Anthropic API-Key gesetzt. KI-Analyse deaktiviert.")
        if not config.niches:
            warnings.append("Keine Nischen konfiguriert. Bitte settings.yaml bearbeiten.")
        if config.follower_count < 1:
            warnings.append("follower_count ist 0 — bitte aktualisieren.")
        return warnings
