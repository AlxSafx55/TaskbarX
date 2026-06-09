"""TikTok trend data collector with RapidAPI + fallback to mock data."""
from __future__ import annotations
import random
import time
from dataclasses import dataclass
from datetime import datetime

import requests


@dataclass
class HashtagData:
    tag: str
    video_count: int
    view_count: int
    trending_score: float
    growth_rate_7d: float = 0.0


@dataclass
class SoundData:
    sound_id: str
    name: str
    author: str
    usage_count: int
    trending_score: float
    genres: list[str]


@dataclass
class VideoData:
    video_id: str
    description: str
    hashtags: list[str]
    views: int
    likes: int
    comments: int
    shares: int
    duration_seconds: int
    sound_name: str
    sound_id: str
    author_followers: int
    posted_at: str
    engagement_rate: float = 0.0

    def __post_init__(self):
        if self.views > 0:
            self.engagement_rate = (self.likes + self.comments + self.shares) / self.views


class TrendCollector:
    """Collects TikTok trend data. Uses RapidAPI if key provided, else returns demo data."""

    RAPIDAPI_HOST = "tiktok-scraper7.p.rapidapi.com"

    def __init__(self, rapidapi_key: str = "", cache=None):
        self.rapidapi_key = rapidapi_key
        self.cache = cache
        self._session = requests.Session()
        if rapidapi_key:
            self._session.headers.update({
                "X-RapidAPI-Key": rapidapi_key,
                "X-RapidAPI-Host": self.RAPIDAPI_HOST,
            })

    def get_trending_hashtags(self, seed_tags: list[str], limit: int = 15) -> list[HashtagData]:
        cache_key = f"hashtags_{'_'.join(seed_tags[:3])}"
        if self.cache:
            cached = self.cache.get("hashtags", cache_key)
            if cached:
                return [HashtagData(**h) for h in cached["items"]]

        if self.rapidapi_key:
            data = self._fetch_rapidapi_hashtags(seed_tags, limit)
        else:
            data = self._demo_hashtags(seed_tags, limit)

        if self.cache and data:
            self.cache.store("hashtags", cache_key, {"items": [vars(h) for h in data]})
        return data

    def get_trending_sounds(self, limit: int = 10) -> list[SoundData]:
        if self.cache:
            cached = self.cache.get("sounds", "global")
            if cached:
                return [SoundData(**s) for s in cached["items"]]

        if self.rapidapi_key:
            data = self._fetch_rapidapi_sounds(limit)
        else:
            data = self._demo_sounds(limit)

        if self.cache and data:
            self.cache.store("sounds", "global", {"items": [vars(s) for s in data]})
        return data

    def get_viral_videos(self, hashtag: str, niche_id: str, limit: int = 20) -> list[VideoData]:
        if self.cache:
            cached = self.cache.get("videos", f"{niche_id}_{hashtag}")
            if cached:
                return [VideoData(**v) for v in cached["items"]]

        if self.rapidapi_key:
            data = self._fetch_rapidapi_videos(hashtag, limit)
        else:
            data = self._demo_videos(hashtag, limit)

        if self.cache and data:
            self.cache.store("videos", f"{niche_id}_{hashtag}", {"items": [vars(v) for v in data]})
            for v in data:
                self.cache.store_video(niche_id, vars(v))
        return data

    def _fetch_rapidapi_hashtags(self, tags: list[str], limit: int) -> list[HashtagData]:
        results = []
        for tag in tags[:5]:
            try:
                url = f"https://{self.RAPIDAPI_HOST}/challenge/info"
                resp = self._session.get(url, params={"unique_id": tag.lstrip("#")}, timeout=10)
                if resp.status_code == 200:
                    info = resp.json().get("challengeInfo", {}).get("stats", {})
                    results.append(HashtagData(
                        tag=tag,
                        video_count=info.get("videoCount", 0),
                        view_count=info.get("viewCount", 0),
                        trending_score=min(100, info.get("viewCount", 0) / 1_000_000),
                        growth_rate_7d=random.uniform(5, 50),
                    ))
                time.sleep(1)
            except Exception:
                pass
        return results or self._demo_hashtags(tags, limit)

    def _fetch_rapidapi_sounds(self, limit: int) -> list[SoundData]:
        try:
            url = f"https://{self.RAPIDAPI_HOST}/music/trending"
            resp = self._session.get(url, params={"count": limit}, timeout=10)
            if resp.status_code == 200:
                items = resp.json().get("itemList", [])
                sounds = []
                for item in items[:limit]:
                    music = item.get("music", {})
                    sounds.append(SoundData(
                        sound_id=str(music.get("id", "")),
                        name=music.get("title", "Unknown"),
                        author=music.get("authorName", ""),
                        usage_count=music.get("playUrl", {}).get("duration", 0),
                        trending_score=random.uniform(60, 95),
                        genres=[],
                    ))
                return sounds
        except Exception:
            pass
        return self._demo_sounds(limit)

    def _fetch_rapidapi_videos(self, hashtag: str, limit: int) -> list[VideoData]:
        try:
            url = f"https://{self.RAPIDAPI_HOST}/challenge/videos"
            resp = self._session.get(
                url, params={"unique_id": hashtag.lstrip("#"), "count": limit}, timeout=15
            )
            if resp.status_code == 200:
                items = resp.json().get("itemList", [])
                videos = []
                for item in items[:limit]:
                    stats = item.get("stats", {})
                    music = item.get("music", {})
                    author = item.get("author", {})
                    desc = item.get("desc", "")
                    tags = [c.get("hashtagName", "") for c in item.get("challenges", [])]
                    dur = item.get("video", {}).get("duration", 0)
                    videos.append(VideoData(
                        video_id=str(item.get("id", "")),
                        description=desc,
                        hashtags=[f"#{t}" for t in tags if t],
                        views=stats.get("playCount", 0),
                        likes=stats.get("diggCount", 0),
                        comments=stats.get("commentCount", 0),
                        shares=stats.get("shareCount", 0),
                        duration_seconds=int(dur),
                        sound_name=music.get("title", ""),
                        sound_id=str(music.get("id", "")),
                        author_followers=author.get("followerCount", 0),
                        posted_at=str(item.get("createTime", "")),
                    ))
                return videos
        except Exception:
            pass
        return self._demo_videos(hashtag, limit)

    # ── Demo / fallback data ────────────────────────────────────────────────

    def _demo_hashtags(self, seed_tags: list[str], limit: int) -> list[HashtagData]:
        base = [
            ("airap", 8_500_000, 12_400_000_000, 94.2, 340.0),
            ("aimusic", 14_200_000, 28_600_000_000, 89.5, 120.0),
            ("aigenerated", 22_000_000, 45_000_000_000, 87.3, 85.0),
            ("aiart", 55_000_000, 110_000_000_000, 92.1, 45.0),
            ("dragon", 9_800_000, 19_500_000_000, 78.4, 30.0),
            ("aiartwork", 12_000_000, 24_000_000_000, 81.6, 55.0),
            ("artificialintelligence", 31_000_000, 62_000_000_000, 85.0, 25.0),
            ("aiprompts", 5_200_000, 8_900_000_000, 76.3, 180.0),
            ("midjourney", 18_000_000, 38_000_000_000, 83.7, 40.0),
            ("fyp", 800_000_000, 1_600_000_000_000, 99.0, 5.0),
            ("viral", 250_000_000, 500_000_000_000, 98.0, 8.0),
            ("raplyrics", 3_400_000, 5_800_000_000, 71.2, 90.0),
            ("digitalart", 40_000_000, 80_000_000_000, 79.8, 20.0),
            ("fantasyart", 7_600_000, 15_000_000_000, 74.5, 35.0),
            ("aidragon", 890_000, 1_200_000_000, 68.9, 220.0),
        ]
        return [
            HashtagData(tag=f"#{row[0]}", video_count=row[1], view_count=row[2],
                        trending_score=row[3], growth_rate_7d=row[4])
            for row in base[:limit]
        ]

    def _demo_sounds(self, limit: int) -> list[SoundData]:
        sounds = [
            ("7341829103", "Epic Dragon Orchestral", "AIBeats", 847_000, 94.5),
            ("8829301847", "Dark Rap Beat 2026", "TrapAI", 623_000, 88.2),
            ("3920481029", "Fantasy Epic Loop", "CinematicAI", 445_000, 82.7),
            ("5510293847", "Phonk Drift Wave", "PhonkMaster", 389_000, 79.4),
            ("2284710938", "Anime Slap Bass", "AnimeSound", 312_000, 75.1),
            ("9910283746", "Lo-Fi Chill Study", "ChillBeats", 285_000, 72.3),
            ("1124738291", "Hyperpop Glitch", "GlitchArt", 241_000, 68.9),
            ("6634819203", "Cinematic Tension Build", "MovieFX", 198_000, 65.4),
        ]
        return [
            SoundData(sound_id=s[0], name=s[1], author=s[2], usage_count=s[3],
                      trending_score=s[4], genres=["Electronic"])
            for s in sounds[:limit]
        ]

    def _demo_videos(self, hashtag: str, limit: int) -> list[VideoData]:
        templates = [
            ("POV: Ich hab KI gebeten einen Rap zu schreiben und das kam raus 🤖🎵", 2_840_000, 186_000, 12_400, 43_200, 27),
            ("Dieser KI-Drache hat mich aus dem Nichts komplett umgehauen 🐉✨", 1_920_000, 142_000, 8_900, 28_600, 22),
            ("Warte bis zum Ende... KI hat diesen Beat in 3 Sekunden gemacht", 4_100_000, 287_000, 18_900, 67_400, 31),
            ("Der Prompt der dieses Bild erzeugt hat kannst du dir nicht vorstellen", 890_000, 67_000, 4_200, 12_800, 18),
            ("KI Rap Teil 3 — Die Story geht weiter 🔥 (Part 1 im Profil)", 3_200_000, 228_000, 15_600, 51_000, 29),
            ("Ich hab 5 Stunden diesen KI-Drachen erschaffen — lohnt es sich?", 1_450_000, 98_000, 6_700, 19_400, 45),
            ("Dieser Midjourney Prompt funktioniert IMMER für epische Drachen", 2_100_000, 155_000, 9_800, 33_600, 24),
            ("KI vs Mensch: Wer rappt besser? 🤖🎤", 5_600_000, 412_000, 28_900, 98_700, 35),
        ]
        videos = []
        for i, (desc, views, likes, comments, shares, dur) in enumerate(templates[:limit]):
            videos.append(VideoData(
                video_id=f"demo_{hashtag}_{i}",
                description=desc,
                hashtags=[hashtag, "#fyp", "#viral", "#aiart"],
                views=views,
                likes=likes,
                comments=comments,
                shares=shares,
                duration_seconds=dur,
                sound_name=["Epic Dragon Orchestral", "Dark Rap Beat 2026", "Fantasy Epic Loop"][i % 3],
                sound_id=f"sound_{i}",
                author_followers=random.randint(1000, 50000),
                posted_at=datetime.now().isoformat(),
            ))
        return videos
