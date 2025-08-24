import math
import logging

logger = logging.getLogger(__name__)

UNIT_ALIASES = {
    "mass": {
        "g": ("g", 1.0), "gram": ("g", 1.0), "grams": ("g", 1.0),
        "kg": ("g", 1000.0), "kilogram": ("g", 1000.0), "kilograms": ("g", 1000.0),
        "lạng": ("g", 100.0),
    },
    "volume": {
        "ml": ("ml", 1.0), "milliliter": ("ml", 1.0), "milliliters": ("ml", 1.0),
        "l": ("ml", 1000.0), "liter": ("ml", 1000.0), "liters": ("ml", 1000.0),
        "tsp": ("ml", 5.0), "teaspoon": ("ml", 5.0), "tbsp": ("ml", 15.0), "tablespoon": ("ml", 15.0),
        "cup": ("ml", 240.0), "cups": ("ml", 240.0),
        "chén": ("ml", 100.0), "bát": ("ml", 250.0),
    },
    "count": {
        "piece": ("piece", 1.0), "pieces": ("piece", 1.0),
        "pc": ("piece", 1.0), "pcs": ("piece", 1.0),
        "cai": ("piece", 1.0), "cái": ("piece", 1.0), "cai.": ("piece", 1.0),
    }
}

PRETTY_UNIT = {"g": "g", "ml": "ml", "piece": "piece"}
VALID_UNITS = sorted([k for cat in UNIT_ALIASES for k in UNIT_ALIASES[cat]])

def normalize_unit(unit: str) -> tuple[str, float]:
    key = unit.strip().lower() if unit else ""
    for category in UNIT_ALIASES:
        if key in UNIT_ALIASES[category]:
            return UNIT_ALIASES[category][key]
    logger.warning(f"Invalid unit '{unit}', defaulting to 'piece'")
    return ("piece", 1.0)

def validate_unit(unit: str) -> bool:
    return unit.strip().lower() in [k for cat in UNIT_ALIASES for k in UNIT_ALIASES[cat]]

def to_base(quantity: float, unit: str) -> tuple[float, str]:
    base_unit, factor = normalize_unit(unit)
    return float(quantity) * factor, base_unit

def from_base(base_qty: float, base_unit: str, target_unit: str) -> float:
    tgt_base, factor = normalize_unit(target_unit)
    if tgt_base != base_unit:
        logger.warning(f"Unit mismatch: cannot convert {base_unit} to {target_unit}")
        return base_qty
    return base_qty / factor

def same_dimension(u1: str, u2: str) -> bool:
    return normalize_unit(u1)[0] == normalize_unit(u2)[0]

def fmt_qty(q: float) -> str:
    if math.isclose(q, round(q), rel_tol=1e-6):
        return str(int(round(q)))
    return f"{q:.2f}".rstrip("0").rstrip(".")