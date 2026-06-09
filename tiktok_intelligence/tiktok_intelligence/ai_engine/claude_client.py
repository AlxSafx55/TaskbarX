"""Anthropic Claude API client with retry logic."""
from __future__ import annotations
import time
from typing import Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ClaudeClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        self._client = None
        if api_key and ANTHROPIC_AVAILABLE:
            self._client = anthropic.Anthropic(api_key=api_key)

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        if not self._client:
            return self._demo_response(user_message)

        for attempt in range(3):
            try:
                resp = self._client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                )
                self.session_input_tokens += resp.usage.input_tokens
                self.session_output_tokens += resp.usage.output_tokens
                return resp.content[0].text
            except Exception as e:
                if attempt == 2:
                    return f"[Claude API Fehler: {e}]"
                time.sleep(2 ** attempt)
        return ""

    def get_cost_estimate(self) -> str:
        input_cost = (self.session_input_tokens / 1_000_000) * 3.0
        output_cost = (self.session_output_tokens / 1_000_000) * 15.0
        total = input_cost + output_cost
        return f"~€{total:.3f} ({self.session_input_tokens} input / {self.session_output_tokens} output tokens)"

    def _demo_response(self, message: str) -> str:
        return (
            "[DEMO-MODUS — kein Anthropic API-Key gesetzt]\n\n"
            "Um echte KI-Insights zu erhalten, füge deinen API-Key in config/settings.yaml ein.\n"
            "Hole deinen kostenlosen Key unter: https://console.anthropic.com\n\n"
            "Was du hier sehen würdest:\n"
            "• Konkrete Video-Ideen für deine Nische basierend auf aktuellen Trends\n"
            "• Spezifische Hook-Formeln die viral gehen\n"
            "• Diagnose warum deine Videos nicht viral werden\n"
            "• Persönlicher Upload-Guide mit Hashtag-Bundle und Posting-Zeitpunkt"
        )
