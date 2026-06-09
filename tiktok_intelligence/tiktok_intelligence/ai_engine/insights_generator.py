"""Generates all AI insights for the daily report."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .claude_client import ClaudeClient
from ..analyzers.viral_analyzer import ViralPatterns
from ..analyzers.hashtag_optimizer import HashtagBundle
from ..analyzers.livestream_analyzer import LiveDiagnosis
from ..core.config_manager import NicheConfig, AppConfig


SYSTEM_PROMPT = """Du bist ein erfahrener TikTok-Wachstumsstratege mit tiefem Wissen über:
- TikToks Empfehlungsalgorithmus (FYP-Mechanik)
- KI-generierte Inhalte (Rap, visuelle Kunst, Prompts)
- Virale Content-Muster in kreativen Nischen
- Livestream-Optimierung auf TikTok
- Fantasy/Action Storytelling mit philosophischen Weisheiten

Gib IMMER spezifische, umsetzbare Ratschläge auf Deutsch. Vermeide allgemeine Tipps.
Berücksichtige immer: Dieser Creator arbeitet 3-9 Stunden pro Video — jedes Video muss strategisch sein.
Antworte präzise und formatiert mit Emojis für bessere Lesbarkeit."""


@dataclass
class VideoIdea:
    title: str
    concept: str
    hook: str
    caption_template: str
    production_time_estimate: str
    best_post_day: str
    best_post_time: str


@dataclass
class DailyInsights:
    date: str
    niche_analyses: dict[str, str] = field(default_factory=dict)
    content_ideas: dict[str, list[VideoIdea]] = field(default_factory=dict)
    trend_opportunities: str = ""
    livestream_advice: str = ""
    content_calendar: str = ""
    upload_guide: dict[str, str] = field(default_factory=dict)
    profile_advice: str = ""
    brand_protection: str = ""
    prompt_recommendations: str = ""
    growth_roadmap_text: str = ""
    cost_estimate: str = ""


class InsightsGenerator:
    def __init__(self, claude: ClaudeClient, config: AppConfig):
        self.claude = claude
        self.config = config

    def generate_full_insights(
        self,
        viral_patterns: dict[str, ViralPatterns],
        hashtag_bundles: dict[str, list[HashtagBundle]],
        live_diagnosis: LiveDiagnosis,
    ) -> DailyInsights:
        insights = DailyInsights(date=datetime.now().strftime("%d. %B %Y"))

        for niche in self.config.niches:
            patterns = viral_patterns.get(niche.id)
            if patterns:
                insights.niche_analyses[niche.id] = self._analyze_niche(niche, patterns)
                insights.content_ideas[niche.id] = self._generate_ideas(niche, patterns)

        insights.trend_opportunities = self._trend_opportunities(viral_patterns)
        insights.livestream_advice = self._livestream_advice(live_diagnosis)
        insights.content_calendar = self._content_calendar()
        insights.upload_guide = self._upload_guide()
        insights.profile_advice = self._profile_advice()
        insights.brand_protection = self._brand_protection()
        insights.prompt_recommendations = self._prompt_recommendations()
        insights.growth_roadmap_text = self._growth_roadmap()
        insights.cost_estimate = self.claude.get_cost_estimate()

        return insights

    def _analyze_niche(self, niche: NicheConfig, patterns: ViralPatterns) -> str:
        prompt = f"""Analysiere diese TikTok-Daten für die Nische "{niche.display_name}":

VIRALE MUSTER:
- Durchschnittliche Engagement-Rate: {patterns.benchmarks.avg_engagement_rate:.1%}
- Median Views: {patterns.benchmarks.median_views:,}
- Optimale Video-Länge: {patterns.duration.optimal_min_seconds}–{patterns.duration.optimal_max_seconds} Sekunden
- Top-Hashtags: {', '.join(patterns.top_hashtags[:6])}
- Trending Sounds: {', '.join(patterns.top_sounds[:3])}
- Hook-Muster: {', '.join(patterns.hook_patterns[:4])}
- Viraler Score Ø: {patterns.viral_score_avg}/100

