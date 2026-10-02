"""Cross-table helper: infer each ingredient's conventional unit from how the
user has already used it — across recipes, logged meals, the fridge, and the
shopping list. Read-only; used to auto-suggest units as you type an ingredient
name anywhere in the app, and to flag it if you're about to type a different
one than what you've used before.
"""

from collections import Counter
from typing import Dict, Optional
from repo.database import Database
from utils.quantity import parse_qty, format_qty


class IngredientRepo:
    def __init__(self, db: Database):
        self._db = db

    def get_common_units(self, user_id: Optional[int] = None) -> Dict[str, str]:
        counters: Dict[str, Counter] = {}

        def _tally(name: str, quantity: str) -> None:
            if not name:
                return
            parsed = parse_qty(quantity)
            if parsed is None or not parsed[1]:
                return
            counters.setdefault(name.strip().lower(), Counter())[parsed[1]] += 1

        with self._db.connect() as conn:
            uid_clause = "=?" if user_id is not None else " IS ?"
            params = (user_id,)

            for row in conn.execute(
                f"SELECT tp.name, tp.quantity FROM template_products tp "
                f"JOIN recipe_templates rt ON rt.id = tp.template_id WHERE rt.user_id{uid_clause}",
                params,
            ).fetchall():
                _tally(row["name"], row["quantity"])

            for row in conn.execute(
                f"SELECT p.name, p.quantity FROM products p "
                f"JOIN meals m ON m.id = p.meal_id WHERE m.user_id{uid_clause}",
                params,
            ).fetchall():
                _tally(row["name"], row["quantity"])

            for row in conn.execute(
                f"SELECT name, quantity FROM fridge_items WHERE user_id{uid_clause}", params
            ).fetchall():
                _tally(row["name"], row["quantity"])

            for row in conn.execute(
                f"SELECT item AS name, quantity FROM shopping_list WHERE user_id{uid_clause}", params
            ).fetchall():
                _tally(row["name"], row["quantity"])

        return {name: counter.most_common(1)[0][0] for name, counter in counters.items()}

    def rename_unit(self, name: str, old_unit: str, new_unit: str, user_id: Optional[int] = None) -> int:
        """Retroactively swap `old_unit` for `new_unit` on every existing row
        named `name` (case-insensitive), across recipes, logged meals, the
        fridge, and the shopping list — keeping each row's own numeric value
        unchanged. Scoped to one user. Returns how many rows were changed."""
        name_key = (name or "").strip().lower()
        old_unit_key = (old_unit or "").strip().lower()
        if not name_key or not old_unit_key or old_unit_key == (new_unit or "").strip().lower():
            return 0

        uid_clause = "=?" if user_id is not None else " IS ?"
        params = (user_id,)
        changed = 0

        with self._db.connect() as conn:
            def _rename(select_sql: str, table: str, name_col: str, qty_col: str) -> None:
                nonlocal changed
                for row in conn.execute(select_sql, params).fetchall():
                    if row["name"].strip().lower() != name_key:
                        continue
                    parsed = parse_qty(row["quantity"])
                    if parsed is None or parsed[1] != old_unit_key:
                        continue
                    new_qty = format_qty(parsed[0], new_unit.strip())
                    conn.execute(f"UPDATE {table} SET {qty_col}=? WHERE id=?", (new_qty, row["id"]))
                    changed += 1

            _rename(
                f"SELECT tp.id, tp.name, tp.quantity FROM template_products tp "
                f"JOIN recipe_templates rt ON rt.id = tp.template_id WHERE rt.user_id{uid_clause}",
                "template_products", "name", "quantity",
            )
            _rename(
                f"SELECT p.id, p.name, p.quantity FROM products p "
                f"JOIN meals m ON m.id = p.meal_id WHERE m.user_id{uid_clause}",
                "products", "name", "quantity",
            )
            _rename(
                f"SELECT id, name, quantity FROM fridge_items WHERE user_id{uid_clause}",
                "fridge_items", "name", "quantity",
            )
            _rename(
                f"SELECT id, item AS name, quantity FROM shopping_list WHERE user_id{uid_clause}",
                "shopping_list", "item", "quantity",
            )

        return changed
