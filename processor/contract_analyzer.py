import os
"""
Vertragsmanager KI - Vertragsanalyse via Ollama

Nutzt ein lokales LLM (Ollama) zur Analyse von Vertragstexten.
DSGVO-konform: Keine Daten verlassen den Server.
"""

import json
import logging

try:
    import ollama
except ImportError:
    ollama = None

logger = logging.getLogger(__name__)

# System-Prompt für die Vertragsanalyse (Deutsch)
SYSTEM_PROMPT = """Du bist ein Experte für deutsches Vertragsrecht.
Analysiere den gegebenen Vertragstext und gib deine Ergebnisse im folgenden JSON-Format zurück:

{
  "zusammenfassung": "Kurze Zusammenfassung des Vertrags in 2-3 Sätzen",
  "vertragsart": "Art des Vertrags (z.B. Dienstvertrag, Mietvertrag, Werkvertrag)",
  "parteien": ["Partei 1", "Partei 2"],
  "laufzeit": "Laufzeit des Vertrags",
  "kuendigungsfrist": "Kündigungsfrist",
  "risikobewertung": "niedrig|neutral|hoch|kritisch",
  "hinweise": ["Besondere Hinweise oder Auffälligkeiten"]
}

Antworte AUSSCHLIESSLICH mit dem JSON-Objekt, ohne zusätzlichen Text."""


def analyze_contract(text: str, model: str = "llama3", base_url: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")) -> dict:
    """
    Analysiert einen Vertragstext mit Ollama.

    Args:
        text: Der vollständige Vertragstext
        model: Name des Ollama-Modells
        base_url: URL des Ollama-Servers

    Returns:
        Dict mit Analyseergebnissen
    """
    if ollama is None:
        logger.error("ollama-Paket nicht installiert. Bitte: pip install ollama")
        return {"zusammenfassung": "Fehler: Ollama nicht verfügbar.", "fehler": True}

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text[:15000]},  # Token-Limit berücksichtigen
            ],
            options={"temperature": 0.1},  # Deterministisch für Analyse
        )

        # JSON aus der Antwort extrahieren
        content = response.get("message", {}).get("content", "{}")

        # Versuche, JSON zu parsen
        try:
            result = json.loads(content)
            result["fehler"] = False
            return result
        except json.JSONDecodeError:
            # Versuche, JSON aus dem Text zu extrahieren
            import re
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                result = json.loads(match.group())
                result["fehler"] = False
                return result

            return {
                "zusammenfassung": content[:500],
                "fehler": False,
                "hinweis": "KI-Antwort konnte nicht als JSON geparst werden.",
            }

    except Exception as e:
        logger.error(f"Fehler bei der Vertragsanalyse: {e}")
        return {"zusammenfassung": f"Fehler bei der Analyse: {str(e)}", "fehler": True}