TOP-VIDEOS IN DER NISCHE:
{self._format_top_videos(patterns.top_videos)}

CREATOR-KONTEXT:
- Nische: {niche.description}
- Produktionszeit: {niche.production_hours_per_video}h pro Video
- Character/Stil: {niche.character_description or 'noch nicht definiert'}

Bitte gib mir:
1. Die 3 wichtigsten Erkenntnisse was diese Woche in dieser Nische viral macht
2. Den einzigen wichtigsten Trend den er DIESE WOCHE nutzen sollte (mit Begründung)
3. Ein konkretes Hook-Beispiel speziell für {niche.display_name}
4. Die Caption-Formel die am besten funktioniert

Sei sehr spezifisch. Keine allgemeinen Tipps."""

        return self.claude.complete(SYSTEM_PROMPT, prompt, max_tokens=1200)

    def _generate_ideas(self, niche: NicheConfig, patterns: ViralPatterns) -> list[VideoIdea]:
        prompt = f"""Erstelle 5 konkrete Video-Ideen für die Nische "{niche.display_name}".

CONTEXT:
- Trending Sounds: {', '.join(patterns.top_sounds[:3])}
- Viral Hashtags: {', '.join(patterns.top_hashtags[:5])}
- Optimale Länge: {patterns.duration.optimal_min_seconds}–{patterns.duration.optimal_max_seconds}s
- Produktionszeit des Creators: {niche.production_hours_per_video}h
- Stil-Keywords: {', '.join(niche.style_keywords)}

Für jede Idee gib exakt folgendes Format:
IDEE [N]:
Titel: [Video-Titel]
Konzept: [1-2 Sätze was zu sehen ist]
Hook (erste 2 Sek): [exakter Satz/Text]
Caption-Template: [fertige Caption mit [PLATZHALTERN]]
Produktionszeit: [Schätzung in Stunden]
Bester Wochentag: [Tag + Uhrzeit]"""

        response = self.claude.complete(SYSTEM_PROMPT, prompt, max_tokens=1500)
        return self._parse_video_ideas(response)

    def _trend_opportunities(self, patterns: dict[str, ViralPatterns]) -> str:
        niche_summary = "\n".join([
            f"- {p.niche_name}: {p.sample_count} Videos analysiert, "
            f"Viral-Score Ø {p.viral_score_avg}/100"
            for p in patterns.values()
        ])
        prompt = f"""Basierend auf diesen analysierten Nischen:
{niche_summary}

Beschreibe:
1. Die 2 größten Trend-Opportunities der nächsten 48 Stunden
2. Einen Trend der GERADE abstirbt (vermeiden!)
3. Einen überraschenden Schnittmengen-Trend zwischen den Nischen

Formuliere konkrete, umsetzbare Empfehlungen mit Zeitfenster."""

        return self.claude.complete(SYSTEM_PROMPT, prompt, max_tokens=800)

    def _livestream_advice(self, diagnosis: LiveDiagnosis) -> str:
        prompt = f"""Ein TikTok-Creator hat folgendes Livestream-Problem:
- {diagnosis.current_ratio_pct}% Viewer/Follower-Rate (Benchmark: 3–7% = Durchschnitt)
- Status: {diagnosis.benchmark_label}
- Typische Stream-Dauer: zu lang
- Ursachen: {'; '.join(diagnosis.root_causes[:3])}

