"""Builds optimized hashtag bundles for each niche."""
from __future__ import annotations
from dataclasses import dataclass

from ..collectors.trend_collector import HashtagData


@dataclass
class HashtagBundle:
    name: str
    description: str
    hashtags: list[str]
    copyable: str
    estimated_reach: str


class HashtagOptimizer:
    MEGA_TAGS = ["#fyp", "#viral", "#foryou", "#trending"]
    MID_TAGS_BY_NICHE = {
        "ai-rap": ["#airap", "#aimusic", "#aigenerated", "#raplyrics", "#hiphop"],
        "ai-visuals": ["#aiart", "#dragon", "#aiartwork", "#digitalart", "#fantasyart"],
        "ai-prompts": ["#aiprompts", "#midjourney", "#aiartwork", "#promptengineering"],
    }
    MICRO_TAGS_BY_NICHE = {
        "ai-rap": ["#ailyricsrap", "#airapgod", "#kirap", "#kimusik"],
        "ai-visuals": ["#aidragon", "#fantasycreature", "#epicdragon", "#midjourneyfantasy"],
        "ai-prompts": ["#secretprompt", "#uniqueaiprompt", "#aipromtptips"],
    }

    def build_bundles(
        self, niche_id: str, trending: list[HashtagData]
    ) -> list[HashtagBundle]:
        trending_tags = [h.tag for h in sorted(trending, key=lambda x: x.trending_score, reverse=True)[:5]]
        mid = self.MID_TAGS_BY_NICHE.get(niche_id, trending_tags[:3])
        micro = self.MICRO_TAGS_BY_NICHE.get(niche_id, [])

        bundle_a = self.MEGA_TAGS[:2] + mid[:2] + trending_tags[:2] + micro[:1]
        bundle_b = mid[:3] + micro[:2] + trending_tags[:1] + ["#niche"]
        bundle_c = trending_tags[:2] + mid[:2] + self.MEGA_TAGS[:1] + micro[:1]

        bundles = [
            HashtagBundle(
                name="Bundle A — Maximale Reichweite",
                description="Breite Entdeckung + aktuell trending",
                hashtags=bundle_a[:8],
                copyable=" ".join(bundle_a[:8]),
                estimated_reach="500M–2B Views",
            ),
            HashtagBundle(
                name="Bundle B — Nischen-Community",
                description="Speziell für deine Zielgruppe",
                hashtags=bundle_b[:7],
                copyable=" ".join(bundle_b[:7]),
                estimated_reach="50M–300M Views",
            ),
            HashtagBundle(
                name="Bundle C — Discovery Mix",
                description="Trending + Nische + Micro-Tag (bestes Ranking)",
                hashtags=bundle_c[:6],
                copyable=" ".join(bundle_c[:6]),
                estimated_reach="200M–800M Views",
            ),
        ]
        return bundles

    def get_alternatives(self, hashtag: str) -> dict[str, str]:
        lookup = {
            "#airap": {"größer": "#aimusic", "kleiner": "#ailyricsrap", "trend": "#aigenerated"},
            "#aiart": {"größer": "#aiartwork", "kleiner": "#midjourneyfantasy", "trend": "#aidragon"},
            "#dragon": {"größer": "#fantasyart", "kleiner": "#epicdragon", "trend": "#aidragon"},
            "#aiprompts": {"größer": "#midjourney", "kleiner": "#secretprompt", "trend": "#aiartwork"},
        }
        return lookup.get(hashtag, {
            "größer": f"{hashtag}art",
            "kleiner": f"{hashtag}niche",
            "trend": "#aigenerated",
        })
