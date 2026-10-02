"""CRUD for the weekly_menu table (per-user).

A "week" is identified by its Monday date (week_start, ISO string YYYY-MM-DD).
Each week has 7 days × 3 slots = 21 rows (auto-created on first get).
"""

import json
from datetime import date, timedelta
from typing import List, Optional

from repo.database import Database

SLOTS = ("breakfast", "lunch", "dinner")
DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def _monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


class WeeklyMenuRepo:
    def __init__(self, db: Database):
        self._db = db

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {
            "id":         row["id"],
            "week_start": row["week_start"],
            "day_offset": row["day_offset"],
            "day_name":   DAY_NAMES[row["day_offset"]],
            "slot":       row["slot"],
            "meal_name":  row["meal_name"],
            "products":   json.loads(row["products_json"]),
        }

    def _upsert_slot(self, conn, user_id, week_start, day_offset, slot,
                     meal_name="", products_json="[]") -> None:
        """Insert or update a single slot row."""
        conn.execute(
            """INSERT INTO weekly_menu (user_id, week_start, day_offset, slot, meal_name, products_json)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id, week_start, day_offset, slot)
               DO UPDATE SET meal_name=excluded.meal_name,
                             products_json=excluded.products_json""",
            (user_id, week_start, day_offset, slot, meal_name, products_json),
        )

    def _ensure_week(self, conn, week_start: str, user_id) -> None:
        """Insert empty rows for every day/slot if they don't exist yet."""
        for day in range(7):
            for slot in SLOTS:
                conn.execute(
                    """INSERT OR IGNORE INTO weekly_menu
                       (user_id, week_start, day_offset, slot, meal_name, products_json)
                       VALUES (?, ?, ?, ?, '', '[]')""",
                    (user_id, week_start, day, slot),
                )

    def _fetch_slot(self, conn, user_id, week_start, day_offset, slot) -> dict:
        row = conn.execute(
            "SELECT * FROM weekly_menu WHERE user_id IS ? AND week_start=? AND day_offset=? AND slot=?",
            (user_id, week_start, day_offset, slot),
        ).fetchone()
        if row is None:
            raise RuntimeError(f"Slot not found after upsert: {week_start} d{day_offset} {slot} uid={user_id}")
        return self._row_to_dict(row)

    # ── reads ─────────────────────────────────────────────────────────────────

    def get_week(self, week_start: Optional[date] = None,
                 user_id=None) -> List[dict]:
        ws = (_monday_of(week_start) if week_start else _monday_of(date.today())).isoformat()
        with self._db.connect() as conn:
            self._ensure_week(conn, ws, user_id)
            rows = conn.execute(
                "SELECT * FROM weekly_menu WHERE user_id IS ? AND week_start=? ORDER BY day_offset, slot",
                (user_id, ws),
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_current_week_start(self) -> str:
        return _monday_of(date.today()).isoformat()

    # ── writes ────────────────────────────────────────────────────────────────

    def set_slot(self, week_start: str, day_offset: int, slot: str,
                 meal_name: str, products: List[dict],
                 user_id=None) -> dict:
        """Upsert a single slot and return the saved row."""
        products_json = json.dumps(products)
        with self._db.connect() as conn:
            self._upsert_slot(conn, user_id, week_start, day_offset, slot,
                              meal_name.strip(), products_json)
            return self._fetch_slot(conn, user_id, week_start, day_offset, slot)

    def set_week_from_recommendation(self, week_start: str, days: List[dict],
                                     user_id=None) -> List[dict]:
        """Bulk-populate a week from a /recommendations/week response."""
        with self._db.connect() as conn:
            self._ensure_week(conn, week_start, user_id)
            for day_offset, day in enumerate(days):
                for slot in SLOTS:
                    rec = day.get(slot, {})
                    meal_name = rec.get("meal_name", "")
                    raw_products = rec.get("suggested_products", [])
                    products = [
                        {"name": p["name"] if isinstance(p, dict) else p,
                         "quantity": p.get("quantity", "") if isinstance(p, dict) else ""}
                        for p in raw_products
                    ]
                    self._upsert_slot(conn, user_id, week_start, day_offset, slot,
                                      meal_name, json.dumps(products))
            rows = conn.execute(
                "SELECT * FROM weekly_menu WHERE user_id IS ? AND week_start=? ORDER BY day_offset, slot",
                (user_id, week_start),
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def clear_week(self, week_start: str, user_id=None) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE weekly_menu SET meal_name='', products_json='[]' WHERE user_id IS ? AND week_start=?",
                (user_id, week_start),
            )
