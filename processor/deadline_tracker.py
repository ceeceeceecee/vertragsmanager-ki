"""
Vertragsmanager KI - Fristenverwaltung

Verwaltet Vertragsfristen, Kündigungsfristen und Verlängerungstermine.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_db_path() -> str:
    """Gibt den Pfad zur Datenbank zurück."""
    try:
        import yaml
        config_path = Path("config/settings.yaml")
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
            return config.get("database", {}).get("path", "data/vertraege.db")
    except Exception:
        pass
    return "data/vertraege.db"


def get_upcoming_deadlines(days: int = 30) -> list:
    """
    Gibt alle anstehenden Fristen zurück.

    Args:
        days: Anzahl der Tage in die Zukunft

    Returns:
        Liste von Fristen als Dicts
    """
    db_path = _get_db_path()
    path = Path(db_path)
    if not path.exists():
        return []

    try:
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT f.datum, f.beschreibung, f.art, f.status, v.titel as vertrag_titel
            FROM fristen f
            JOIN vertraege v ON f.vertrag_id = v.id
            WHERE f.status = 'offen'
              AND f.datum <= date('now', '+' || ? || ' days')
            ORDER BY f.datum ASC
            """,
            (days,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"Fehler beim Laden der Fristen: {e}")
        return []


def get_deadline_stats() -> dict:
    """
    Gibt Statistiken zu Fristen zurück.

    Returns:
        Dict mit Anzahlen pro Status
    """
    db_path = _get_db_path()
    path = Path(db_path)
    if not path.exists():
        return {}

    try:
        conn = sqlite3.connect(str(path))
        rows = conn.execute(
            "SELECT status, COUNT(*) as anzahl FROM fristen GROUP BY status"
        ).fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}
    except Exception as e:
        logger.error(f"Fehler beim Laden der Fristenstatistik: {e}")
        return {}


def add_deadline(vertrag_id: int, art: str, datum: str, beschreibung: str = "") -> bool:
    """
    Fügt eine neue Frist hinzu.

    Args:
        vertrag_id: ID des Vertrags
        art: Art der Frist (z.B. 'Kündigungsfrist')
        datum: Datum im Format YYYY-MM-DD
        beschreibung: Optionale Beschreibung

    Returns:
        True bei Erfolg
    """
    db_path = _get_db_path()
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(str(path))
        conn.execute(
            "INSERT INTO fristen (vertrag_id, art, datum, beschreibung) VALUES (?, ?, ?, ?)",
            (vertrag_id, art, datum, beschreibung),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen der Frist: {e}")
        return False
