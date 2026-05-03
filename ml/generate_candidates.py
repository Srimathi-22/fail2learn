import sqlite3
import json
from datetime import datetime

DB_PATH = "db/fail2learn.db"

# ─── Expanded fallback candidates for all reactions ───────
FALLBACK_CANDIDATES = {
    "CO2 to methanol": [
        {"formula": "Cu-Zn-Ga/Al2O3",    "rationale": "Gallium promotes CO2 adsorption on copper sites",         "predicted_activity": 0.78, "predicted_selectivity": 0.72, "predicted_stability": 0.65, "failure_risk": 0.22, "failure_reason": "sintering at high temp"},
        {"formula": "In2O3-ZrO2",         "rationale": "Indium oxide shows high methanol selectivity",            "predicted_activity": 0.65, "predicted_selectivity": 0.80, "predicted_stability": 0.55, "failure_risk": 0.30, "failure_reason": "reduction instability"},
        {"formula": "MnO-CuO/SiO2",       "rationale": "Manganese promoter enhances copper stability",            "predicted_activity": 0.70, "predicted_selectivity": 0.68, "predicted_stability": 0.75, "failure_risk": 0.18, "failure_reason": "slow activation period"},
        {"formula": "Pd-Cu/CeO2",         "rationale": "Palladium improves H2 dissociation on ceria support",    "predicted_activity": 0.80, "predicted_selectivity": 0.75, "predicted_stability": 0.60, "failure_risk": 0.20, "failure_reason": "catalyst poisoning by sulfur"},
        {"formula": "Fe-Co/TiO2",         "rationale": "Bimetallic synergy improves CO2 conversion",             "predicted_activity": 0.72, "predicted_selectivity": 0.65, "predicted_stability": 0.70, "failure_risk": 0.25, "failure_reason": "oxidation at high temperature"},
        {"formula": "Ni-Ga/ZrO2",         "rationale": "Nickel-gallium intermetallic for methanol synthesis",     "predicted_activity": 0.75, "predicted_selectivity": 0.78, "predicted_stability": 0.68, "failure_risk": 0.21, "failure_reason": "phase segregation"},
        {"formula": "ZnO-ZrO2",           "rationale": "Binary oxide with high CO2 activation energy",            "predicted_activity": 0.68, "predicted_selectivity": 0.82, "predicted_stability": 0.72, "failure_risk": 0.19, "failure_reason": "low surface area"},
        {"formula": "Cu-ZnO-ZrO2/Al2O3", "rationale": "Quaternary catalyst with enhanced active sites",          "predicted_activity": 0.85, "predicted_selectivity": 0.76, "predicted_stability": 0.71, "failure_risk": 0.17, "failure_reason": "complex preparation"},
        {"formula": "Ag-In/SiO2",         "rationale": "Silver promotes electron transfer to indium sites",       "predicted_activity": 0.62, "predicted_selectivity": 0.85, "predicted_stability": 0.58, "failure_risk": 0.28, "failure_reason": "silver agglomeration"},
        {"formula": "Mo-Cu/Al2O3",        "rationale": "Molybdenum modifier increases methanol yield",            "predicted_activity": 0.74, "predicted_selectivity": 0.70, "predicted_stability": 0.73, "failure_risk": 0.23, "failure_reason": "MoO3 over-reduction"},
    ],
    "syngas to ethanol": [
        {"formula": "Rh-Mn/SiO2",         "rationale": "Rhodium-manganese for direct ethanol synthesis",          "predicted_activity": 0.76, "predicted_selectivity": 0.70, "predicted_stability": 0.65, "failure_risk": 0.24, "failure_reason": "CO poisoning"},
        {"formula": "MoS2-Co/Al2O3",      "rationale": "Sulphide catalyst with cobalt promoter",                 "predicted_activity": 0.68, "predicted_selectivity": 0.72, "predicted_stability": 0.70, "failure_risk": 0.22, "failure_reason": "sulphur leaching"},
        {"formula": "Cu-Fe-Zn/SiO2",      "rationale": "Ternary catalyst for higher alcohol synthesis",           "predicted_activity": 0.72, "predicted_selectivity": 0.65, "predicted_stability": 0.68, "failure_risk": 0.26, "failure_reason": "methanol byproduct formation"},
        {"formula": "Rh-Fe/TiO2",         "rationale": "Iron promoter enhances C-C coupling on rhodium",         "predicted_activity": 0.79, "predicted_selectivity": 0.74, "predicted_stability": 0.62, "failure_risk": 0.21, "failure_reason": "iron oxidation state instability"},
        {"formula": "Co-Cu/ZnO",          "rationale": "Cobalt-copper synergy for ethanol selectivity",           "predicted_activity": 0.71, "predicted_selectivity": 0.68, "predicted_stability": 0.72, "failure_risk": 0.23, "failure_reason": "zinc volatilisation"},
        {"formula": "Ni-Mo-K/Al2O3",      "rationale": "Potassium promoter shifts selectivity to ethanol",        "predicted_activity": 0.67, "predicted_selectivity": 0.76, "predicted_stability": 0.69, "failure_risk": 0.20, "failure_reason": "potassium migration"},
        {"formula": "Pd-Zn/CeO2",         "rationale": "Palladium-zinc alloy for selective ethanol production",   "predicted_activity": 0.74, "predicted_selectivity": 0.73, "predicted_stability": 0.64, "failure_risk": 0.25, "failure_reason": "alloy decomposition"},
        {"formula": "Fe-Cu-K/SiO2",       "rationale": "Fischer-Tropsch modified for ethanol",                    "predicted_activity": 0.69, "predicted_selectivity": 0.67, "predicted_stability": 0.74, "failure_risk": 0.22, "failure_reason": "wax deposition"},
        {"formula": "Rh-V/Al2O3",         "rationale": "Vanadium oxide promoter for C2 oxygenates",              "predicted_activity": 0.77, "predicted_selectivity": 0.71, "predicted_stability": 0.63, "failure_risk": 0.24, "failure_reason": "vanadium reduction"},
        {"formula": "Cu-Co-Mo/ZrO2",      "rationale": "Ternary synergistic catalyst on zirconia support",        "predicted_activity": 0.73, "predicted_selectivity": 0.75, "predicted_stability": 0.67, "failure_risk": 0.21, "failure_reason": "phase separation at high temp"},
    ],
    "ethanol to jet fuel": [
        {"formula": "HZSM-5/Zn",          "rationale": "Zinc modified zeolite for ethanol dehydration",           "predicted_activity": 0.80, "predicted_selectivity": 0.74, "predicted_stability": 0.70, "failure_risk": 0.20, "failure_reason": "coking and pore blockage"},
        {"formula": "Pt-Sn/Al2O3",        "rationale": "Platinum-tin for dehydrogenation step",                  "predicted_activity": 0.77, "predicted_selectivity": 0.72, "predicted_stability": 0.68, "failure_risk": 0.22, "failure_reason": "tin migration"},
        {"formula": "Ni-HZSM-5",          "rationale": "Nickel in zeolite for oligomerisation",                  "predicted_activity": 0.74, "predicted_selectivity": 0.70, "predicted_stability": 0.72, "failure_risk": 0.23, "failure_reason": "coke formation"},
        {"formula": "Pd/C-HZSM-5",        "rationale": "Palladium on carbon with zeolite for hydrocarbon range",  "predicted_activity": 0.79, "predicted_selectivity": 0.76, "predicted_stability": 0.65, "failure_risk": 0.21, "failure_reason": "palladium sintering"},
        {"formula": "WOx/ZrO2",           "rationale": "Tungsten oxide acid sites for dehydration",              "predicted_activity": 0.71, "predicted_selectivity": 0.78, "predicted_stability": 0.74, "failure_risk": 0.19, "failure_reason": "tungsten leaching in water"},
        {"formula": "MgO-Al2O3 (HTlc)",   "rationale": "Hydrotalcite base catalyst for aldol condensation",      "predicted_activity": 0.68, "predicted_selectivity": 0.80, "predicted_stability": 0.76, "failure_risk": 0.18, "failure_reason": "hydration deactivation"},
        {"formula": "Cu-ZnO/HZSM-5",      "rationale": "Bifunctional catalyst combining dehydrogenation+acid",   "predicted_activity": 0.82, "predicted_selectivity": 0.73, "predicted_stability": 0.67, "failure_risk": 0.20, "failure_reason": "zinc migration to zeolite"},
        {"formula": "Rh/SiO2-Al2O3",      "rationale": "Rhodium on mixed oxide for C-C bond formation",          "predicted_activity": 0.76, "predicted_selectivity": 0.71, "predicted_stability": 0.63, "failure_risk": 0.25, "failure_reason": "rhodium agglomeration"},
        {"formula": "Fe-HZSM-5",          "rationale": "Iron zeolite for aromatisation of ethanol",              "predicted_activity": 0.73, "predicted_selectivity": 0.69, "predicted_stability": 0.71, "failure_risk": 0.24, "failure_reason": "over-aromatisation"},
        {"formula": "Co/Al2O3-HZSM-5",    "rationale": "Cobalt on alumina with zeolite for jet range hydrocarbons","predicted_activity": 0.78, "predicted_selectivity": 0.75, "predicted_stability": 0.69, "failure_risk": 0.21, "failure_reason": "cobalt oxidation"},
    ],
    "cellulose to hydrocarbons": [
        {"formula": "Ru/C",               "rationale": "Ruthenium on carbon for cellulose hydrogenolysis",        "predicted_activity": 0.74, "predicted_selectivity": 0.68, "predicted_stability": 0.70, "failure_risk": 0.24, "failure_reason": "ruthenium leaching"},
        {"formula": "Ni-W/SiO2-Al2O3",   "rationale": "Nickel-tungsten for hydrodeoxygenation",                 "predicted_activity": 0.71, "predicted_selectivity": 0.72, "predicted_stability": 0.68, "failure_risk": 0.23, "failure_reason": "sulphur sensitivity"},
        {"formula": "Mo2C",               "rationale": "Molybdenum carbide for deoxygenation",                   "predicted_activity": 0.76, "predicted_selectivity": 0.70, "predicted_stability": 0.65, "failure_risk": 0.25, "failure_reason": "oxidation of carbide phase"},
        {"formula": "Pd-Fe/ZrO2",         "rationale": "Bimetallic for selective C-O cleavage",                  "predicted_activity": 0.78, "predicted_selectivity": 0.74, "predicted_stability": 0.63, "failure_risk": 0.22, "failure_reason": "iron oxidation"},
        {"formula": "HZSM-5/Ga",          "rationale": "Gallium zeolite for bio-oil upgrading",                  "predicted_activity": 0.72, "predicted_selectivity": 0.76, "predicted_stability": 0.71, "failure_risk": 0.20, "failure_reason": "coke deposition"},
        {"formula": "Pt/TiO2",            "rationale": "Platinum on titania for aqueous phase reforming",        "predicted_activity": 0.75, "predicted_selectivity": 0.71, "predicted_stability": 0.67, "failure_risk": 0.23, "failure_reason": "platinum sintering in water"},
        {"formula": "Ni-Cu/Al2O3",        "rationale": "Bimetallic for selective hydrogenation of intermediates", "predicted_activity": 0.70, "predicted_selectivity": 0.73, "predicted_stability": 0.72, "failure_risk": 0.21, "failure_reason": "copper segregation"},
        {"formula": "ReOx/CeO2",          "rationale": "Rhenium oxide for selective C-O hydrogenolysis",         "predicted_activity": 0.73, "predicted_selectivity": 0.77, "predicted_stability": 0.64, "failure_risk": 0.24, "failure_reason": "rhenium volatilisation"},
        {"formula": "Co-Mo-S/Al2O3",      "rationale": "HDS catalyst adapted for cellulose conversion",          "predicted_activity": 0.69, "predicted_selectivity": 0.69, "predicted_stability": 0.74, "failure_risk": 0.22, "failure_reason": "sulphur loss"},
        {"formula": "Zn-Cr/HZSM-5",      "rationale": "Bifunctional for dehydration and aromatisation",         "predicted_activity": 0.77, "predicted_selectivity": 0.72, "predicted_stability": 0.68, "failure_risk": 0.21, "failure_reason": "chromium leaching"},
    ],
    "biomass to fuels": [
        {"formula": "Ni/Al2O3",           "rationale": "Nickel for biomass steam reforming",                     "predicted_activity": 0.76, "predicted_selectivity": 0.68, "predicted_stability": 0.72, "failure_risk": 0.22, "failure_reason": "carbon deposition"},
        {"formula": "Fe-Ni/CeO2-ZrO2",   "rationale": "Bimetallic on mixed oxide for tar reforming",            "predicted_activity": 0.73, "predicted_selectivity": 0.71, "predicted_stability": 0.69, "failure_risk": 0.24, "failure_reason": "iron sintering"},
        {"formula": "Co-Mo/Al2O3",        "rationale": "Hydrotreating catalyst for bio-oil upgrading",           "predicted_activity": 0.74, "predicted_selectivity": 0.73, "predicted_stability": 0.70, "failure_risk": 0.21, "failure_reason": "sulphur depletion"},
        {"formula": "Pt-Re/C",            "rationale": "Aqueous phase reforming of biomass oxygenates",          "predicted_activity": 0.78, "predicted_selectivity": 0.70, "predicted_stability": 0.64, "failure_risk": 0.23, "failure_reason": "rhenium leaching in water"},
        {"formula": "Ru-Ni/SiO2",         "rationale": "Ruthenium promoter for low temperature reforming",       "predicted_activity": 0.80, "predicted_selectivity": 0.72, "predicted_stability": 0.66, "failure_risk": 0.20, "failure_reason": "ruthenium sintering"},
        {"formula": "HZSM-5/Fe",          "rationale": "Iron zeolite for catalytic fast pyrolysis",              "predicted_activity": 0.71, "predicted_selectivity": 0.75, "predicted_stability": 0.73, "failure_risk": 0.19, "failure_reason": "coke formation"},
        {"formula": "MgO/Al2O3",          "rationale": "Basic catalyst for ketonisation of bio-acids",           "predicted_activity": 0.68, "predicted_selectivity": 0.78, "predicted_stability": 0.76, "failure_risk": 0.18, "failure_reason": "surface carbonation"},
        {"formula": "Pd-Ni/TiO2",         "rationale": "Hydrodeoxygenation of bio-oil on titania",               "predicted_activity": 0.77, "predicted_selectivity": 0.74, "predicted_stability": 0.65, "failure_risk": 0.22, "failure_reason": "palladium-nickel phase separation"},
        {"formula": "Cu-ZnO/SiO2",        "rationale": "Methanol synthesis from biomass syngas",                 "predicted_activity": 0.72, "predicted_selectivity": 0.70, "predicted_stability": 0.71, "failure_risk": 0.23, "failure_reason": "zinc volatilisation"},
        {"formula": "Ni-Ce/Al2O3",        "rationale": "Cerium promoter reduces carbon deposition on nickel",    "predicted_activity": 0.75, "predicted_selectivity": 0.69, "predicted_stability": 0.74, "failure_risk": 0.20, "failure_reason": "cerium over-reduction"},
    ],
}


