# ⚖️ Vertragsmanager KI

> KI-gestütztes Vertragsmanagement für Unternehmen — DSGVO-konform, self-hosted, Open Source.

[![DSGVO-konform](https://img.shields.io/badge/DSGVO-konform-brightgreen)](https://dsgvo-gesetz.de)
[![Self-Hosted](https://img.shields.io/badge/Self_Hosted-✓-blue)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)]()
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)]()
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?logo=ollama)]()
[![License: MIT](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)

## ✨ Funktionen

- **📄 Vertrag analysieren** — KI-gestützte Analyse von Verträgen (PDF, DOCX, TXT)
- **🔍 Klauselerkennung** — Automatische Extraktion von Kündigungsfristen, Haftungsregelungen, Laufzeiten, Geheimhaltungsklauseln
- **⏰ Fristenmanagement** — Warnungen vor Ablauf von Kündigungsfristen und Vertragslaufzeiten
- **📊 Dashboard** — Übersicht über alle Verträge mit Status und Kennzahlen
- **📈 Berichte** — Vergleich von Verträgen gegen Best Practices
- **🔒 DSGVO-konform** — Alle Daten lokal, kein Cloud-LLM, Ollama als KI-Backend
- **🐳 Docker-Ready** — Ein Befehl zum Starten

## 🚀 Schnellstart

### Mit Docker (empfohlen)

```bash
git clone https://github.com/ceeceeceecee/vertragsmanager-ki.git
cd vertragsmanager-ki
cp config/settings.example.yaml config/settings.yaml
docker compose up -d
```

Die Anwendung ist dann unter **http://localhost:8501** erreichbar.

### Ohne Docker

```bash
# Voraussetzungen: Python 3.11+, Ollama installiert
git clone https://github.com/ceeceeceecee/vertragsmanager-ki.git
cd vertragsmanager-ki
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ollama Modell herunterladen
ollama pull llama3

# Konfiguration kopieren
cp config/settings.example.yaml config/settings.yaml

# Anwendung starten
streamlit run app.py
```

## ⚙️ Konfiguration

Kopiere `config/settings.example.yaml` nach `config/settings.yaml` und passe die Werte an:

```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "llama3"
  timeout: 120

database:
  path: "data/vertraege.db"

app:
  language: "de"
  max_upload_size_mb: 50
  deadline_warning_days: 30
```

## 📁 Projektstruktur

```
vertragsmanager-ki/
├── app.py                          # Streamlit-Hauptanwendung
├── requirements.txt                # Python-Abhängigkeiten
├── Dockerfile                      # Container-Image
├── docker-compose.yml              # App + Ollama Services
├── LICENSE                         # MIT-Lizenz
├── README.md
├── config/
│   └── settings.example.yaml       # Konfigurationsvorlage
├── processor/
│   ├── __init__.py
│   ├── contract_analyzer.py        # Ollama-Integration
│   ├── clause_extractor.py         # Klauselerkennung
│   └── deadline_tracker.py         # Fristenverwaltung
├── database/
│   └── schema.sql                  # SQLite-Schema
└── screenshots/
    ├── dashboard.png
    ├── vertrag_analysieren.png
    └── fristenuebersicht.png
```

## 🔒 Datenschutz & Sicherheit

- **100% lokal** — Keine Daten verlassen deinen Server
- **Keine Cloud-APIs** — Ollama als lokales LLM, kein OpenAI/ChatGPT
- **SQLite** — Datenbank lokal auf dem Server
- **Keine Telemetrie** — Keine Daten werden gesendet
- **MIT-Lizenz** — Open Source, prüfbar

## 🛠️ Tech Stack

| Komponente | Technologie |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| KI | [Ollama](https://ollama.ai) (lokales LLM) |
| Datenbank | SQLite |
| Container | Docker + Docker Compose |
| Sprache | Python 3.11+ |

## 📄 Lizenz

MIT — siehe [LICENSE](LICENSE).

---

*Entwickelt mit ❤️ für datenschutzfreundliches Vertragsmanagement.*
