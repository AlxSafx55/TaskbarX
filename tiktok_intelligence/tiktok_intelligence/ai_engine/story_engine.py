"""Story engine: generates engaging video storylines with philosophical quotes and music."""
from __future__ import annotations
from dataclasses import dataclass, field

from .claude_client import ClaudeClient


@dataclass
class StoryScene:
    scene_number: int
    duration_seconds: int
    visual_description: str
    narration_or_text: str
    music_mood: str


@dataclass
class VideoStory:
    title: str
    hook_first_3_seconds: str
    total_duration_seconds: int
    scenes: list[StoryScene]
    philosophical_quote: str
    quote_source: str
    music_recommendation: str
    series_potential: bool
    teaser_for_next_part: str
    production_notes: str
    ai_prompts: dict[str, str] = field(default_factory=dict)


SYSTEM_PROMPT = """Du bist ein kreativer Direktor für virale KI-Content Videos auf TikTok.
Du spezialisierst dich auf:
- Fantasy/Action Storys mit epischer Atmosphäre
- Einbettung von philosophischen Weisheiten (Nietzsche, Sun Tzu, Marcus Aurelius, etc.)
- Sucht-erzeugende Struktur (Zuschauer können nicht aufhören zu schauen)
- KI-generierte Visuals und Rap-Musik Fusion
Antworte strukturiert auf Deutsch."""

PHILOSOPHICAL_QUOTES = [
    ("Wer mit Ungeheuern kämpft, mag zusehn, dass er nicht dabei zum Ungeheuer wird.", "Friedrich Nietzsche"),
    ("Kenne deinen Feind und kenne dich selbst — in hundert Schlachten wirst du nie besiegt sein.", "Sun Tzu"),
    ("Die Kraft kommt nicht vom Körper. Sie kommt vom unbesiegbaren Willen.", "Mahatma Gandhi"),
    ("Im Chaos liegt auch Gelegenheit.", "Sun Tzu"),
    ("Das Leben ist kurz, aber die Kunst ist lang.", "Hippokrates"),
    ("Ich bin kein Produkt meiner Umstände. Ich bin ein Produkt meiner Entscheidungen.", "Stephen Covey"),
    ("Wenn der Wind des Wandels weht, bauen manche Mauern — andere bauen Windmühlen.", "Chinesisches Sprichwort"),
]


class StoryEngine:
    def __init__(self, claude: ClaudeClient):
        self.claude = claude

    def generate_story(
        self,
        niche_id: str,
        topic: str,
        target_duration_seconds: int = 30,
        style: str = "fantasy-epic",
    ) -> VideoStory:
        import random
        quote, source = random.choice(PHILOSOPHICAL_QUOTES)

        prompt = (
            f"Erstelle eine virale TikTok-Video-Story:\n\n"
            f"THEMA: {topic}\n"
            f"NISCHE: {niche_id}\n"
            f"ZIEL-LÄNGE: {target_duration_seconds} Sekunden\n"
            f"STIL: {style}\n"
            f"PHILOSOPHISCHES ZITAT zum integrieren: \"{quote}\" — {source}\n\n"
            f"Erstelle:\n"
            f"1. HOOK (erste 3 Sekunden): Was sehen/hören die Zuschauer das sie SOFORT fesselt?\n"
            f"2. SZENEN: 3-4 kurze Szenen mit Beschreibung + KI-Prompt für jede Szene\n"
            f"3. WIE das Zitat integriert wird (Text-Overlay, Voiceover, oder im Rap?)\n"
            f"4. MUSIK-EMPFEHLUNG: Genre + Stimmung + Suno-Prompt\n"
            f"5. CLIFFHANGER: Wie endet das Video damit die Leute Teil 2 wollen?\n"
            f"6. PRODUKTION: Welche KI-Tools und wie?\n\n"
            f"Format: klar strukturiert mit Labels."
        )

        response = self.claude.complete(SYSTEM_PROMPT, prompt, max_tokens=1500)

        music_prompt = self._generate_music_prompt(niche_id, style)

        return VideoStory(
            title=f"{topic} — {style.title()} Story",
            hook_first_3_seconds=self._extract_section(response, "HOOK", "erste 3 Sekunden"),
            total_duration_seconds=target_duration_seconds,
            scenes=self._parse_scenes(response, target_duration_seconds),
            philosophical_quote=quote,
            quote_source=source,
            music_recommendation=music_prompt,
            series_potential=True,
            teaser_for_next_part=self._extract_section(response, "CLIFFHANGER"),
            production_notes=self._extract_section(response, "PRODUKTION"),
            ai_prompts={
                "midjourney": self._generate_visual_prompt(topic, style),
                "suno": music_prompt,
                "runway": self._generate_video_prompt(topic, style),
            },
        )

    def generate_series_preview(self, series_title: str, part_count: int = 3) -> str:
        prompt = (
            f"Erstelle ein Skript für ein kurzes 'Was kommt als nächstes' Preview-Video.\n\n"
            f"Serie: '{series_title}'\n"
            f"Anzahl Teile: {part_count}\n\n"
            f"Das Video soll:\n"
            f"- 15-20 Sekunden lang sein\n"
            f"- Kurze Szenen-Blitze zeigen\n"
            f"- Spannung aufbauen\n"
            f"- Mit 'Teil [N] kommt am [Tag]' enden\n\n"
            f"Gib mir das genaue Szenen-Skript."
        )
        return self.claude.complete(SYSTEM_PROMPT, prompt, max_tokens=600)

    def _generate_music_prompt(self, niche_id: str, style: str) -> str:
        prompts = {
            "ai-rap": "Dark trap beat, 140 BPM, 808 bass drops, aggressive AI vocalist, verse-chorus structure, cyberpunk theme, professional mix",
            "ai-visuals": "Epic orchestral, fantasy theme, soaring strings, powerful drums, cinematic trailer style, emotional build-up, Hans Zimmer inspired",
            "ai-prompts": "Lo-fi hip hop, mysterious ambient, glitch effects, futuristic synths, creative discovery mood, study-beats vibe",
        }
        return prompts.get(niche_id, "Epic cinematic, emotional, trending TikTok style")

    def _generate_visual_prompt(self, topic: str, style: str) -> str:
        return (
            f"Epic {style} scene depicting {topic}, cinematic lighting, ultra detailed, "
            f"volumetric fog, dramatic composition, --ar 9:16 --style raw --v 6.1"
        )

    def _generate_video_prompt(self, topic: str, style: str) -> str:
        return (
            f"Camera slowly reveals {topic} in {style} setting, "
            f"dramatic lighting shift, particles floating, epic atmosphere, 4K cinematic"
        )

    def _extract_section(self, text: str, *keywords: str) -> str:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            for kw in keywords:
                if kw.upper() in line.upper() and ":" in line:
                    remaining = line.split(":", 1)[-1].strip()
                    if remaining:
                        return remaining
                    # Get next non-empty line
                    for j in range(i + 1, min(i + 4, len(lines))):
                        if lines[j].strip():
                            return lines[j].strip()
        return text[:200] if text else "Keine Daten"

    def _parse_scenes(self, response: str, total_duration: int) -> list[StoryScene]:
        scene_duration = total_duration // 4
        return [
            StoryScene(
                scene_number=i,
                duration_seconds=scene_duration,
                visual_description=f"Szene {i} (aus KI-Analyse)",
                narration_or_text="",
                music_mood="Epic",
            )
            for i in range(1, 5)
        ]
