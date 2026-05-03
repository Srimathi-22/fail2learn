import sqlite3
import os
from datetime import datetime

DB_PATH = "db/fail2learn.db"


def init_db():
    """Initialize all database tables."""
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Known catalysts from external databases
    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalysts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            source          TEXT,
            reaction        TEXT,
            catalyst_id     TEXT UNIQUE,
            formula         TEXT,
            energy_per_atom REAL,
            band_gap        REAL,
            ec_number       TEXT,
            is_novel        INTEGER DEFAULT 0,
            fetched_at      TEXT
        )
    """)

    # AI-generated novel candidates
    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            source                TEXT,
            reaction              TEXT,
            catalyst_id           TEXT UNIQUE,
            formula               TEXT,
            rationale             TEXT,
            predicted_activity    REAL,
            predicted_selectivity REAL,
            predicted_stability   REAL,
            failure_risk          REAL,
            failure_reason        TEXT,
            is_novel              INTEGER DEFAULT 1,
            generated_at          TEXT
        )
    """)

    # Ranked predictions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            catalyst_id           TEXT,
            formula               TEXT,
            source                TEXT,
            reaction              TEXT,
            rationale             TEXT,
            predicted_activity    REAL,
            predicted_selectivity REAL,
            predicted_stability   REAL,
            failure_risk          REAL,
            failure_reason        TEXT,
            composite_score       REAL,
            final_score           REAL,
            rank                  INTEGER,
            is_novel              INTEGER,
            predicted_at          TEXT
        )
    """)

    # Real experimental results logged by researchers
    cur.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            catalyst_id      TEXT,
            formula          TEXT,
            reaction         TEXT,
            actual_yield     REAL,
            actual_activity  REAL,
            actual_stability REAL,
            outcome          TEXT,
            notes            TEXT,
            logged_by        TEXT,
            logged_at        TEXT
        )
    """)

    # Detected failure patterns
    cur.execute("""
        CREATE TABLE IF NOT EXISTS failure_patterns (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            reaction          TEXT,
            pattern_type      TEXT,
            description       TEXT,
            affected_formulas TEXT,
            frequency         INTEGER,
            recommendation    TEXT,
            detected_at       TEXT
        )
    """)

    # Retraining audit log
    cur.execute("""
        CREATE TABLE IF NOT EXISTS retrain_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            reaction     TEXT,
            factors      TEXT,
            retrained_at TEXT
        )
    """)

    # Collaboration — experiment annotations by users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            catalyst_id   TEXT,
            user          TEXT,
            note          TEXT,
            created_at    TEXT,
            FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized — all tables created")
    print(f"   Location: {os.path.abspath(DB_PATH)}")


def get_db():
    """Return a DB connection. Use as context manager in routes."""
    return sqlite3.connect(DB_PATH)


def get_stats() -> dict:
    """Return overall DB stats for dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    def count(table, where=""):
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table} {where}")
            return cur.fetchone()[0]
        except Exception:
            return 0

    stats = {
        "total_catalysts"  : count("catalysts"),
        "total_candidates" : count("candidates"),
        "novel_candidates" : count("candidates", "WHERE is_novel=1"),
        "total_experiments": count("experiments"),
        "successful_runs"  : count("experiments", "WHERE outcome='success'"),
        "failed_runs"      : count("experiments", "WHERE outcome='failure'"),
        "failure_patterns" : count("failure_patterns"),
        "retrain_events"   : count("retrain_log"),
        "last_updated"     : datetime.now().isoformat(),
    }
    conn.close()
    return stats


if __name__ == "__main__":
    init_db()
    stats = get_stats()
    print(f"\nDB Stats: {stats}")