Erstelle einen SEHR KONKRETEN Aktionsplan:
1. Was muss er als ERSTES ändern? (größter Impact)
2. Skript für die erste Minute des nächsten Lives
3. Was sagen wenn niemand kommt (Motivationstaktik)
4. Wie man 10 Zuschauer zum Teilen bringt
5. Idealer Live-Aufbau für KI-Content-Creators (30 Min. Struktur)"""

        return self.claude.complete(SYSTEM_PROMPT, prompt, max_tokens=1000)

    def _content_calendar(self) -> str:
        days = []
        today = datetime.now()
        day_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        niches_cycle = [n.display_name for n in self.config.niches]

        for i in range(7):
            day = today + timedelta(days=i)
            day_name = day_names[day.weekday()]
            niche = niches_cycle[i % len(niches_cycle)] if niches_cycle else "Nische"
            is_best = day.weekday() in [1, 3]  # Dienstag, Donnerstag
            is_live = day.weekday() == 2  # Mittwoch
            marker = " 🌟 BESTER TAG" if is_best else ""
            live_note = "\n         🔴 LIVE: 21:30 Uhr (90 Min.)" if is_live else ""
            days.append(
                f"{day_name} {day.strftime('%d.%m.')}{marker}: "
                f"📱 {niche} — 19:00 Uhr posten{live_note}"
            )

        return "\n".join(days)

    def _upload_guide(self) -> dict[str, str]:
        return {
            "video_settings": (
                "✅ Auflösung: 1080×1920 (9:16 Hochformat)\n"
                "✅ Codec: H.264, mindestens 30fps (60fps wenn möglich)\n"
                "✅ Audio: 44.1kHz Stereo\n"
                "✅ Max. Dateigröße: 287MB\n"
                "❌ KEIN Wasserzeichen anderer Plattformen (Instagram-Logo killt die Reichweite!)"
            ),
            "caption_formula": (
                "Zeile 1: Hook-Satz (max. 8 Wörter) — muss Neugier wecken\n"
                "Zeile 2: 1-2 Sätze über den KI-Prozess (zeigt Expertise)\n"
                "Zeile 3: Call-to-Action ('Folge für mehr KI [Nische]')\n"
                "Hashtags: Bundle A oder B aus dem Bericht oben"
            ),
            "sound_tip": (
                "🎵 Trending Sound = +30% mehr Reichweite vom Algorithmus\n"
                "🎵 Original Audio (eigener Rap) = Algorithmus boosted Original-Creator\n"
                "➡️ Für KI-Rap: Original Audio verwenden!\n"
                "➡️ Für visuelle Videos: Trending Sound aus Liste oben nehmen"
            ),
            "posting_checklist": (
                "□ Video-Datei: max 287MB, 9:16, H.264\n"
                "□ Caption geschrieben (Hook + Beschreibung + CTA)\n"
                "□ Hashtag-Bundle kopiert (Bundle A oder B)\n"
                "□ Trending Sound ausgewählt (oder Original)\n"
                "□ Cover-Frame: bestes Standbild des Videos\n"
                "□ Zeitplan: auf optimale Posting-Zeit einstellen\n"
                "□ Kommentare erste 30 Min. im Auge behalten und antworten"
            ),
        }

    def _profile_advice(self) -> str:
        prompt = f"""Ein KI-Content-Creator auf TikTok (100 Follower) möchte sein Profil optimieren.
Nischen: {', '.join(n.display_name for n in self.config.niches)}

Erstelle:
1. 5 TikTok-Nutzernamen (kurz, merkbar, SEO-stark, zeigt Nische)
2. 3 Bio-Varianten (Kurz/SEO/Story)
3. Profilbild-Empfehlung (KI-generiertes Bild — beschreibe es)
4. Link-in-Bio Strategie

