"""CRUD operations for the shopping_list table (per-user)."""

import json
import uuid
from typing import Dict, List, Optional
from repo.database import Database
from utils.quantity import parse_qty as _parse_qty, format_qty as _format_qty, group_key as _group_key


def _load_sources(row) -> Dict[str, str]:
    """Per-source contributions behind a shopping-list row's total quantity.

    Rows created before this tracking existed (or a manual one-off add) have
    no sources recorded yet; their current quantity is folded in as a single
    '__legacy__' contribution so it isn't lost the first time something else
    merges into that row.
    """
    try:
        sources = json.loads(row["sources"]) if row["sources"] else {}
    except ValueError:
        sources = {}
    if not sources and (row["quantity"] or "").strip():
        sources = {"__legacy__": row["quantity"]}
    return sources


def _recompute_quantity(sources: Dict[str, str]) -> str:
    """Re-derive a row's displayed quantity from all of its sources.

    All values are expected to share a group key (see _group_key) since that's
    the only way they'd have been merged into the same row — so if they all
    parse, sum them; otherwise (untracked/unparseable) just keep the text.
    """
    parsed = [_parse_qty(v) for v in sources.values()]
    if sources and all(p is not None for p in parsed):
        unit = parsed[0][1]
        return _format_qty(sum(v for v, _ in parsed), unit)
    return next(iter(sources.values()), "")


