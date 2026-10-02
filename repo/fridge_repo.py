"""CRUD for the fridge_items table (per-user) — what's currently on hand.

Quantity uses the same free-text convention as the shopping list ('10 бр',
'200g'), and the same "combine only when the unit matches" rule. Unlike the
shopping list, fridge changes are never deduped by source — every addition or
consumption is a real one-time event and should always accumulate.
"""

from typing import Dict, List, Optional
from repo.database import Database
from utils.quantity import parse_qty, format_qty, group_key


class FridgeRepo:
    def __init__(self, db: Database):
        self._db = db

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {"id": row["id"], "name": row["name"], "quantity": row["quantity"], "added_at": row["added_at"]}

    # ── reads ─────────────────────────────────────────────────────────────────

    def get_all(self, user_id: Optional[int] = None) -> List[dict]:
        with self._db.connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    "SELECT * FROM fridge_items WHERE user_id=? ORDER BY name COLLATE NOCASE", (user_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM fridge_items WHERE user_id IS NULL ORDER BY name COLLATE NOCASE"
                ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_by_id(self, item_id: int) -> Optional[dict]:
        with self._db.connect() as conn:
            row = conn.execute("SELECT * FROM fridge_items WHERE id=?", (item_id,)).fetchone()
        return self._row_to_dict(row) if row else None

    # ── internal indexing (mirrors ShoppingRepo's live-index pattern) ──────────

    @staticmethod
    def _fetch_rows(conn, user_id: Optional[int]) -> List:
        if user_id is not None:
            return conn.execute(
                "SELECT id, name, quantity FROM fridge_items WHERE user_id=?", (user_id,)
            ).fetchall()
        return conn.execute("SELECT id, name, quantity FROM fridge_items WHERE user_id IS NULL").fetchall()

    @classmethod
    def _build_index(cls, conn, user_id: Optional[int]) -> Dict[str, List[dict]]:
        index: Dict[str, List[dict]] = {}
        for r in cls._fetch_rows(conn, user_id):
            index.setdefault(r["name"].strip().lower(), []).append(
                {"id": r["id"], "name": r["name"], "quantity": r["quantity"]}
            )
        return index

    @staticmethod
    def _merge_add(conn, user_id, index: Dict[str, List[dict]], name: str, quantity: str) -> int:
        """Add `quantity` of `name` into a matching same-unit row, or create one."""
        name, quantity = name.strip(), quantity.strip()
        name_key = name.lower()
        new_group = group_key(quantity)
        parsed_new = parse_qty(quantity)

        if parsed_new is not None:
            for row in index.get(name_key, []):
                if group_key(row["quantity"]) == new_group:
                    cur_val, unit = parse_qty(row["quantity"])
                    new_qty = format_qty(cur_val + parsed_new[0], unit)
                    conn.execute("UPDATE fridge_items SET quantity=? WHERE id=?", (new_qty, row["id"]))
                    row["quantity"] = new_qty
                    return row["id"]

        cur = conn.execute(
            "INSERT INTO fridge_items (user_id, name, quantity) VALUES (?,?,?)",
            (user_id, name, quantity),
        )
        new_id = cur.lastrowid
        index.setdefault(name_key, []).append({"id": new_id, "name": name, "quantity": quantity})
        return new_id

    # ── writes ────────────────────────────────────────────────────────────────

    def add_or_merge(self, name: str, quantity: str, user_id: Optional[int] = None) -> dict:
        with self._db.connect() as conn:
            index = self._build_index(conn, user_id)
            row_id = self._merge_add(conn, user_id, index, name, quantity)
        return self.get_by_id(row_id)

    def add_many(self, items: List[dict], user_id: Optional[int] = None) -> List[dict]:
        """Bulk-add a list of {name, quantity} dicts (manual multi-line entry,
        or automatic restocking from cleared shopping-list items)."""
        touched: List[int] = []
        with self._db.connect() as conn:
            index = self._build_index(conn, user_id)
            for entry in items:
                name = entry.get("name", "")
                if not name.strip():
                    continue
                row_id = self._merge_add(conn, user_id, index, name, entry.get("quantity", ""))
                if row_id not in touched:
                    touched.append(row_id)
        return [self.get_by_id(i) for i in touched]

    @staticmethod
    def _record_pending(conn, user_id, source: str, name: str, quantity: str) -> None:
        conn.execute(
            """INSERT INTO fridge_pending_consumption (user_id, source, name, quantity) VALUES (?,?,?,?)
               ON CONFLICT(user_id, source, name) DO UPDATE SET quantity=excluded.quantity""",
            (user_id, source, name.lower(), quantity),
        )

    @staticmethod
    def _clear_pending(conn, user_id, source: str, name: str) -> None:
        conn.execute(
            "DELETE FROM fridge_pending_consumption WHERE user_id IS ? AND source=? AND name=?",
            (user_id, source, name.lower()),
        )

    def reconcile_with_shopping_list(self, items: List[dict], user_id: Optional[int] = None) -> List[dict]:
        """Given {item, quantity, source} entries about to be added to the
        shopping list, use up whatever's already in the fridge instead of
        buying it again. Fully-covered entries are dropped; partially-covered
        ones have their quantity reduced to just what's still needed. Units
        must match exactly (same rule as shopping-list merging) — anything
        unparseable or unit-mismatched passes through untouched.

        When an entry has a `source` (e.g. a specific weekly-menu slot), the
        remaining shortfall — the part that still has to be bought — is
        recorded against that source, so `consume_pending` can later subtract
        exactly that amount (and no more) once the meal is actually cooked.
        """
        result: List[dict] = []
        with self._db.connect() as conn:
            index = self._build_index(conn, user_id)
            for entry in items:
                name = entry.get("item", "").strip()
                source = entry.get("source")
                needed = parse_qty(entry.get("quantity", ""))
                if not name or needed is None:
                    result.append(entry)
                    continue
                need_val, unit = needed

                match = None
                for row in index.get(name.lower(), []):
                    have = parse_qty(row["quantity"])
                    if have is not None and have[1] == unit and have[0] > 0:
                        match = row
                        break
                if match is None:
                    if source:
                        self._record_pending(conn, user_id, source, name, format_qty(need_val, unit))
                    result.append(entry)
                    continue

                have_val, _ = parse_qty(match["quantity"])
                take = min(have_val, need_val)
                new_qty = format_qty(have_val - take, unit)
                conn.execute("UPDATE fridge_items SET quantity=? WHERE id=?", (new_qty, match["id"]))
                match["quantity"] = new_qty

                remaining = need_val - take
                if remaining > 1e-9:
                    if source:
                        self._record_pending(conn, user_id, source, name, format_qty(remaining, unit))
                    result.append({**entry, "quantity": format_qty(remaining, unit)})
                else:
                    # fully covered by what's already in the fridge — drop it, and
                    # clear any stale shortfall a previous export might have left
                    if source:
                        self._clear_pending(conn, user_id, source, name)
        return result

    def consume_pending(self, source: str, user_id: Optional[int] = None) -> int:
        """Settle a source's recorded shortfall: subtract exactly what was
        bought specifically for it from the fridge (not the recipe's full
        amount — the rest was already taken out at export time), then clear
        the tracking. Called when a meal is marked "Cooked"."""
        with self._db.connect() as conn:
            if user_id is not None:
                pending = conn.execute(
                    "SELECT id, name, quantity FROM fridge_pending_consumption WHERE user_id=? AND source=?",
                    (user_id, source),
                ).fetchall()
            else:
                pending = conn.execute(
                    "SELECT id, name, quantity FROM fridge_pending_consumption WHERE user_id IS NULL AND source=?",
                    (source,),
                ).fetchall()
            if not pending:
                return 0

            index = self._build_index(conn, user_id)
            settled = 0
            for p in pending:
                owed = parse_qty(p["quantity"])
                if owed is not None:
                    owed_val, unit = owed
                    for row in index.get(p["name"], []):
                        have = parse_qty(row["quantity"])
                        if have is not None and have[1] == unit:
                            new_qty = format_qty(have[0] - owed_val, unit)
                            conn.execute("UPDATE fridge_items SET quantity=? WHERE id=?", (new_qty, row["id"]))
                            row["quantity"] = new_qty
                            break
                conn.execute("DELETE FROM fridge_pending_consumption WHERE id=?", (p["id"],))
                settled += 1
        return settled

    def update(self, item_id: int, name: str, quantity: str, user_id: Optional[int] = None) -> Optional[dict]:
        with self._db.connect() as conn:
            if user_id is not None:
                cur = conn.execute(
                    "UPDATE fridge_items SET name=?, quantity=? WHERE id=? AND user_id=?",
                    (name.strip(), quantity.strip(), item_id, user_id),
                )
            else:
                cur = conn.execute(
                    "UPDATE fridge_items SET name=?, quantity=? WHERE id=?",
                    (name.strip(), quantity.strip(), item_id),
                )
            if cur.rowcount == 0:
                return None
        return self.get_by_id(item_id)

    def delete(self, item_id: int, user_id: Optional[int] = None) -> bool:
        with self._db.connect() as conn:
            if user_id is not None:
                affected = conn.execute(
                    "DELETE FROM fridge_items WHERE id=? AND user_id=?", (item_id, user_id)
                ).rowcount
            else:
                affected = conn.execute("DELETE FROM fridge_items WHERE id=?", (item_id,)).rowcount
        return affected > 0
