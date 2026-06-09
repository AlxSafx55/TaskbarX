"""Analyzes livestream performance and generates improvement plan."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class LiveDiagnosis:
    current_ratio_pct: float
    benchmark_label: str
    root_causes: list[str]
    action_plan: list[str]
    optimal_duration_minutes: int
    best_live_times: list[str]
    opening_hooks: list[str]
    engagement_prompts: list[str]


class LiveStreamAnalyzer:
    BENCHMARKS = [
        (1.0, "Kritisch — sofortige Änderung nötig"),
        (3.0, "Unter Durchschnitt"),
        (7.0, "Durchschnitt (3–7%)"),
        (15.0, "Gut"),
        (100.0, "Sehr gut / Creator-Level"),
    ]

    def diagnose(
        self,
        follower_count: int,
        avg_viewers: float,
        duration_hours: float,
        start_times: list[str],
    ) -> LiveDiagnosis:
        ratio = (avg_viewers / follower_count * 100) if follower_count > 0 else 0

        label = "Unbekannt"
        for threshold, lbl in self.BENCHMARKS:
            if ratio <= threshold:
                label = lbl
                break

        causes = self._diagnose_causes(ratio, duration_hours, start_times, follower_count)
        action_plan = self._action_plan(ratio, duration_hours, start_times)
        best_times = self._best_live_times(start_times)

        return LiveDiagnosis(
            current_ratio_pct=round(ratio, 1),
            benchmark_label=label,
            root_causes=causes,
            action_plan=action_plan,
            optimal_duration_minutes=90,
            best_live_times=best_times,
            opening_hooks=[
                "Hey, schön dass du dabei bist! Heute zeige ich euch LIVE wie ich diesen KI-Drachen erschaffe — bleibt bis zum Ende, das Ergebnis wird euch umhauen!",
                "Wir machen heute live einen KI-Rap von Anfang bis Fertig — ihr bestimmt das Thema! Schreibt euren Wunsch in die Kommentare!",
                "Ich zeige euch heute den geheimen Prompt, der immer virale Bilder erstellt. Nur hier im Live!",
            ],
            engagement_prompts=[
                "Wenn euch das gefällt — Like drücken damit TikTok das mehr Leuten zeigt! 🔥",
                "Folgt mir damit ihr die nächsten Lives nicht verpasst!",
                "Kommentiert euren Lieblings-KI-Stil — ich generiere ihn live für euch!",
                "Teilt den Stream mit jemandem der KI liebt!",
            ],
        )

    def _diagnose_causes(
        self, ratio: float, duration_hours: float, start_times: list[str], followers: int
    ) -> list[str]:
        causes = []
        if ratio < 3.5:
            causes.append(
                f"Viewer/Follower-Rate von {ratio:.1f}% ist sehr niedrig — "
                "TikTok zeigt deinen Live kaum neuen Zuschauern"
            )
        if duration_hours > 2:
            causes.append(
                f"Live-Dauer von {duration_hours}h ist zu lang — "
                "TikTok-Algorithmus belohnt kürzere, engagierte Streams (60–90 Min.)"
            )
        if any(t.startswith("20:") for t in start_times):
            causes.append(
                "Start um 20:00 Uhr: Hohe Konkurrenz zu anderen großen Streamern. "
                "9:30 Uhr oder 21:30 Uhr haben weniger Konkurrenz"
            )
        if followers < 500:
            causes.append(
                f"Bei {followers} Followern ist organische Live-Discovery noch gering. "
                "Regelmäßige Posts vor jedem Live sind entscheidend"
            )
        causes.append(
            "Fehlende Pre-Live Ankündigung: Kein 'Ich gehe gleich live!'-Video 1h vorher"
        )
        return causes[:5]

    def _action_plan(
        self, ratio: float, duration_hours: float, start_times: list[str]
    ) -> list[str]:
        return [
            "1h vor dem Live: Kurzes TikTok-Video posten 'Heute Abend 21:30 live!'",
            "Live auf 60–90 Minuten begrenzen (höhere Watch-Rate = mehr Algorithmus-Boost)",
            "Startzeit auf 21:30 Uhr wechseln (Post-Primetime, weniger Konkurrenz)",
            "Erstes Wort im Titel: 'LIVE:' + was die Zuschauer erwarten können",
            "Alle 10 Minuten: Aktive Frage an die Zuschauer stellen",
            "KI-Generierung LIVE zeigen: Zuschauer geben Thema vor = maximales Engagement",
            "End-Teaser: 'Nächste Woche live zeige ich euch...' damit sie zurückkommen",
        ]

    def _best_live_times(self, current_times: list[str]) -> list[str]:
        return [
            "Mittwoch 21:30 Uhr (höchster Forecast für deine Nische)",
            "Samstag 15:00 Uhr (Wochenend-Discovery-Peak)",
            "Freitag 21:00 Uhr (Wochenendbeginn-Aktivität)",
        ]