Format: klar strukturiert mit Labels."""

        return self.claude.complete(SYSTEM_PROMPT, prompt, max_tokens=800)

    def _brand_protection(self) -> str:
        return (
            "🛡️ DEIN MARKEN-SCHUTZ-SYSTEM:\n\n"
            "1. Logo: Lass Claude/Midjourney ein einzigartiges Logo für deinen Channel generieren\n"
            "   Prompt-Idee: 'Minimalist logo for AI content creator, dragon + circuit board, dark background'\n\n"
            "2. Wasserzeichen-Strategie:\n"
            "   • Position: Untere rechte Ecke (20px Abstand zum Rand)\n"
            "   • Größe: 8-10% der Videofläche\n"
            "   • Transparenz: 60-70% (sichtbar aber nicht störend)\n\n"
            "3. Stil-Bibel:\n"
            "   • Lege JETZT Farben, Schriftart und Charakter-Details fest\n"
            "   • Speichere Master-Prompts für konsistente Charaktere\n"
            "   • Gleicher Outro-Sound auf jedem Video = Wiedererkennungswert\n\n"
            "4. Unsichtbarer Schutz:\n"
            "   • Einzigartige Stil-Kombination die nur du verwendest\n"
            "   • Kleine Details die Kopien sofort als Fakes erkennbar machen"
        )

    def _prompt_recommendations(self) -> str:
        return (
            "🤖 KI-PROMPT-BIBLIOTHEK FÜR DEINE TOOLS:\n\n"
            "MIDJOURNEY (Drachen/Fantasy):\n"
            "`epic dragon flying through neon-lit cyberpunk city, cinematic lighting, "
            "ultra detailed scales, volumetric fog, --ar 9:16 --style raw --v 6.1`\n\n"
            "SUNO (Rap-Musik):\n"
            "`Dark trap beat, 140 BPM, 808 bass, AI vocalist, verse-chorus-verse structure, "
            "aggressive delivery, cyberpunk theme, professional mix`\n\n"
            "RUNWAY GEN-3 (Video-Animation):\n"
            "`Dragon takes off from mountain peak, camera tracks movement, "
            "epic cinematic shot, golden hour lighting, dust particles`\n\n"
            "DALL-E 3 (Rap-Artist Visuals):\n"
            "`AI rapper in futuristic studio, holographic microphone, "
            "neon lights, digital elements floating, ultra-realistic, 9:16 format`\n\n"
            "⚠️ KONSISTENZ-TRICK: Speichere für deinen Hauptcharakter einen 'Seed' oder "
            "'Style Reference' — dann sieht er in jedem Video identisch aus!"
        )

    def _growth_roadmap(self) -> str:
        lines = ["📍 DEINE WACHSTUMS-ROADMAP:\n"]
        current = self.config.follower_count
        for milestone in self.config.growth_milestones:
            target = milestone.get("followers", 0)
            icon = "✅" if current >= target else ("🔄" if current >= target * 0.5 else "⏳")
            lines.append(f"{icon} {target:,} Follower:")
            for action in milestone.get("actions", []):
                lines.append(f"   → {action}")
            lines.append("")
        return "\n".join(lines)

    def _format_top_videos(self, videos: list[dict]) -> str:
        if not videos:
            return "Keine Video-Daten"
        lines = []
        for i, v in enumerate(videos[:3], 1):
            lines.append(
                f"{i}. '{v['description'][:80]}' — "
                f"{v['views']:,} Views, {v['engagement_rate']}% Engagement, "
                f"{v['duration']}s, Sound: {v['sound']}"
            )
        return "\n".join(lines)

    def _parse_video_ideas(self, response: str) -> list[VideoIdea]:
        ideas = []
        if "[DEMO-MODUS" in response:
            for i in range(3):
                ideas.append(VideoIdea(
                    title=f"Demo-Idee {i+1}",
                    concept="KI-generierter Content mit aktuellem Trend",
                    hook="POV: KI hat das in 3 Sekunden gemacht...",
                    caption_template="[Dein Hook] 🤖✨ [Beschreibung] | Folge für mehr KI-Content!",
                    production_time_estimate="4-6h",
                    best_post_day="Dienstag",
                    best_post_time="19:00 Uhr",
                ))
            return ideas

        blocks = response.split("IDEE ")
        for block in blocks[1:]:
            lines = {
                k.strip().lower(): v.strip()
                for line in block.strip().split("\n")
                if ":" in line
                for k, v in [line.split(":", 1)]
            }
            ideas.append(VideoIdea(
                title=lines.get("titel", ""),
                concept=lines.get("konzept", ""),
                hook=lines.get("hook (erste 2 sek)", lines.get("hook", "")),
                caption_template=lines.get("caption-template", ""),
                production_time_estimate=lines.get("produktionszeit", ""),
                best_post_day=lines.get("bester wochentag", ""),
                best_post_time="",
            ))
        return ideas or [VideoIdea("", "", "", "", "", "", "")]
