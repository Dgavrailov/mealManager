"""CRUD for per-user recommendation preferences (currently: excluded ingredients)."""

import json
from typing import List
from repo.database import Database


class RecommendationSettingsRepo:
    def __init__(self, db: Database):
        self._db = db

    def get_excluded_ingredients(self, user_id: int) -> List[str]:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT excluded_ingredients FROM recommendation_settings WHERE user_id=?",
                (user_id,),
            ).fetchone()
        if row is None:
            return []
        try:
            return json.loads(row["excluded_ingredients"])
        except ValueError:
            return []

    def set_excluded_ingredients(self, user_id: int, names: List[str]) -> List[str]:
        with self._db.connect() as conn:
            conn.execute(
                """INSERT INTO recommendation_settings (user_id, excluded_ingredients) VALUES (?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET excluded_ingredients=excluded.excluded_ingredients""",
                (user_id, json.dumps(names)),
            )
        return names
