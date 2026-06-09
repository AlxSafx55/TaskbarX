#!/bin/bash
# TikTok AI Growth Intelligence — Linux Setup Script

set -e
echo "========================================================"
echo "  TikTok AI Growth Intelligence System - Setup"
echo "========================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nicht gefunden. Bitte installiere Python 3.10+"
    exit 1
fi

echo "✅ Python gefunden: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Installiere Abhängigkeiten..."
pip3 install anthropic PyYAML python-dotenv click rich requests jinja2 pytz tenacity flask APScheduler

# Copy example config if settings.yaml doesn't exist
if [ ! -f "config/settings.yaml" ]; then
    cp config/settings.example.yaml config/settings.yaml
    echo "✅ Konfigurationsdatei erstellt: config/settings.yaml"
fi

# Create data directories
mkdir -p data/cache data/reports

echo ""
echo "========================================================"
echo "✅ Installation abgeschlossen!"
echo ""
echo "Nächste Schritte:"
echo "  1. python3 run.py setup       → Interaktive Einrichtung"
echo "  2. python3 run.py run         → Erste Analyse starten"
echo "  3. python3 run.py schedule    → Tägliche Automatisierung"
echo "========================================================"