class ShoppingRepo:
    def __init__(self, db: Database):
        self._db = db

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {
            "id":       row["id"],
            "item":     row["item"],
            "quantity": row["quantity"],
            "done":     bool(row["done"]),
            "added_at": row["added_at"],
        }

    # ── reads ─────────────────────────────────────────────────────────────────

    def get_all(self, user_id: Optional[int] = None) -> List[dict]:
        with self._db.connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    "SELECT * FROM shopping_list WHERE user_id=? ORDER BY done ASC, id ASC",
                    (user_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM shopping_list ORDER BY done ASC, id ASC"
                ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_by_id(self, item_id: int) -> Optional[dict]:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM shopping_list WHERE id = ?", (item_id,)
            ).fetchone()
        return self._row_to_dict(row) if row else None

    # ── writes ────────────────────────────────────────────────────────────────

    @staticmethod
    def _fetch_open_rows(conn, user_id: Optional[int]) -> List:
        if user_id is not None:
            return conn.execute(
                "SELECT id, item, quantity, sources FROM shopping_list WHERE done=0 AND user_id=?",
                (user_id,),
            ).fetchall()
        return conn.execute(
            "SELECT id, item, quantity, sources FROM shopping_list WHERE done=0 AND user_id IS NULL"
        ).fetchall()

    @classmethod
    def _build_index(cls, conn, user_id: Optional[int]) -> Dict[str, List[dict]]:
        """item name (lower) -> open rows, each carrying its live sources map."""
        index: Dict[str, List[dict]] = {}
        for r in cls._fetch_open_rows(conn, user_id):
            index.setdefault(r["item"].strip().lower(), []).append({
                "id": r["id"], "quantity": r["quantity"], "sources": _load_sources(r),
            })
        return index

    @staticmethod
    def _merge_entry(conn, user_id, index: Dict[str, List[dict]],
                     item: str, quantity: str, source: Optional[str]) -> int:
        """Fold one {item, quantity} contribution from `source` into the list.

        A contribution from a source that's already recorded on a row simply
        replaces its own prior value there (so re-running the same export is
        a no-op), while a new source adds its amount on top — but only when
        the quantities land on the same group key (matching unit, or identical
        untouchable text); otherwise it becomes its own separate line, as
        happened before any of this merging existed.
        """
        item, quantity = item.strip(), quantity.strip()
        if not source:
            source = f"anon:{uuid.uuid4().hex}"
        name_key = item.lower()
        new_group = _group_key(quantity)

        for row in index.get(name_key, []):
            if _group_key(row["quantity"]) == new_group:
                row["sources"][source] = quantity
                row["quantity"] = _recompute_quantity(row["sources"])
                conn.execute(
                    "UPDATE shopping_list SET quantity=?, sources=? WHERE id=?",
                    (row["quantity"], json.dumps(row["sources"]), row["id"]),
                )
                return row["id"]

        sources = {source: quantity}
        new_qty = _recompute_quantity(sources)
        cur = conn.execute(
            "INSERT INTO shopping_list (item, quantity, user_id, sources) VALUES (?,?,?,?)",
            (item, new_qty, user_id, json.dumps(sources)),
        )
        new_id = cur.lastrowid
        index.setdefault(name_key, []).append({"id": new_id, "quantity": new_qty, "sources": sources})
        return new_id

    def add(self, item: str, quantity: str = "", user_id: Optional[int] = None,
            source: Optional[str] = None) -> dict:
        with self._db.connect() as conn:
            index = self._build_index(conn, user_id)
            row_id = self._merge_entry(conn, user_id, index, item, quantity,
                                       source or f"manual:{uuid.uuid4().hex}")
        return self.get_by_id(row_id)

    def add_many(self, items: List[dict], user_id: Optional[int] = None) -> List[dict]:
        """Bulk-add a list of {item, quantity, source} dicts.

        `source` identifies where a contribution came from (e.g. a specific
        recipe or a weekly-menu slot). Two different sources needing the same
        amount of the same ingredient both count — nothing is silently
        collapsed — but re-sending the same source's contribution again (e.g.
        clicking "Add to Shopping List" again unchanged) doesn't keep piling
        on, since it replaces that source's own prior value rather than
        adding another one. Entries with no source behave as before: always
        additive, never idempotent — that's correct for manual, one-off adds.
        """
        touched_ids: List[int] = []
        with self._db.connect() as conn:
            index = self._build_index(conn, user_id)
            for entry in items:
                row_id = self._merge_entry(
                    conn, user_id, index,
                    entry["item"], entry.get("quantity", ""), entry.get("source"),
                )
                if row_id not in touched_ids:
                    touched_ids.append(row_id)
        return [self.get_by_id(row_id) for row_id in touched_ids]

    def toggle_done(self, item_id: int, user_id: Optional[int] = None) -> Optional[dict]:
        with self._db.connect() as conn:
            if user_id is not None:
                cur = conn.execute(
                    "UPDATE shopping_list SET done = NOT done WHERE id=? AND user_id=?", (item_id, user_id)
                )
            else:
                cur = conn.execute(
                    "UPDATE shopping_list SET done = NOT done WHERE id=?", (item_id,)
                )
            if cur.rowcount == 0:
                return None
        return self.get_by_id(item_id)

    def update(self, item_id: int, item: str, quantity: str, user_id: Optional[int] = None) -> Optional[dict]:
        with self._db.connect() as conn:
            if user_id is not None:
                cur = conn.execute(
                    "UPDATE shopping_list SET item=?, quantity=? WHERE id=? AND user_id=?",
                    (item.strip(), quantity.strip(), item_id, user_id),
                )
            else:
                cur = conn.execute(
                    "UPDATE shopping_list SET item=?, quantity=? WHERE id=?",
                    (item.strip(), quantity.strip(), item_id),
                )
            if cur.rowcount == 0:
                return None
        return self.get_by_id(item_id)

    def delete(self, item_id: int, user_id: Optional[int] = None) -> bool:
        with self._db.connect() as conn:
            if user_id is not None:
                affected = conn.execute(
                    "DELETE FROM shopping_list WHERE id=? AND user_id=?", (item_id, user_id)
                ).rowcount
            else:
                affected = conn.execute(
                    "DELETE FROM shopping_list WHERE id=?", (item_id,)
                ).rowcount
        return affected > 0

    def get_done(self, user_id: Optional[int] = None) -> List[dict]:
        with self._db.connect() as conn:
            if user_id is not None:
                rows = conn.execute(
                    "SELECT * FROM shopping_list WHERE done=1 AND user_id=?", (user_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM shopping_list WHERE done=1 AND user_id IS NULL"
                ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def clear_done(self, user_id: Optional[int] = None) -> int:
        with self._db.connect() as conn:
            if user_id is not None:
                affected = conn.execute(
                    "DELETE FROM shopping_list WHERE done=1 AND user_id=?", (user_id,)
                ).rowcount
            else:
                affected = conn.execute(
                    "DELETE FROM shopping_list WHERE done=1 AND user_id IS NULL"
                ).rowcount
        return affected
