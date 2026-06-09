# Skills — TikTok AI Growth Intelligence

Jeder Skill wird durch seinen Namen aktiviert.
Schreibe einfach den Skill-Namen in deine Nachricht, z.B.:
> "#TREND-SCAN — was ist heute viral?"

---

## SKILL 01 — #TREND-SCAN
**Aufgabe:** Suche täglich nach aktuellen TikTok-Trends im Web.

**Aktivierung:** `#TREND-SCAN`

**Ausführung:**
1. Suche im Web nach "TikTok trending today [Datum]"
2. Suche nach "TikTok viral sounds this week"
3. Suche nach "trending hashtags TikTok [Nische]"
4. Gib aus:
   - Top 5 virale Hashtags heute (mit geschätzten Views)
   - Top 3 Trending Sounds (Name + wie viele Videos)
   - 1 großer Trend der JETZT gerade aufsteigt
   - Trend der GERADE stirbt (vermeiden)
5. Übergib Ergebnisse an → **ContentAgent** für Video-Ideen

**Zugriff durch Agenten:** TrendAgent, ContentAgent

---

## SKILL 02 — #IDEEN-GENERATOR
**Aufgabe:** Generiere konkrete Video-Ideen basierend auf Trends.

**Aktivierung:** `#IDEEN-GENERATOR [Nische]`

**Ausführung:**
1. Rufe zuerst #TREND-SCAN auf
2. Passe Trends an die genannte Nische an
3. Erstelle 5 Video-Konzepte mit:
   - Titel
   - Hook (erste 3 Sekunden — exakter Text)
   - Kurzbeschreibung (2 Sätze)
   - Geschätzte Produktionszeit
   - Viral-Wahrscheinlichkeit (0–100)
4. Ranke die 5 Ideen nach Viral-Potenzial
5. Übergib Top-Idee an → **ContentAgent** für vollständige Story

**Zugriff durch Agenten:** ContentAgent, TrendAgent

---

## SKILL 03 — #STORY-BUILDER
**Aufgabe:** Erstelle vollständige Video-Storyline mit philosophischem Zitat.

**Aktivierung:** `#STORY-BUILDER [Thema]`

**Ausführung:**
1. Wähle passendes philosophisches Zitat (Nietzsche, Sun Tzu, Marcus Aurelius, Seneca)
2. Erstelle Szenen-Struktur:
   - Szene 1 (0–5s): Hook — fesselt sofort
   - Szene 2 (5–15s): Aufbau — Spannung steigt
   - Szene 3 (15–25s): Höhepunkt — Philosophisches Zitat erscheint
   - Szene 4 (25–30s): Cliffhanger — Zuschauer will Teil 2
3. Erstelle Midjourney-Prompt für jede Szene
4. Erstelle Suno-Prompt für passende Musik
5. Übergib an → **PromptAgent** für Tool-spezifische Optimierung

**Zugriff durch Agenten:** ContentAgent

---

## SKILL 04 — #HASHTAG-PROFI
**Aufgabe:** Erstelle optimierte Hashtag-Bundles in 3 Varianten.

**Aktivierung:** `#HASHTAG-PROFI [Nische] [Video-Thema]`

**Ausführung:**
1. Rufe #TREND-SCAN auf für aktuelle Trending-Tags
2. Erstelle 3 Bundles:

**Bundle A — Maximale Reichweite (10 Tags):**
- 2 Mega-Tags (1B+ Views): #fyp #viral
- 3 Nischen-Tags (100M–1B): passend zur Nische
- 3 Trend-Tags (aktuell trending)
- 2 Content-Tags (Video-spezifisch)

**Bundle B — Nischen-Community (8 Tags):**
- 5 spezifische Nischen-Tags
- 2 Community-Tags
- 1 Micro-Tag (unter 50M, gutes Ranking möglich)

**Bundle C — Discovery Mix (7 Tags):**
- 2 Trending + 3 Nische + 1 Micro + 1 Mega

3. Alle Bundles fertig zum Kopieren ausgeben
4. Für jeden Haupt-Tag eine Alternative angeben (größer/kleiner/trending)

**Zugriff durch Agenten:** ContentAgent, TrendAgent

---

## SKILL 05 — #HOOK-MASTER
**Aufgabe:** Erstelle unwiderstehliche Hooks für die ersten 3 Sekunden.

**Aktivierung:** `#HOOK-MASTER [Thema] [Nische]`

**Ausführung:**
1. Analysiere was in dieser Nische viral geht
2. Erstelle 5 verschiedene Hook-Typen:
   - **POV-Hook:** "POV: KI hat gerade..."
   - **Schock-Hook:** "Das hätte ich nie erwartet..."
   - **Neugier-Hook:** "Warte bis du das siehst..."
   - **Frage-Hook:** "Was würdest du tun wenn..."
   - **Zitat-Hook:** Philosophisches Zitat direkt am Anfang
