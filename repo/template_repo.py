"""CRUD for recipe_templates + template_products (per-user)."""

import json
from typing import Dict, List, Optional
from repo.database import Database
from models.meal_type import MealType
from dto.validators import ValidationError


def _check_name_free(conn, name: str, user_id: Optional[int], exclude_id: Optional[int] = None) -> None:
    """Recipe names are unique per owner — raise a friendly error instead of
    letting the UNIQUE constraint surface as a raw 500."""
    if user_id is not None:
        query = "SELECT id FROM recipe_templates WHERE user_id=? AND name=?"
        params = [user_id, name]
    else:
        query = "SELECT id FROM recipe_templates WHERE user_id IS NULL AND name=?"
        params = [name]
    if exclude_id is not None:
        query += " AND id != ?"
        params.append(exclude_id)
    if conn.execute(query, params).fetchone() is not None:
        raise ValidationError(f"A recipe named '{name}' already exists.")


def _load_products(conn, template_id: int) -> List[Dict]:
    rows = conn.execute(
        "SELECT id, name, quantity FROM template_products WHERE template_id=?",
        (template_id,),
    ).fetchall()
    return [{"id": r["id"], "name": r["name"], "quantity": r["quantity"]} for r in rows]


def _row_to_dict(row, products: List[Dict]) -> Dict:
    try:
        meal_types = json.loads(row["meal_types"]) if row["meal_types"] else []
    except ValueError:
        meal_types = []
    if not meal_types:
        meal_types = [row["meal_type"]]
    try:
        methods = json.loads(row["methods"]) if row["methods"] else []
    except ValueError:
        methods = []
    return {
        "id":         row["id"],
        "name":       row["name"],
        "meal_type":  row["meal_type"],
        "meal_types": meal_types,
        "methods":    methods,
        "notes":      row["notes"] or "",
        "recipe":     row["recipe"] or "",
        "calories":   row["calories"],
        "products":   products,
    }


class TemplateRepo:
    def __init__(self, db: Database):
        self.db = db

    def create(self, data: Dict, user_id: Optional[int] = None) -> Dict:
        meal_types = data["meal_types"]
        primary = meal_types[0].value
        types_json = json.dumps([t.value for t in meal_types])
        methods = data.get("methods", [])
        methods_json = json.dumps(methods)
        calories = data.get("calories")
        with self.db.connect() as conn:
            _check_name_free(conn, data["name"], user_id)
            cur = conn.execute(
                "INSERT INTO recipe_templates (user_id, name, meal_type, meal_types, methods, notes, recipe, calories) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (user_id, data["name"], primary, types_json, methods_json,
                 data.get("notes", ""), data.get("recipe", ""), calories),
            )
            tid = cur.lastrowid
            products = []
            for p in data.get("products", []):
                pcur = conn.execute(
                    "INSERT INTO template_products (template_id, name, quantity) VALUES (?,?,?)",
                    (tid, p["name"], p.get("quantity", "")),
                )
                products.append({"id": pcur.lastrowid, "name": p["name"], "quantity": p.get("quantity", "")})
        return {"id": tid, "name": data["name"], "meal_type": primary, "meal_types": [t.value for t in meal_types],
                "methods": methods, "notes": data.get("notes", ""), "recipe": data.get("recipe", ""),
                "calories": calories, "products": products}

    def update(self, tid: int, data: Dict, user_id: Optional[int] = None) -> Optional[Dict]:
        meal_types = data["meal_types"]
        primary = meal_types[0].value
        types_json = json.dumps([t.value for t in meal_types])
        methods = data.get("methods", [])
        methods_json = json.dumps(methods)
        calories = data.get("calories")
        with self.db.connect() as conn:
            if user_id is not None:
                row = conn.execute(
                    "SELECT id FROM recipe_templates WHERE id=? AND user_id=?", (tid, user_id)
                ).fetchone()
            else:
                row = conn.execute("SELECT id FROM recipe_templates WHERE id=?", (tid,)).fetchone()
            if row is None:
                return None
            _check_name_free(conn, data["name"], user_id, exclude_id=tid)
            conn.execute(
                "UPDATE recipe_templates SET name=?, meal_type=?, meal_types=?, methods=?, notes=?, recipe=?, calories=? "
                "WHERE id=?",
                (data["name"], primary, types_json, methods_json, data.get("notes", ""), data.get("recipe", ""),
                 calories, tid),
            )
            conn.execute("DELETE FROM template_products WHERE template_id=?", (tid,))
            products = []
            for p in data.get("products", []):
                pcur = conn.execute(
                    "INSERT INTO template_products (template_id, name, quantity) VALUES (?,?,?)",
                    (tid, p["name"], p.get("quantity", "")),
                )
                products.append({"id": pcur.lastrowid, "name": p["name"], "quantity": p.get("quantity", "")})
        return {"id": tid, "name": data["name"], "meal_type": primary, "meal_types": [t.value for t in meal_types],
                "methods": methods, "notes": data.get("notes", ""), "recipe": data.get("recipe", ""),
                "calories": calories, "products": products}

    def delete(self, tid: int, user_id: Optional[int] = None) -> bool:
        with self.db.connect() as conn:
            if user_id is not None:
                cur = conn.execute("DELETE FROM recipe_templates WHERE id=? AND user_id=?", (tid, user_id))
            else:
                cur = conn.execute("DELETE FROM recipe_templates WHERE id=?", (tid,))
        return cur.rowcount > 0

    def get_all(self, user_id: Optional[int] = None) -> List[Dict]:
        with self.db.connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    "SELECT * FROM recipe_templates WHERE user_id=? ORDER BY meal_type, name",
                    (user_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM recipe_templates ORDER BY meal_type, name"
                ).fetchall()
            return [_row_to_dict(r, _load_products(conn, r["id"])) for r in rows]

    def get_by_id(self, tid: int, user_id: Optional[int] = None) -> Optional[Dict]:
        with self.db.connect() as conn:
            if user_id is not None:
                row = conn.execute(
                    "SELECT * FROM recipe_templates WHERE id=? AND user_id=?", (tid, user_id)
                ).fetchone()
            else:
                row = conn.execute("SELECT * FROM recipe_templates WHERE id=?", (tid,)).fetchone()
            if row is None:
                return None
            return _row_to_dict(row, _load_products(conn, row["id"]))
