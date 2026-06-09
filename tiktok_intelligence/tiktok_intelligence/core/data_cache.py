"""SQLite-backed cache with TTL support."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


class DataCache:
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS trending_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_type TEXT NOT NULL,
        niche TEXT NOT NULL,
        data_json TEXT NOT NULL,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL
    );
    CREATE TABLE IF NOT EXISTS video_metrics (
        video_id TEXT PRIMARY KEY,
        niche TEXT,
        views INTEGER,
        likes INTEGER,
        comments INTEGER,
        shares INTEGER,
        duration_seconds INTEGER,
        hashtags TEXT,
        sound_name TEXT,
        posted_at TIMESTAMP,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_date TEXT,
        report_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    def __init__(self, db_path: str = "./data/cache/cache.db"):
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(path)
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(self.SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def store(self, data_type: str, niche: str, data: dict, ttl_hours: int = 23) -> None:
        expires = datetime.utcnow() + timedelta(hours=ttl_hours)
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO trending_data (data_type, niche, data_json, expires_at) "
                "VALUES (?, ?, ?, ?)",
                (data_type, niche, json.dumps(data, ensure_ascii=False), expires.isoformat()),
            )

    def get(self, data_type: str, niche: str) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT data_json FROM trending_data "
                "WHERE data_type=? AND niche=? AND expires_at > ? "
                "ORDER BY fetched_at DESC LIMIT 1",
                (data_type, niche, datetime.utcnow().isoformat()),
            ).fetchone()
        if row:
            return json.loads(row[0])
        return None

    def store_video(self, niche: str, video: dict) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO video_metrics "
                "(video_id, niche, views, likes, comments, shares, duration_seconds, "
                "hashtags, sound_name, posted_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    video.get("id", ""),
                    niche,
                    video.get("views", 0),
                    video.get("likes", 0),
                    video.get("comments", 0),
                    video.get("shares", 0),
                    video.get("duration_seconds", 0),
                    json.dumps(video.get("hashtags", [])),
                    video.get("sound_name", ""),
                    video.get("posted_at", ""),
                ),
            )

    def get_recent_videos(self, niche: str, days: int = 7) -> list[dict]:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT video_id, views, likes, comments, shares, duration_seconds, "
                "hashtags, sound_name FROM video_metrics "
                "WHERE niche=? AND fetched_at > ? ORDER BY views DESC",
                (niche, cutoff),
            ).fetchall()
        return [
            {
                "id": r[0], "views": r[1], "likes": r[2], "comments": r[3],
                "shares": r[4], "duration_seconds": r[5],
                "hashtags": json.loads(r[6] or "[]"), "sound_name": r[7],
            }
            for r in rows
        ]

    def save_report(self, report_path: str) -> None:
        date = datetime.now().strftime("%Y-%m-%d")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO reports (report_date, report_path) VALUES (?, ?)",
                (date, report_path),
            )

    def get_latest_report(self) -> str | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT report_path FROM reports ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
        return row[0] if row else None

    def cleanup(self, keep_days: int = 30) -> None:
        cutoff = (datetime.utcnow() - timedelta(days=keep_days)).isoformat()
        with self._conn() as conn:
            conn.execute("DELETE FROM trending_data WHERE fetched_at < ?", (cutoff,))
            conn.execute("DELETE FROM video_metrics WHERE fetched_at < ?", (cutoff,))
