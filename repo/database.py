"""SQLite connection manager and schema initialiser — stdlib only."""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "meals.db"


class Database:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        self._init_users()
        self._init_meals()
        self._init_templates()
        self._init_shopping()
        self._init_weekly_menu()
        self._init_family()
        self._init_recommendation_settings()
        self._init_fridge()
        self._run_migrations()

    # ── table creation ────────────────────────────────────────────────────────

    def _init_users(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT    NOT NULL UNIQUE,
                    email         TEXT    NOT NULL UNIQUE,
                    password_hash TEXT    NOT NULL,
                    salt          TEXT    NOT NULL,
                    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    token      TEXT    PRIMARY KEY,
                    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
                    expires_at TEXT    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS password_resets (
                    token      TEXT    PRIMARY KEY,
                    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
                    expires_at TEXT    NOT NULL,
                    used       INTEGER NOT NULL DEFAULT 0
                );
            """)

    def _init_meals(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS meals (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id   INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name      TEXT    NOT NULL,
                    meal_type TEXT    NOT NULL CHECK(meal_type IN ('breakfast','lunch','dinner','snack')),
                    meal_date TEXT    NOT NULL,
                    notes     TEXT    DEFAULT '',
                    recipe    TEXT    DEFAULT '',
                    calories  INTEGER
                );

                CREATE TABLE IF NOT EXISTS products (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    meal_id  INTEGER NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
                    name     TEXT    NOT NULL,
                    quantity TEXT    DEFAULT ''
                );

                CREATE INDEX IF NOT EXISTS idx_meals_date    ON meals(meal_date);
                CREATE INDEX IF NOT EXISTS idx_products_meal ON products(meal_id);
            """)

    def _init_templates(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS recipe_templates (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name       TEXT    NOT NULL,
                    meal_type  TEXT    NOT NULL CHECK(meal_type IN ('breakfast','lunch','dinner','snack')),
                    meal_types TEXT    NOT NULL DEFAULT '[]',
                    notes      TEXT    DEFAULT '',
                    recipe     TEXT    DEFAULT '',
                    calories   INTEGER,
                    UNIQUE(user_id, name)
                );

                CREATE TABLE IF NOT EXISTS template_products (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER NOT NULL REFERENCES recipe_templates(id) ON DELETE CASCADE,
                    name        TEXT    NOT NULL,
                    quantity    TEXT    DEFAULT ''
                );

                CREATE INDEX IF NOT EXISTS idx_tpl_products ON template_products(template_id);
            """)

    def _init_shopping(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS shopping_list (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id   INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    item      TEXT    NOT NULL,
                    quantity  TEXT    DEFAULT '',
                    sources   TEXT    NOT NULL DEFAULT '{}',
                    done      INTEGER NOT NULL DEFAULT 0,
                    added_at  TEXT    NOT NULL DEFAULT (date('now'))
                );
            """)

    def _init_weekly_menu(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS weekly_menu (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id      INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    week_start   TEXT    NOT NULL,
                    day_offset   INTEGER NOT NULL CHECK(day_offset BETWEEN 0 AND 6),
                    slot         TEXT    NOT NULL CHECK(slot IN ('breakfast','lunch','dinner')),
                    meal_name    TEXT    NOT NULL DEFAULT '',
                    products_json TEXT   NOT NULL DEFAULT '[]',
                    UNIQUE(user_id, week_start, day_offset, slot)
                );
            """)

    def _init_family(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
                -- A family group links users who share data.
                -- The owner creates the group; others join via invite.
                CREATE TABLE IF NOT EXISTS family_groups (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name       TEXT    NOT NULL DEFAULT 'Family',
                    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
                );

                -- Members of a family group (including the owner).
                CREATE TABLE IF NOT EXISTS family_members (
                    group_id   INTEGER NOT NULL REFERENCES family_groups(id) ON DELETE CASCADE,
                    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    status     TEXT    NOT NULL DEFAULT 'pending'
                               CHECK(status IN ('pending','active')),
                    invited_at TEXT    NOT NULL DEFAULT (datetime('now')),
                    PRIMARY KEY (group_id, user_id)
                );

                CREATE INDEX IF NOT EXISTS idx_fm_user  ON family_members(user_id);
                CREATE INDEX IF NOT EXISTS idx_fm_group ON family_members(group_id);
            """)

    def _init_recommendation_settings(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
                -- Per-owner recommendation preferences (shared across a family,
                -- same as recipes/meals/shopping list).
                CREATE TABLE IF NOT EXISTS recommendation_settings (
                    user_id              INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    excluded_ingredients TEXT    NOT NULL DEFAULT '[]'
                );
            """)

    def _init_fridge(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
                -- What's currently on hand at home. Quantity is free text, same
                -- convention as shopping_list/products (e.g. '10 бр', '200g'),
                -- and can go to/below zero when more was used than was in stock.
                CREATE TABLE IF NOT EXISTS fridge_items (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id  INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name     TEXT    NOT NULL,
                    quantity TEXT    NOT NULL DEFAULT '',
                    added_at TEXT    NOT NULL DEFAULT (datetime('now'))
                );

                CREATE INDEX IF NOT EXISTS idx_fridge_user ON fridge_items(user_id);

                -- When a shopping-list export can only partially cover a need from
                -- the fridge, the shortfall that still had to be bought is tracked
                -- here, tagged by the same 'source' key used on shopping_list rows
                -- (e.g. 'wm:2026-09-30:0:dinner'). Once that source's meal is
                -- actually cooked, this exact amount — and only this amount — is
                -- subtracted from the fridge, since the rest was already taken out
                -- at export time. Re-exporting the same source replaces its row
                -- rather than accumulating (same idempotency rule as shopping_list).
                CREATE TABLE IF NOT EXISTS fridge_pending_consumption (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id  INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    source   TEXT    NOT NULL,
                    name     TEXT    NOT NULL,
                    quantity TEXT    NOT NULL,
                    UNIQUE(user_id, source, name)
                );

                CREATE INDEX IF NOT EXISTS idx_fpc_source ON fridge_pending_consumption(user_id, source);
            """)

    # ── migrations for existing databases ────────────────────────────────────

    def _run_migrations(self) -> None:
        with self.connect() as conn:
            # Add recipe column to meals if missing
            meal_cols = [r[1] for r in conn.execute("PRAGMA table_info(meals)").fetchall()]
            if "recipe" not in meal_cols:
                conn.execute("ALTER TABLE meals ADD COLUMN recipe TEXT DEFAULT ''")

            # Add user_id to meals if missing (existing rows get NULL = shared/legacy)
            if "user_id" not in meal_cols:
                conn.execute("ALTER TABLE meals ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")

            # Add calories (optional) to meals if missing
            if "calories" not in meal_cols:
                conn.execute("ALTER TABLE meals ADD COLUMN calories INTEGER")

            # Add user_id to recipe_templates if missing
            tpl_cols = [r[1] for r in conn.execute("PRAGMA table_info(recipe_templates)").fetchall()]
            if "user_id" not in tpl_cols:
                conn.execute("ALTER TABLE recipe_templates ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")

            # Add meal_types (JSON list) to recipe_templates if missing — backfill from the
            # legacy single-valued meal_type column so existing recipes keep their type.
            if "meal_types" not in tpl_cols:
                conn.execute("ALTER TABLE recipe_templates ADD COLUMN meal_types TEXT NOT NULL DEFAULT '[]'")
                for row in conn.execute("SELECT id, meal_type FROM recipe_templates").fetchall():
                    conn.execute(
                        "UPDATE recipe_templates SET meal_types=? WHERE id=?",
                        (json.dumps([row["meal_type"]]), row["id"]),
                    )

            # Add methods (JSON list, e.g. ["air_fryer","instant_pot"]) to recipe_templates.
            if "methods" not in tpl_cols:
                conn.execute("ALTER TABLE recipe_templates ADD COLUMN methods TEXT NOT NULL DEFAULT '[]'")

            # Add calories (optional) to recipe_templates if missing
            if "calories" not in tpl_cols:
                conn.execute("ALTER TABLE recipe_templates ADD COLUMN calories INTEGER")

            # Add user_id to shopping_list if missing
            shop_cols = [r[1] for r in conn.execute("PRAGMA table_info(shopping_list)").fetchall()]
            if "user_id" not in shop_cols:
                conn.execute("ALTER TABLE shopping_list ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")

            # Add sources (JSON: per-contribution provenance, for quantity merging) if missing
            if "sources" not in shop_cols:
                conn.execute("ALTER TABLE shopping_list ADD COLUMN sources TEXT NOT NULL DEFAULT '{}'")

            # Add user_id to weekly_menu if missing
            wm_cols = [r[1] for r in conn.execute("PRAGMA table_info(weekly_menu)").fetchall()]
            if "user_id" not in wm_cols:
                conn.execute("ALTER TABLE weekly_menu ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")

            # Create user_id indexes (safe to run even if they already exist)
            conn.executescript("""
                CREATE INDEX IF NOT EXISTS idx_meals_user ON meals(user_id);
                CREATE INDEX IF NOT EXISTS idx_tpl_user   ON recipe_templates(user_id);
                CREATE INDEX IF NOT EXISTS idx_shop_user  ON shopping_list(user_id);
                CREATE INDEX IF NOT EXISTS idx_wm_user    ON weekly_menu(user_id);
            """)

        # Migrate weekly_menu UNIQUE constraint to include user_id
        self._migrate_weekly_menu_unique()

        # Migrate CHECK constraints to include 'snack'
        self._migrate_snack_check()

    def _migrate_weekly_menu_unique(self) -> None:
        """Recreate weekly_menu if its UNIQUE constraint doesn't include user_id."""
        with self.connect() as conn:
            row = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='weekly_menu'"
            ).fetchone()
            if row is None:
                return
            # Old constraint was UNIQUE(week_start, day_offset, slot) — missing user_id
            if "user_id, week_start" not in row[0]:
                conn.executescript("""
                    PRAGMA foreign_keys = OFF;
                    CREATE TABLE weekly_menu_new (
                        id            INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id       INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        week_start    TEXT    NOT NULL,
                        day_offset    INTEGER NOT NULL CHECK(day_offset BETWEEN 0 AND 6),
                        slot          TEXT    NOT NULL CHECK(slot IN ('breakfast','lunch','dinner')),
                        meal_name     TEXT    NOT NULL DEFAULT '',
                        products_json TEXT    NOT NULL DEFAULT '[]',
                        UNIQUE(user_id, week_start, day_offset, slot)
                    );
                    INSERT INTO weekly_menu_new
                        (id, user_id, week_start, day_offset, slot, meal_name, products_json)
                    SELECT id, user_id, week_start, day_offset, slot, meal_name, products_json
                    FROM weekly_menu;
                    DROP TABLE weekly_menu;
                    ALTER TABLE weekly_menu_new RENAME TO weekly_menu;
                    CREATE INDEX IF NOT EXISTS idx_wm_user ON weekly_menu(user_id);
                    PRAGMA foreign_keys = ON;
                """)

    def _migrate_snack_check(self) -> None:
        with self.connect() as conn:
            for table in ("meals", "recipe_templates"):
                row = conn.execute(
                    f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'"
                ).fetchone()
                if row and "'snack'" not in row[0]:
                    self._recreate_with_snack(conn, table)

    def _recreate_with_snack(self, conn, table: str) -> None:
        cols = {
            "meals": """id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        name TEXT NOT NULL,
                        meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast','lunch','dinner','snack')),
                        meal_date TEXT NOT NULL, notes TEXT DEFAULT '', recipe TEXT DEFAULT '',
                        calories INTEGER""",
            "recipe_templates": """id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        name TEXT NOT NULL,
                        meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast','lunch','dinner','snack')),
                        notes TEXT DEFAULT '', recipe TEXT DEFAULT '',
                        meal_types TEXT NOT NULL DEFAULT '[]',
                        methods TEXT NOT NULL DEFAULT '[]',
                        calories INTEGER,
                        UNIQUE(user_id, name)""",
        }
        conn.executescript(f"""
            PRAGMA foreign_keys = OFF;
            CREATE TABLE IF NOT EXISTS {table}_new ({cols[table]});
            INSERT INTO {table}_new SELECT * FROM {table};
            DROP TABLE {table};
            ALTER TABLE {table}_new RENAME TO {table};
            PRAGMA foreign_keys = ON;
        """)
