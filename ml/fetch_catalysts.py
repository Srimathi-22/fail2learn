import requests
import json
import sqlite3
from datetime import datetime

# ─── Config ───────────────────────────────────────────────
MATERIALS_PROJECT_API_KEY = "YOUR_MP_API_KEY"   # get free key at materialsproject.org
BRENDA_EMAIL              = "YOUR_EMAIL"         # registered BRENDA email
BRENDA_PASSWORD           = "YOUR_PASSWORD"      # BRENDA password

DB_PATH = "db/fail2learn.db"

# ─── Target reactions (add more as needed) ────────────────
TARGET_REACTIONS = [
    "CO2 to methanol",
    "syngas to ethanol",
    "ethanol to jet fuel",
    "cellulose to hydrocarbons",
    "biomass to fuels",
]

# ─── Materials Project ────────────────────────────────────
def fetch_from_materials_project(reaction: str) -> list[dict]:
    """
    Fetch candidate catalyst materials from Materials Project API.
    Returns list of catalyst dicts with id, formula, energy, band_gap.
    """
    print(f"  [Materials Project] Fetching for: {reaction}")

    # Map reaction keywords to relevant element filters
    element_map = {
        "CO2 to methanol"       : ["Cu", "Zn", "Al"],
        "syngas to ethanol"     : ["Rh", "Cu", "Fe"],
        "ethanol to jet fuel"   : ["Pt", "Pd", "Ni"],
        "cellulose to hydrocarbons": ["Mo", "Ni", "W"],
        "biomass to fuels"      : ["Fe", "Co", "Ni"],
    }
    elements = element_map.get(reaction, ["Cu", "Fe", "Ni"])

    catalysts = []
    try:
        url = "https://api.materialsproject.org/materials/summary/"
        params = {
            "elements"       : ",".join(elements),
            "fields"         : "material_id,formula_pretty,energy_per_atom,band_gap,is_stable",
            "is_stable"      : True,
            "_limit"         : 10,
            "X-API-KEY"      : MATERIALS_PROJECT_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            for item in data:
                catalysts.append({
                    "source"        : "Materials Project",
                    "reaction"      : reaction,
                    "catalyst_id"   : item.get("material_id", ""),
                    "formula"       : item.get("formula_pretty", ""),
                    "energy_per_atom": item.get("energy_per_atom", None),
                    "band_gap"      : item.get("band_gap", None),
                    "is_novel"      : False,
                    "fetched_at"    : datetime.now().isoformat(),
                })
        else:
            print(f"  [Materials Project] API error {resp.status_code} — using fallback data")
            catalysts = _mp_fallback(reaction)
    except Exception as e:
        print(f"  [Materials Project] Request failed: {e} — using fallback data")
        catalysts = _mp_fallback(reaction)

    print(f"  [Materials Project] Got {len(catalysts)} catalysts")
    return catalysts


def _mp_fallback(reaction: str) -> list[dict]:
    """Fallback synthetic catalysts if API is unavailable."""
    fallback = {
        "CO2 to methanol": [
            {"formula": "Cu/ZnO/Al2O3", "energy_per_atom": -3.21, "band_gap": 0.0},
            {"formula": "In2O3",         "energy_per_atom": -4.10, "band_gap": 2.9},
            {"formula": "ZnO",           "energy_per_atom": -3.60, "band_gap": 3.4},
        ],
        "syngas to ethanol": [
            {"formula": "Rh/SiO2",  "energy_per_atom": -5.80, "band_gap": 0.0},
            {"formula": "MoS2",     "energy_per_atom": -4.30, "band_gap": 1.2},
            {"formula": "CuFe2O4", "energy_per_atom": -3.90, "band_gap": 1.8},
        ],
        "ethanol to jet fuel": [
            {"formula": "Pt/Al2O3", "energy_per_atom": -6.10, "band_gap": 0.0},
            {"formula": "HZSM-5",   "energy_per_atom": -4.50, "band_gap": 0.0},
            {"formula": "Pd/C",     "energy_per_atom": -5.20, "band_gap": 0.0},
        ],
    }
    items = fallback.get(reaction, fallback["CO2 to methanol"])
    return [
        {
            "source"         : "Materials Project (fallback)",
            "reaction"       : reaction,
            "catalyst_id"    : f"mp-fallback-{i+1}",
            "formula"        : item["formula"],
            "energy_per_atom": item["energy_per_atom"],
            "band_gap"       : item["band_gap"],
            "is_novel"       : False,
            "fetched_at"     : datetime.now().isoformat(),
        }
        for i, item in enumerate(items)
    ]


# ─── BRENDA Enzyme Database ───────────────────────────────
def fetch_from_brenda(reaction: str) -> list[dict]:
    """
    Fetch relevant enzymes from BRENDA database.
    Returns list of enzyme dicts.
    Note: BRENDA requires SOAP API — simplified REST-like approach used here.
    """
    print(f"  [BRENDA] Fetching enzymes for: {reaction}")

    # Map reaction to relevant EC numbers
    ec_map = {
        "CO2 to methanol"          : ["1.1.1.244", "1.2.1.2"],
        "syngas to ethanol"        : ["1.1.1.1",   "4.1.2.22"],
        "ethanol to jet fuel"      : ["1.1.1.1",   "2.3.1.9"],
        "cellulose to hydrocarbons": ["3.2.1.4",   "3.2.1.91"],
        "biomass to fuels"         : ["3.2.1.4",   "1.1.1.1"],
    }
    ec_numbers = ec_map.get(reaction, ["1.1.1.1"])

    enzymes = []
    for ec in ec_numbers:
        try:
            url = f"https://www.brenda-enzymes.org/php/result_flat.php4?ecno={ec}"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                enzymes.append({
                    "source"      : "BRENDA",
                    "reaction"    : reaction,
                    "catalyst_id" : f"brenda-{ec}",
                    "formula"     : f"EC {ec}",
                    "ec_number"   : ec,
                    "is_novel"    : False,
                    "fetched_at"  : datetime.now().isoformat(),
                })
            else:
                enzymes.append(_brenda_fallback_entry(reaction, ec))
        except Exception:
            enzymes.append(_brenda_fallback_entry(reaction, ec))

    print(f"  [BRENDA] Got {len(enzymes)} enzymes")
    return enzymes


def _brenda_fallback_entry(reaction: str, ec: str) -> dict:
    enzyme_names = {
        "1.1.1.244": "methanol dehydrogenase",
        "1.2.1.2"  : "formate dehydrogenase",
        "1.1.1.1"  : "alcohol dehydrogenase",
        "4.1.2.22" : "fructose-6-phosphate aldolase",
        "2.3.1.9"  : "acetyl-CoA acetyltransferase",
        "3.2.1.4"  : "cellulase (endoglucanase)",
        "3.2.1.91" : "cellobiohydrolase",
    }
    return {
        "source"      : "BRENDA (fallback)",
        "reaction"    : reaction,
        "catalyst_id" : f"brenda-{ec}",
        "formula"     : f"EC {ec} — {enzyme_names.get(ec, 'unknown enzyme')}",
        "ec_number"   : ec,
        "is_novel"    : False,
        "fetched_at"  : datetime.now().isoformat(),
    }


# ─── Save to DB ───────────────────────────────────────────
def save_catalysts(catalysts: list[dict]):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalysts (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            source        TEXT,
            reaction      TEXT,
            catalyst_id   TEXT UNIQUE,
            formula       TEXT,
            energy_per_atom REAL,
            band_gap      REAL,
            ec_number     TEXT,
            is_novel      INTEGER DEFAULT 0,
            fetched_at    TEXT
        )
    """)
    for c in catalysts:
        cur.execute("""
            INSERT OR IGNORE INTO catalysts
            (source, reaction, catalyst_id, formula, energy_per_atom, band_gap, ec_number, is_novel, fetched_at)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            c.get("source"), c.get("reaction"), c.get("catalyst_id"),
            c.get("formula"), c.get("energy_per_atom"), c.get("band_gap"),
            c.get("ec_number"), int(c.get("is_novel", False)), c.get("fetched_at"),
        ))
    conn.commit()
    conn.close()
    print(f"  [DB] Saved {len(catalysts)} records to {DB_PATH}")


# ─── Main ─────────────────────────────────────────────────
def fetch_all(reaction: str) -> list[dict]:
    """Fetch from all sources for a given reaction."""
    print(f"\nFetching catalysts for: '{reaction}'")
    all_catalysts = []
    all_catalysts += fetch_from_materials_project(reaction)
    all_catalysts += fetch_from_brenda(reaction)
    save_catalysts(all_catalysts)
    return all_catalysts


if __name__ == "__main__":
    import os
    os.makedirs("db", exist_ok=True)

    for reaction in TARGET_REACTIONS:
        results = fetch_all(reaction)
        print(f"  Total fetched: {len(results)}\n")

    print("✅ fetch_catalysts.py complete!")
    print(f"   Check db/fail2learn.db for all results.")
    