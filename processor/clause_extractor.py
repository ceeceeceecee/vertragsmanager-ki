"""
Vertragsmanager KI - Klauselerkennung

Extrahiert automatisch wichtige Klauseln aus Vertragstexten.
"""

import json
import logging

try:
    import ollama
except ImportError:
    ollama = None

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Du bist ein Experte für deutsches Vertragsrecht.
Extrahiere alle wichtigen Klauseln aus dem folgenden Vertragstext.

Antworte im JSON-Format als Array:
[
  {
    "klausel_typ": "Kündigungsfrist|Haftung|Laufzeit|Geheimhaltung|Gewährleistung|Zahlungsbedingungen|Sonstiges",
    "inhalt": "Wortlaut oder Zusammenfassung der Klausel",
    "risiko_bewertung": "niedrig|neutral|hoch|kritisch",
    "empfehlung": "Empfehlung oder Hinweis zur Klausel"
  }
]

Antworte AUSSCHLIESSLICH mit dem JSON-Array."""


def extract_clauses(text: str, model: str = "llama3", base_url: str = "http://localhost:11434") -> list:
    """
    Extrahiert Klauseln aus einem Vertragstext.

    Args:
        text: Der Vertragstext
        model: Ollama-Modellname
        base_url: Ollama-Server-URL

    Returns:
        Liste von Klauseln als Dicts
    """
    if ollama is None:
        logger.error("ollama-Paket nicht installiert")
        return []

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": text[:15000]},
            ],
            options={"temperature": 0.1},
        )

        content = response.get("message", {}).get("content", "[]")

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\[[\s\S]*\]', content)
            if match:
                return json.loads(match.group())
            return []

    except Exception as e:
        logger.error(f"Fehler bei der Klauselerkennung: {e}")
        return []
