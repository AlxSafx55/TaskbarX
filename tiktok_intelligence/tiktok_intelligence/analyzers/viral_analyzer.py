"""Analyzes viral video patterns to extract insights."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from typing import Optional

from ..collectors.trend_collector import VideoData, HashtagData, SoundData


@dataclass
class DurationAnalysis:
    optimal_min_seconds: int
    optimal_max_seconds: int
    bucket_distribution: dict[str, int]
    recommendation: str


@dataclass
class EngagementBenchmarks:
    avg_engagement_rate: float
    p25_views: int
    median_views: int
    p75_views: int
    avg_shares_ratio: float
    avg_comments_ratio: float


@dataclass
class ViralPatterns:
    niche_id: str
    niche_name: str
    top_hashtags: list[str]
    top_sounds: list[str]
    duration: DurationAnalysis
    benchmarks: EngagementBenchmarks
    hook_patterns: list[str]
    caption_insights: str
    viral_score_avg: float
    sample_count: int
    top_videos: list[dict] = field(default_factory=list)


class ViralAnalyzer:
    DURATION_BUCKETS = {
        "hook_only (0-15s)": (0, 15),
        "sweet_spot (16-30s)": (16, 30),
        "standard (31-60s)": (31, 60),
        "long (61-180s)": (61, 180),
        "extended (180s+)": (181, 9999),
    }

    def analyze(self, videos: list[VideoData], niche_id: str, niche_name: str) -> ViralPatterns:
        if not videos:
            return self._empty_patterns(niche_id, niche_name)

        sorted_videos = sorted(videos, key=lambda v: v.views, reverse=True)
        top = sorted_videos[:min(10, len(sorted_videos))]

        return ViralPatterns(
            niche_id=niche_id,
            niche_name=niche_name,
            top_hashtags=self._top_hashtags(top),
            top_sounds=self._top_sounds(top),
            duration=self._analyze_duration(top),
            benchmarks=self._benchmarks(videos),
            hook_patterns=self._hook_patterns(top),
            caption_insights=self._caption_insights(top),
            viral_score_avg=self._avg_viral_score(top),
            sample_count=len(videos),
            top_videos=[
                {
                    "description": v.description[:120],
                    "views": v.views,
                    "likes": v.likes,
                    "shares": v.shares,
                    "duration": v.duration_seconds,
                    "engagement_rate": round(v.engagement_rate * 100, 2),
                    "sound": v.sound_name,
                }
                for v in top[:5]
            ],
        )

    def _top_hashtags(self, videos: list[VideoData]) -> list[str]:
        counter = Counter()
        for v in videos:
            counter.update(v.hashtags)
        return [tag for tag, _ in counter.most_common(8)]

    def _top_sounds(self, videos: list[VideoData]) -> list[str]:
        counter = Counter(v.sound_name for v in videos if v.sound_name)
        return [s for s, _ in counter.most_common(5)]

    def _analyze_duration(self, videos: list[VideoData]) -> DurationAnalysis:
        bucket_counts: dict[str, int] = {k: 0 for k in self.DURATION_BUCKETS}
        for v in videos:
            for name, (lo, hi) in self.DURATION_BUCKETS.items():
                if lo <= v.duration_seconds <= hi:
                    bucket_counts[name] += 1
                    break

        best_bucket = max(bucket_counts, key=lambda k: bucket_counts[k])
        lo, hi = self.DURATION_BUCKETS[best_bucket]

        durations = [v.duration_seconds for v in videos if v.duration_seconds > 0]
        if durations:
            avg = sum(durations) / len(durations)
            opt_min = max(lo, int(avg * 0.8))
            opt_max = min(hi, int(avg * 1.2))
        else:
            opt_min, opt_max = 15, 35

        return DurationAnalysis(
            optimal_min_seconds=opt_min,
            optimal_max_seconds=opt_max,
            bucket_distribution=bucket_counts,
            recommendation=f"Optimale Länge für deine Nische: {opt_min}–{opt_max} Sekunden",
        )

    def _benchmarks(self, videos: list[VideoData]) -> EngagementBenchmarks:
        views_sorted = sorted(v.views for v in videos)
        n = len(views_sorted)
        if n == 0:
            return EngagementBenchmarks(0, 0, 0, 0, 0, 0)

        rates = [v.engagement_rate for v in videos if v.views > 0]
        share_ratios = [v.shares / v.views for v in videos if v.views > 0]
        comment_ratios = [v.comments / v.views for v in videos if v.views > 0]

        return EngagementBenchmarks(
            avg_engagement_rate=sum(rates) / len(rates) if rates else 0,
            p25_views=views_sorted[n // 4],
            median_views=views_sorted[n // 2],
            p75_views=views_sorted[3 * n // 4],
            avg_shares_ratio=sum(share_ratios) / len(share_ratios) if share_ratios else 0,
            avg_comments_ratio=sum(comment_ratios) / len(comment_ratios) if comment_ratios else 0,
        )

    def _hook_patterns(self, videos: list[VideoData]) -> list[str]:
        hook_words = ["POV:", "Warte", "Wenn du", "Schau was", "KI hat", "Ich hab",
                      "Das ist", "Diese", "Dieser", "Wait for", "POV:", "Watch"]
        found = []
        for v in videos:
            for word in hook_words:
                if v.description.startswith(word) and word not in found:
                    found.append(word)
        return found[:6] or ["POV:", "Warte bis zum Ende...", "Das hat mich umgehauen:"]

    def _caption_insights(self, videos: list[VideoData]) -> str:
        lengths = [len(v.description) for v in videos]
        avg_len = sum(lengths) / len(lengths) if lengths else 80
        has_emoji = sum(1 for v in videos if any(ord(c) > 127 for c in v.description))
        emoji_pct = (has_emoji / len(videos) * 100) if videos else 0
        return (
            f"Ø Länge: {int(avg_len)} Zeichen · "
            f"{int(emoji_pct)}% verwenden Emojis · "
            f"Kurze Hooks am Anfang dominieren"
        )

    def _avg_viral_score(self, videos: list[VideoData]) -> float:
        scores = []
        for v in videos:
            if v.views == 0:
                continue
            share_score = min(100, (v.shares / v.views) * 2000)
            engagement_score = min(100, v.engagement_rate * 500)
            view_score = min(100, v.views / 50000)
            scores.append(share_score * 0.4 + engagement_score * 0.35 + view_score * 0.25)
        return round(sum(scores) / len(scores), 1) if scores else 0.0

    def _empty_patterns(self, niche_id: str, niche_name: str) -> ViralPatterns:
        return ViralPatterns(
            niche_id=niche_id, niche_name=niche_name, top_hashtags=[],
            top_sounds=[], duration=DurationAnalysis(15, 35, {}, "Keine Daten"),
            benchmarks=EngagementBenchmarks(0, 0, 0, 0, 0, 0),
            hook_patterns=[], caption_insights="Keine Daten", viral_score_avg=0, sample_count=0,
        )
