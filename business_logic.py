import logging
from typing import Dict, List, Tuple, Optional
from database import DatabaseManager
from utils import to_base, from_base, same_dimension, fmt_qty

logger = logging.getLogger(__name__)

def inventory_as_base(user_id: Optional[int]) -> Dict[Tuple[str, str], float]:
    if not user_id:
        logger.warning("inventory_as_base: No user_id provided.")
        return {}
    inv = DatabaseManager.list_inventory(user_id)
    logger.info(f"inventory_as_base: Retrieved {len(inv)} inventory items for user_id={user_id}")
    agg: Dict[Tuple[str, str], float] = {}
    for row in inv:
        key = (DatabaseManager.normalize_name(row["name"]), row["base_unit"])
        agg[key] = agg.get(key, 0.0) + row["base_qty"]
        logger.debug(f"inventory_as_base: {row['name']} -> {row['base_qty']} {row['base_unit']} (normalized key: {key})")
    return agg

def recipe_feasibility(recipe: Dict, user_id: Optional[int]) -> Tuple[bool, List[Dict]]:
    if not user_id:
        logger.error("recipe_feasibility: No valid user_id")
        return False, []
    inv = inventory_as_base(user_id)
    logger.info(f"Checking feasibility for recipe: {recipe['title']} (id={recipe['id']})")
    shorts = []
    feasible = True
    for r in recipe["ingredients"]:
        name_normalized = DatabaseManager.normalize_name(r["name"])
        needed_base, base_unit = to_base(r["quantity"], r["unit"])
        have_base = inv.get((name_normalized, base_unit), 0.0)
        logger.debug(f"Ingredient: {r['name']} (normalized: {name_normalized}) | Need: {needed_base} {base_unit} | Have: {have_base} {base_unit}")
        if have_base + 1e-9 < needed_base:
            feasible = False
            missing = needed_base - have_base
            display_missing = from_base(missing, base_unit, r["unit"])
            shorts.append(
                {
                    "name": r["name"],
                    "needed_qty": r["quantity"],
                    "needed_unit": r["unit"],
                    "have_qty": from_base(have_base, base_unit, r["unit"]),
                    "have_unit": r["unit"],
                    "missing_base": missing,
                    "base_unit": base_unit,
                    "missing_qty_disp": display_missing,
                    "missing_unit_disp": r["unit"],
                }
            )
    logger.info(f"Recipe {recipe['title']} feasible: {feasible}, missing ingredients: {len(shorts)}")
    return feasible, shorts

def consume_ingredients_for_recipe(recipe: Dict, user_id: Optional[int]) -> bool:
    ok, _ = recipe_feasibility(recipe, user_id)
    if not ok:
        return False
    if not user_id:
        logger.error("consume_ingredients_for_recipe: No valid user_id")
        return False
    for r in recipe["ingredients"]:
        DatabaseManager.adjust_inventory(user_id, r["name"], -abs(float(r["quantity"])), r["unit"])
    return True