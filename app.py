"""
Vertragsmanager KI - Streamlit-Hauptanwendung

Bietet ein mehrseitiges Dashboard für KI-gestütztes Vertragsmanagement.
"""

import streamlit as st
import sqlite3
import os
import yaml
from pathlib import Path

from processor.contract_analyzer import analyze_contract
from processor.clause_extractor import extract_clauses
from processor.deadline_tracker import get_upcoming_deadlines, get_deadline_stats


# --- Konfiguration laden ---
def load_config():
    """Lädt die Konfiguration aus settings.yaml."""
    config_path = Path("config/settings.yaml")
    example_path = Path("config/settings.example.yaml")

    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    elif example_path.exists():
        with open(example_path) as f:
            return yaml.safe_load(f)
    else:
        return {
            "ollama": {"base_url": "http://localhost:11434", "model": "llama3", "timeout": 120},
            "database": {"path": "data/vertraege.db"},
            "app": {"deadline_warning_days": 30},
        }


# --- Datenbank-Initialisierung ---
def init_database():
    """Erstellt die Datenbanktabelle falls nicht vorhanden."""
    db_path = Path(CONFIG["database"]["path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_path = Path("database/schema.sql")
    if schema_path.exists():
        conn = sqlite3.connect(str(db_path))
        with open(schema_path) as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()


def get_connection():
    """Gibt eine Datenbankverbindung zurück."""
    db_path = Path(CONFIG["database"]["path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path))


# --- Konfiguration global verfügbar machen ---
CONFIG = load_config()

# --- Datenbank initialisieren ---
init_database()

# --- Seitennavigation ---
st.set_page_config(
    page_title="Vertragsmanager KI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚖️ Vertragsmanager KI")
st.caption("KI-gestütztes Vertragsmanagement — DSGVO-konform & self-hosted")

# Seitenauswahl in der Sidebar
seite = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "📄 Vertrag analysieren", "⏰ Fristen", "📈 Berichte", "⚙️ Einstellungen"],
)

st.sidebar.divider()
st.sidebar.caption("🔒 Alle Daten bleiben lokal auf deinem Server.")


# ============================================================
# 📊 DASHBOARD
# ============================================================
if seite == "📊 Dashboard":
    st.header("📊 Dashboard")

    conn = get_connection()
    cur = conn.cursor()

    # Kennzahlen
    cur.execute("SELECT COUNT(*) FROM vertraege WHERE status = 'aktiv'")
    aktive_vertraege = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM vertraege")
    gesamt_vertraege = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM fristen WHERE status = 'offen' AND datum <= date('now', '+30 days')")
    anstehende_fristen = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM klauseln WHERE risiko_bewertung IN ('hoch', 'kritisch')")
    risikoklauseln = cur.fetchone()[0]

    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Aktive Verträge", aktive_vertraege)
    col2.metric("Gesamt", gesamt_vertraege)
    col3.metric("Anstehende Fristen", anstehende_fristen, delta=f"nächste 30 Tage")
    col4.metric("Risikoklauseln", risikoklauseln)

    st.divider()

    # Letzte Verträge
    st.subheader("Letzte Verträge")
    conn = get_connection()
    df = conn.execute(
        "SELECT titel, partei, vertragsart, status, startdatum, enddatum FROM vertraege ORDER BY erstellt_am DESC LIMIT 10"
    ).fetchall()
    conn.close()

    if df:
        import pandas as pd
        df_table = pd.DataFrame(
            df, columns=["Titel", "Partei", "Art", "Status", "Start", "Ende"]
        )
        st.dataframe(df_table, use_container_width=True, hide_index=True)
    else:
        st.info("Noch keine Verträge vorhanden. Lade einen Vertrag hoch, um zu starten.")

    # Fristen-Vorschau
    st.subheader("⏰ Nächste Fristen")
    fristen = get_upcoming_deadlines(30)
    if fristen:
        for f in fristen:
            st.write(f"**{f['beschreibung']}** — {f['datum']} (Vertrag: {f['vertrag_titel']})")
    else:
        st.info("Keine anstehenden Fristen in den nächsten 30 Tagen.")


# ============================================================
# 📄 VERTRAG ANALYSIEREN
# ============================================================
elif seite == "📄 Vertrag analysieren":
    st.header("📄 Vertrag analysieren")

    uploaded = st.file_uploader(
        "Vertrag hochladen (PDF, TXT)",
        type=["pdf", "txt"],
        help="Lade einen Vertrag hoch, um ihn von der KI analysieren zu lassen.",
    )

    if uploaded:
        with st.spinner("Vertrag wird analysiert..."):
            vertrag_text = uploaded.read().decode("utf-8", errors="replace")

            # KI-Analyse
            analyse = analyze_contract(
                vertrag_text,
                model=CONFIG["ollama"]["model"],
                base_url=CONFIG["ollama"]["base_url"],
            )

            st.subheader("Zusammenfassung")
            st.write(analyse.get("zusammenfassung", "Keine Zusammenfassung verfügbar."))

            # Klauseln extrahieren
            st.subheader("Extrahierte Klauseln")
            klauseln = extract_clauses(
                vertrag_text,
                model=CONFIG["ollama"]["model"],
                base_url=CONFIG["ollama"]["base_url"],
            )

            if klauseln:
                import pandas as pd
                df = pd.DataFrame(klauseln)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("Es konnten keine Klauseln automatisch extrahiert werden.")

        # In Datenbank speichern
        if st.button("Vertrag speichern"):
            titel = st.text_input("Vertragstitel", value=uploaded.name)
            if titel:
                conn = get_connection()
                conn.execute(
                    "INSERT INTO vertraege (titel, zusammenfassung) VALUES (?, ?)",
                    (titel, analyse.get("zusammenfassung", "")),
                )
                conn.commit()
                conn.close()
                st.success(f"Vertrag '{titel}' gespeichert!")


# ============================================================
# ⏰ FRISTEN
# ============================================================
elif seite == "⏰ Fristen":
    st.header("⏰ Fristenverwaltung")

    tage = st.slider("Zeitraum (Tage)", 7, 365, 90)
    fristen = get_upcoming_deadlines(tage)

    if fristen:
        import pandas as pd
        df = pd.DataFrame(fristen)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(f"Keine anstehenden Fristen in den nächsten {tage} Tagen.")

    # Statistiken
    stats = get_deadline_stats()
    if stats:
        st.divider()
        st.subheader("Statistiken")
        col1, col2, col3 = st.columns(3)
        col1.metric("Offene Fristen", stats.get("offen", 0))
        col2.metric("Erledigt", stats.get("erledigt", 0))
        col3.metric("Versäumt", stats.get("versaeumt", 0))


# ============================================================
# 📈 BERICHTE
# ============================================================
elif seite == "📈 Berichte":
    st.header("📈 Berichte")

    tab1, tab2 = st.tabs(["Risikoanalyse", "Vertragsübersicht"])

    with tab1:
        st.subheader("Risikobewertung der Klauseln")
        conn = get_connection()
        risiken = conn.execute(
            "SELECT risiko_bewertung, COUNT(*) as anzahl FROM klauseln GROUP BY risiko_bewertung"
        ).fetchall()
        conn.close()

        if risiken:
            import plotly.express as px
            import pandas as pd
            df = pd.DataFrame(risiken, columns=["Bewertung", "Anzahl"])
            fig = px.pie(df, values="Anzahl", names="Bewertung", color="Bewertung",
                         color_discrete_map={"niedrig": "green", "neutral": "gray",
                                             "hoch": "orange", "kritisch": "red"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Noch keine Klauseln analysiert.")

    with tab2:
        st.subheader("Verträge nach Art")
        conn = get_connection()
        arten = conn.execute(
            "SELECT vertragsart, COUNT(*) as anzahl FROM vertraege GROUP BY vertragsart"
        ).fetchall()
        conn.close()

        if arten:
            import plotly.express as px
            import pandas as pd
            df = pd.DataFrame(arten, columns=["Art", "Anzahl"])
            fig = px.bar(df, x="Art", y="Anzahl", color="Art")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Noch keine Verträge vorhanden.")


# ============================================================
# ⚙️ EINSTELLUNGEN
# ============================================================
elif seite == "⚙️ Einstellungen":
    st.header("⚙️ Einstellungen")

    st.subheader("Ollama-KI")
    st.write(f"Modell: `{CONFIG['ollama']['model']}`")
    st.write(f"URL: `{CONFIG['ollama']['base_url']}`")

    st.subheader("Fristenwarnung")
    st.write(f"Standardwarnung: {CONFIG['app'].get('deadline_warning_days', 30)} Tage vor Fristablauf")

    st.subheader("Datenbank")
    db_path = Path(CONFIG["database"]["path"])
    if db_path.exists():
        st.success(f"Datenbank vorhanden: `{CONFIG['database']['path']}`")
    else:
        st.warning("Datenbank noch nicht erstellt. Sie wird beim ersten Start automatisch angelegt.")

    st.divider()
    st.caption("Um die Einstellungen zu ändern, bearbeite `config/settings.yaml`.")
