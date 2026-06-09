"""Comment assistant: suggests optimal replies to TikTok comments with keywords."""
from __future__ import annotations
from dataclasses import dataclass

from .claude_client import ClaudeClient


@dataclass
class CommentReply:
    original_comment: str
    suggested_reply: str
    keywords_used: list[str]
    strategy: str


SYSTEM_PROMPT = """Du bist ein TikTok-Community-Manager für einen KI-Content-Creator.
Deine Antworten sind:
- Kurz und authentisch (max. 2 Sätze)
- Enthalten natürlich eingebettete Keywords für den Algorithmus
- Persönlich und einladend (nicht generisch)
- Fördern Interaktion (Frage oder Call-to-Action)
Antworte immer auf Deutsch."""


class CommentAssistant:
    KEYWORD_POOL = {
        "ai-rap": ["KI-Rap", "AI-Musik", "AI-generiert", "KI-Lyrics", "AI-Beat"],
        "ai-visuals": ["KI-Art", "AI-Drache", "Midjourney", "KI-generiert", "AI-Fantasy"],
        "ai-prompts": ["KI-Prompt", "Midjourney", "AI-Kunst", "Prompt-Tipps", "AI-generiert"],
    }

    GENERIC_KEYWORDS = ["KI", "AI", "TikTok", "Content-Creator", "künstliche Intelligenz"]

    def __init__(self, claude: ClaudeClient):
        self.claude = claude

    def suggest_reply(self, comment: str, niche_id: str = "ai-rap") -> CommentReply:
        keywords = self.KEYWORD_POOL.get(niche_id, self.GENERIC_KEYWORDS)[:3]

        prompt = (
            f"Kommentar: \"{comment}\"\n\n"
            f"Nische: {niche_id}\n"
            f"Versuche diese Keywords natürlich einzubauen (wenn passend): {', '.join(keywords)}\n\n"
            f"Schreibe eine kurze, authentische Antwort (max. 2 Sätze) die:\n"
            f"1. Auf den Kommentar eingeht\n"
            f"2. Keywords natürlich verwendet\n"
            f"3. Mit einer Frage oder einem CTA endet\n\n"
            f"Antworte NUR mit dem Antworttext, nichts anderes."
        )

        reply_text = self.claude.complete(SYSTEM_PROMPT, prompt, max_tokens=200)

        return CommentReply(
            original_comment=comment,
            suggested_reply=reply_text,
            keywords_used=keywords,
            strategy="Engagement-Boost: Keywords + persönliche Note + CTA",
        )

    def bulk_suggestions(
        self, comments: list[str], niche_id: str = "ai-rap"
    ) -> list[CommentReply]:
        return [self.suggest_reply(c, niche_id) for c in comments]

    def get_cta_templates(self) -> dict[str, list[str]]:
        return {
            "like_follow": [
                "Wenn dir sowas gefällt — Folge mir für mehr KI-Content! 🤖✨",
                "Drück den Like wenn du mehr davon willst! 🔥",
            ],
            "share": [
                "Teile das mit jemandem der KI liebt! 🐉",
                "Kennst du jemanden der das sehen muss? ➡️",
            ],
            "save": [
                "Speichere das für später — ich mache bald Teil 2! 📌",
                "Speichere es damit du den Prompt nicht vergisst! 🔖",
            ],
            "comment": [
                "Was soll ich als nächstes mit KI erstellen? Schreib es unten! 👇",
                "Welches Thema soll die KI als nächstes rappen? 🎤",
            ],
        }