def generate_candidates(reaction: str, n: int = 5) -> list[dict]:
    """Generate novel catalyst candidates using pre-defined synthetic data."""
    candidates_pool = FALLBACK_CANDIDATES.get(reaction, FALLBACK_CANDIDATES["CO2 to methanol"])
    selected = candidates_pool[:n]

    results = []
    for i, c in enumerate(selected):
        results.append({
            "source"               : "Synthetic (AI-designed)",
            "reaction"             : reaction,
            "catalyst_id"          : f"ai-gen-{reaction[:6].replace(' ','-')}-{i+1}",
            "formula"              : c["formula"],
            "rationale"            : c["rationale"],
            "predicted_activity"   : c["predicted_activity"],
            "predicted_selectivity": c["predicted_selectivity"],
            "predicted_stability"  : c["predicted_stability"],
            "failure_risk"         : c["failure_risk"],
            "failure_reason"       : c["failure_reason"],
            "is_novel"             : True,
            "generated_at"         : datetime.now().isoformat(),
        })

    _save_candidates(results)
    print(f"[generate] Generated {len(results)} candidates for '{reaction}'")
    return results


def _save_candidates(candidates: list[dict]):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
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
    for c in candidates:
        cur.execute("""
            INSERT OR IGNORE INTO candidates
            (source,reaction,catalyst_id,formula,rationale,
             predicted_activity,predicted_selectivity,predicted_stability,
             failure_risk,failure_reason,is_novel,generated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            c["source"], c["reaction"], c["catalyst_id"], c["formula"],
            c["rationale"], c["predicted_activity"], c["predicted_selectivity"],
            c["predicted_stability"], c["failure_risk"], c["failure_reason"],
            int(c["is_novel"]), c["generated_at"]
        ))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    for reaction in FALLBACK_CANDIDATES.keys():
        results = generate_candidates(reaction, n=10)
        print(f"  {reaction}: {len(results)} candidates generated")
    print("✅ generate_candidates.py complete!")
