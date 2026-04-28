-- SQLite-Schema für Vertragsmanager KI

CREATE TABLE IF NOT EXISTS vertraege (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    partei TEXT,
    vertragsart TEXT,
    status TEXT DEFAULT 'aktiv' CHECK(status IN ('aktiv', 'gekündigt', 'abgelaufen', 'entwurf')),
    startdatum TEXT,
    enddatum TEXT,
    kuendigungsfrist TEXT,
    dateipfad TEXT,
    zusammenfassung TEXT,
    erstellt_am TEXT DEFAULT (datetime('now', 'localtime')),
    aktualisiert_am TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS klauseln (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vertrag_id INTEGER NOT NULL,
    klausel_typ TEXT NOT NULL,       -- z.B. 'Kündigungsfrist', 'Haftung', 'Laufzeit'
    inhalt TEXT,
    seite TEXT,
    risiko_bewertung TEXT DEFAULT 'neutral' CHECK(risiko_bewertung IN ('niedrig', 'neutral', 'hoch', 'kritisch')),
    extrahiert_am TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (vertrag_id) REFERENCES vertraege(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fristen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vertrag_id INTEGER NOT NULL,
    art TEXT NOT NULL,               -- z.B. 'Kündigungsfrist', 'Vertragsende', 'Verlängerung'
    datum TEXT NOT NULL,
    beschreibung TEXT,
    status TEXT DEFAULT 'offen' CHECK(status IN ('offen', 'erledigt', 'versäumt')),
    benachrichtigt INTEGER DEFAULT 0,
    FOREIGN KEY (vertrag_id) REFERENCES vertraege(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_vertraege_status ON vertraege(status);
CREATE INDEX IF NOT EXISTS idx_klauseln_vertrag ON klauseln(vertrag_id);
CREATE INDEX IF NOT EXISTS idx_klauseln_typ ON klauseln(klausel_typ);
CREATE INDEX IF NOT EXISTS idx_fristen_datum ON fristen(datum);
CREATE INDEX IF NOT EXISTS idx_fristen_status ON fristen(status);