3. Bewerte jeden Hook (0–100 Viral-Score)
4. Gib den besten Hook als Empfehlung aus
5. Erkläre WARUM dieser Hook funktioniert

**Zugriff durch Agenten:** ContentAgent

---

## SKILL 06 — #PROMPT-MEISTER
**Aufgabe:** Optimiere Prompts für jedes KI-Tool.

**Aktivierung:** `#PROMPT-MEISTER [Tool] [Beschreibung]`

**Unterstützte Tools:** Midjourney, DALL-E, Grok Aurora, Gemini, Suno, Udio, Runway, Kling, Sora

**Ausführung:**
1. Erkenne welches Tool genutzt wird
2. Wende tool-spezifische Syntax an:
   - Midjourney: `--ar 9:16 --v 6.1 --style raw --q 2`
   - Suno: BPM + Genre + Stimmung + Struktur
   - Runway: Kamera-Bewegung + Licht + Atmosphäre
   - Grok Aurora: Detaillierte Atmosphäre-Beschreibung
3. Füge Konsistenz-Parameter hinzu (damit Charakter gleich bleibt)
4. Gib 3 Varianten aus (Standard / Episch / Experimentell)

**Zugriff durch Agenten:** ContentAgent, TrendAgent

---

## SKILL 07 — #KOMMENTAR-COACH
**Aufgabe:** Schlage optimale Kommentar-Antworten vor.

**Aktivierung:** `#KOMMENTAR-COACH [Kommentar einfügen]`

**Ausführung:**
1. Analysiere den Kommentar (positiv/negativ/Frage/Lob)
2. Erstelle 3 Antwort-Varianten:
   - **Kurz (unter 20 Zeichen):** Emoji-Reaktion + 1 Wort
   - **Mittel (20–80 Zeichen):** Persönlich + 1 Keyword + CTA
   - **Lang (80+ Zeichen):** Vollständige Antwort mit Mehrwert + Keyword + Frage
3. Baue diese Keywords natürlich ein: KI, AI, TikTok, [Nische]
4. Ende immer mit Frage oder Follow-CTA
5. Markiere welche Antwort den Algorithmus am meisten boosted

**Zugriff durch Agenten:** CommentAgent

---

## SKILL 08 — #LIVE-COACH
**Aufgabe:** Optimiere Livestream-Strategie und gib Live-Support.

**Aktivierung:** `#LIVE-COACH`

**Ausführung:**
1. Prüfe aktuelle Zuschauer-Situation (aus Kontext)
2. Gib sofort umsetzbare Aktionen aus:
   - Opening-Hook-Skript (erste 60 Sekunden)
   - Engagement-Prompts (alle 10 Minuten)
   - CTA-Rotation (Like / Folgen / Teilen / Speichern)
   - Themen-Ideen falls Live stockt
   - Cliffhanger für nächstes Live
3. Diagnose: Warum kommen wenig Zuschauer?
4. Optimaler Live-Zeitplan für diese Woche

**Zugriff durch Agenten:** LiveAgent

---

## SKILL 09 — #PERFORMANCE-CHECK
**Aufgabe:** Analysiere was funktioniert hat und was nicht.

**Aktivierung:** `#PERFORMANCE-CHECK [Video-Ergebnis einfügen]`

**Ausführung:**
1. Vergleiche Ergebnis mit Erwartung
2. Analysiere:
   - War der Hook stark genug?
   - Waren Hashtags optimal?
   - War die Posting-Zeit richtig?
   - War die Video-Länge optimal?
3. Gib konkrete Verbesserungen für das nächste Video
4. Update die Strategie: Was soll mehr/weniger gemacht werden?
5. Übergib Erkenntnisse an → alle Agenten

**Zugriff durch Agenten:** AnalysisAgent

---

## SKILL 10 — #UPLOAD-GUIDE
**Aufgabe:** Erstelle kompletten Upload-Guide für ein spezifisches Video.

**Aktivierung:** `#UPLOAD-GUIDE [Video-Beschreibung]`

**Ausführung:**
1. Rufe #HASHTAG-PROFI auf
2. Rufe #HOOK-MASTER auf
3. Erstelle vollständigen Guide:
   - Video-Einstellungen (1080x1920, H.264, 30fps)
   - Fertige Caption (copy-paste bereit)
   - Hashtag-Bundle (copy-paste bereit)
   - Bester Posting-Tag + Uhrzeit
   - Sound-Empfehlung
   - Cover-Frame Tipp
   - Erste 30 Minuten nach Upload: was tun?

**Zugriff durch Agenten:** ContentAgent, AnalysisAgent
