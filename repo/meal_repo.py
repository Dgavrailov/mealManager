"""CRUD for meals + products (per-user) — stdlib sqlite3 only."""

from datetime import date
from typing import List, Optional

from models.meal import Meal
from models.meal_type import MealType
from models.product import Product
from repo.database import Database


def _row_to_meal(row, products: List[Product]) -> Meal:
    return Meal(
        id=row["id"],
        name=row["name"],
        meal_type=MealType(row["meal_type"]),
        meal_date=date.fromisoformat(row["meal_date"]),
        notes=row["notes"] or "",
        recipe=row["recipe"] or "",
        calories=row["calories"],
        products=products,
    )


def _load_products(conn, meal_id: int) -> List[Product]:
    rows = conn.execute(
        "SELECT id, meal_id, name, quantity FROM products WHERE meal_id=?", (meal_id,)
    ).fetchall()
    return [Product(id=r["id"], meal_id=r["meal_id"], name=r["name"], quantity=r["quantity"]) for r in rows]


class MealRepo:
    def __init__(self, db: Database):
        self.db = db

    # ── write ─────────────────────────────────────────────────────────────────

    def create(self, meal: Meal, user_id: Optional[int] = None) -> Meal:
        with self.db.connect() as conn:
            cur = conn.execute(
                "INSERT INTO meals (user_id, name, meal_type, meal_date, notes, recipe, calories) VALUES (?,?,?,?,?,?,?)",
                (user_id, meal.name, meal.meal_type.value, meal.meal_date.isoformat(), meal.notes, meal.recipe,
                 meal.calories),
            )
            meal_id = cur.lastrowid
            products = []
            for p in meal.products:
                pcur = conn.execute(
                    "INSERT INTO products (meal_id, name, quantity) VALUES (?,?,?)",
                    (meal_id, p.name, p.quantity),
                )
                products.append(Product(id=pcur.lastrowid, meal_id=meal_id, name=p.name, quantity=p.quantity))
        return Meal(id=meal_id, name=meal.name, meal_type=meal.meal_type, meal_date=meal.meal_date,
                    notes=meal.notes, recipe=meal.recipe, calories=meal.calories, products=products)

    def update(self, meal: Meal, user_id: Optional[int] = None) -> Optional[Meal]:
        with self.db.connect() as conn:
            if user_id is not None:
                cur = conn.execute(
                    "UPDATE meals SET name=?, meal_type=?, meal_date=?, notes=?, recipe=?, calories=? WHERE id=? AND user_id=?",
                    (meal.name, meal.meal_type.value, meal.meal_date.isoformat(), meal.notes, meal.recipe,
                     meal.calories, meal.id, user_id),
                )
            else:
                cur = conn.execute(
                    "UPDATE meals SET name=?, meal_type=?, meal_date=?, notes=?, recipe=?, calories=? WHERE id=?",
                    (meal.name, meal.meal_type.value, meal.meal_date.isoformat(), meal.notes, meal.recipe,
                     meal.calories, meal.id),
                )
            if cur.rowcount == 0:
                return None
            conn.execute("DELETE FROM products WHERE meal_id=?", (meal.id,))
            products = []
            for p in meal.products:
                pcur = conn.execute(
                    "INSERT INTO products (meal_id, name, quantity) VALUES (?,?,?)",
                    (meal.id, p.name, p.quantity),
                )
                products.append(Product(id=pcur.lastrowid, meal_id=meal.id, name=p.name, quantity=p.quantity))
        return Meal(id=meal.id, name=meal.name, meal_type=meal.meal_type, meal_date=meal.meal_date,
                    notes=meal.notes, recipe=meal.recipe, calories=meal.calories, products=products)

    def delete(self, meal_id: int, user_id: Optional[int] = None) -> bool:
        with self.db.connect() as conn:
            if user_id is not None:
                cur = conn.execute("DELETE FROM meals WHERE id=? AND user_id=?", (meal_id, user_id))
            else:
                cur = conn.execute("DELETE FROM meals WHERE id=?", (meal_id,))
        return cur.rowcount > 0

    # ── read ──────────────────────────────────────────────────────────────────

    def get_by_id(self, meal_id: int, user_id: Optional[int] = None) -> Optional[Meal]:
        with self.db.connect() as conn:
            if user_id is not None:
                row = conn.execute("SELECT * FROM meals WHERE id=? AND user_id=?", (meal_id, user_id)).fetchone()
                if row is None:
                    return None
                products = _load_products(conn, meal_id)
                return _row_to_meal(row, products)
            row = conn.execute("SELECT * FROM meals WHERE id=?", (meal_id,)).fetchone()
            if row is None:
                return None
            products = _load_products(conn, meal_id)
        return _row_to_meal(row, products)

    def get_by_date(self, meal_date: date, user_id: Optional[int] = None) -> List[Meal]:
        with self.db.connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    "SELECT * FROM meals WHERE meal_date=? AND user_id=? ORDER BY meal_type",
                    (meal_date.isoformat(), user_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM meals WHERE meal_date=? ORDER BY meal_type",
                    (meal_date.isoformat(),),
                ).fetchall()
            return [_row_to_meal(r, _load_products(conn, r["id"])) for r in rows]

    def get_range(self, start: date, end: date, user_id: Optional[int] = None) -> List[Meal]:
        with self.db.connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    "SELECT * FROM meals WHERE meal_date BETWEEN ? AND ? AND user_id=? ORDER BY meal_date, meal_type",
                    (start.isoformat(), end.isoformat(), user_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM meals WHERE meal_date BETWEEN ? AND ? ORDER BY meal_date, meal_type",
                    (start.isoformat(), end.isoformat()),
                ).fetchall()
            return [_row_to_meal(r, _load_products(conn, r["id"])) for r in rows]

    def get_all(self, user_id: Optional[int] = None) -> List[Meal]:
        with self.db.connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    "SELECT * FROM meals WHERE user_id=? ORDER BY meal_date DESC, meal_type",
                    (user_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM meals ORDER BY meal_date DESC, meal_type"
                ).fetchall()
            return [_row_to_meal(r, _load_products(conn, r["id"])) for r in rows]

    def get_recent(self, days: int = 14, user_id: Optional[int] = None) -> List[Meal]:
        with self.db.connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    "SELECT * FROM meals WHERE meal_date >= date('now',?) AND user_id=? ORDER BY meal_date DESC, meal_type",
                    (f"-{days} days", user_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM meals WHERE meal_date >= date('now',?) ORDER BY meal_date DESC, meal_type",
                    (f"-{days} days",),
                ).fetchall()
            return [_row_to_meal(r, _load_products(conn, r["id"])) for r in rows]
