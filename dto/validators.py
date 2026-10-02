"""
Lightweight request validation replacing Pydantic — pure stdlib.
Raises ValidationError with a descriptive message on bad input.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from models.meal_type import MealType


class ValidationError(Exception):
    pass


VALID_METHODS = {"air_fryer", "instant_pot"}


def validate_calories(raw: Any) -> Optional[int]:
    """Optional calorie count on a meal/recipe. Empty/None means 'not set'."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise ValidationError("'calories' must be a number")
    if raw < 0:
        raise ValidationError("'calories' must be zero or positive")
    return int(raw)


def validate_methods(raw: Any) -> List[str]:
    """Optional cooking-method tags on a recipe template (e.g. air fryer, instant pot)."""
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValidationError("'methods' must be an array")
    methods: List[str] = []
    for m in raw:
        if not isinstance(m, str) or m.lower() not in VALID_METHODS:
            raise ValidationError(f"'methods' entries must be one of: {sorted(VALID_METHODS)}")
        if m.lower() not in methods:
            methods.append(m.lower())
    return methods


def validate_date(value: Any, field: str = "meal_date") -> date:
    if not isinstance(value, str):
        raise ValidationError(f"'{field}' must be a string in YYYY-MM-DD format")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValidationError(f"'{field}' must be a valid date in YYYY-MM-DD format, got '{value}'")


def validate_product(raw: Any, index: int) -> Dict:
    if not isinstance(raw, dict):
        raise ValidationError(f"products[{index}] must be an object")
    name = raw.get("name", "")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError(f"products[{index}].name must be a non-empty string")
    quantity = raw.get("quantity", "")
    if not isinstance(quantity, str):
        raise ValidationError(f"products[{index}].quantity must be a string")
    return {"name": name.strip(), "quantity": quantity.strip()}


def validate_meal_payload(body: Any) -> Dict:
    """Validate and normalise a raw JSON body for meal create/update."""
    if not isinstance(body, dict):
        raise ValidationError("Request body must be a JSON object")

    name = body.get("name", "")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("'name' must be a non-empty string")

    meal_type_raw = body.get("meal_type", "")
    try:
        meal_type = MealType.from_str(str(meal_type_raw))
    except ValueError as e:
        raise ValidationError(str(e))

    meal_date = validate_date(body.get("meal_date"), "meal_date")

    raw_products = body.get("products", [])
    if not isinstance(raw_products, list):
        raise ValidationError("'products' must be an array")
    products = [validate_product(p, i) for i, p in enumerate(raw_products)]

    notes = body.get("notes", "")
    if not isinstance(notes, str):
        raise ValidationError("'notes' must be a string")

    recipe = body.get("recipe", "")
    if not isinstance(recipe, str):
        raise ValidationError("'recipe' must be a string")

    calories = validate_calories(body.get("calories"))

    return {
        "name": name.strip(),
        "meal_type": meal_type,
        "meal_date": meal_date,
        "products": products,
        "notes": notes.strip(),
        "recipe": recipe.strip(),
        "calories": calories,
    }


def validate_template_payload(body: Any) -> Dict:
    """Validate and normalise a raw JSON body for recipe template create/update.

    Unlike a logged meal (one instance, one type), a recipe template can be
    tagged with several meal types at once (e.g. usable for both lunch and
    dinner), so it takes a non-empty 'meal_types' list instead of a single
    'meal_type'.
    """
    if not isinstance(body, dict):
        raise ValidationError("Request body must be a JSON object")

    name = body.get("name", "")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("'name' must be a non-empty string")

    raw_types = body.get("meal_types")
    if raw_types is None:
        raw_types = [body.get("meal_type", "")]
    if not isinstance(raw_types, list) or not raw_types:
        raise ValidationError("'meal_types' must be a non-empty array")

    meal_types: List[MealType] = []
    for raw_type in raw_types:
        try:
            mt = MealType.from_str(str(raw_type))
        except ValueError as e:
            raise ValidationError(str(e))
        if mt not in meal_types:
            meal_types.append(mt)

    raw_products = body.get("products", [])
    if not isinstance(raw_products, list):
        raise ValidationError("'products' must be an array")
    products = [validate_product(p, i) for i, p in enumerate(raw_products)]

    notes = body.get("notes", "")
    if not isinstance(notes, str):
        raise ValidationError("'notes' must be a string")

    recipe = body.get("recipe", "")
    if not isinstance(recipe, str):
        raise ValidationError("'recipe' must be a string")

    methods = validate_methods(body.get("methods"))
    calories = validate_calories(body.get("calories"))

    return {
        "name": name.strip(),
        "meal_types": meal_types,
        "methods": methods,
        "products": products,
        "notes": notes.strip(),
        "recipe": recipe.strip(),
        "calories": calories,
    }
