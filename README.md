# Meal Manager (stdlib-only)

A personal meal-planning web app: log what you eat, keep a recipe book, plan
a weekly menu, get diversity-aware meal recommendations, and generate a
shopping list from any of it. Backend is pure Python standard library
(`http.server` + `sqlite3`, no pip installs); the UI is a single-page app
(vanilla JS + Bootstrap via CDN) served at `/ui`.

## Start

```bash
cd /home/dg046388/my_scripts/meal_manager_stdlib_v1

python3.14 main.py --host 127.0.0.1 --port 8080
```

Then open **http://127.0.0.1:8080/ui** in a browser and register an account.

Other flags:

```bash
# Seed 14 days of sample data on startup (idempotent)
python3.14 main.py --seed

# Print terminal charts for the last 14 days of meals, then exit
python3.14 main.py --charts

# Defaults if omitted: --host 0.0.0.0 --port 8000
python3.14 main.py
```

The server auto-creates and migrates `data/meals.db` (SQLite) on every
startup — no separate setup step needed.

### Optional: email for password reset

Copy `.env.example`-style config into `.env` (same directory as `main.py`)
to send real password-reset emails via Gmail SMTP:

```
SMTP_USER=you@gmail.com
SMTP_PASS=your_app_password
SMTP_FROM=you@gmail.com
SECRET_KEY=some-random-string
```

Without `SMTP_USER` configured, "forgot password" still works — the reset
link is just printed to the server console instead of emailed. Inline `#
comments` in `.env` values are stripped automatically.

---

## Features

- **Accounts** — register/login/logout, forgot/reset password, sessions via
  an HttpOnly cookie (3-day expiry). Passwords are hashed with PBKDF2-SHA256
  (200,000 iterations); older accounts are upgraded transparently on next login.
- **Family sharing** — one user creates a family group and invites others by
  email; once accepted, members share the same meals, recipes, shopping list,
  weekly menu, and recommendation exclusions.
- **Meal Log** — record what you actually ate, with ingredients, an optional
  **calorie count**, notes, and an optional recipe write-up, filterable by date.
- **Recipes** — a reusable recipe book (separate from the meal log). Each
  recipe can be tagged with **multiple meal types** at once (e.g. usable for
  both lunch and dinner), optional **cooking-method tags** (Air Fryer /
  Instant Pot), and an optional **calorie count**. Search matches recipe
  names only; a dropdown filters by cooking method.
- **Snacks** — by default shows only recipe-book entries tagged "snack"
  (📖 Snack Recipes, undated); a checkbox reveals/searches your logged snack
  entries (from the Meal Log, by date) alongside them.
- **Recommendations** — suggests a single day or a full week of
  breakfast/lunch/dinner, favoring recipes with the least ingredient overlap
  with recent meals, and never repeating a recipe within the same day. An
  "Exclude ingredients from scoring" list (saved to your account, editable
  any time) lets you permanently ignore specific ingredients across every
  future recommendation.
- **Weekly Menu** — a 7-day × 3-slot planner. Click a filled-in meal name to
  see its full ingredients/recipe/notes/calories, same as expanding it in the
  Recipes tab. Recommendations can be pushed straight into it.
- **Visualize** — meal-type distribution, top ingredients, a diversity trend,
  and a daily-coverage view showing accumulated calories per day (plus a
  period average). Pick a time range: 14 days (default), 1/3/6/12 months,
  all time, or a custom start/end date.
- **Shopping List** — add ingredients from a recipe, a snack, a weekly-menu
  day, or a recommendation. Quantities for the same ingredient are summed
  when the unit matches (e.g. "200g" + "300g" → "500 g"); mismatched or
  unparseable units are kept as separate lines. Re-adding from the same
  recipe/slot again is idempotent (it won't keep piling up); two different
  recipes needing the same amount both count.

---

## Project structure

```
meal_manager_stdlib_v1/
├── main.py                        # Entry point (argparse, wires everything up, serve_forever)
├── config.py                      # Loads .env (SMTP + SECRET_KEY + APP_BASE_URL)
├── .env                           # SMTP credentials (optional, gitignored in spirit)
├── data/
│   └── meals.db                   # SQLite DB (auto-created + auto-migrated)
├── models/
│   ├── meal_type.py               # MealType enum (breakfast/lunch/dinner/snack)
│   ├── product.py                 # Product dataclass (ingredient + quantity)
│   └── meal.py                    # Meal dataclass (incl. optional calories)
├── dto/
│   └── validators.py              # Request validation (no Pydantic)
├── repo/
│   ├── database.py                # SQLite connection, schema, and migrations
│   ├── meal_repo.py                # CRUD for logged meals + products
│   ├── template_repo.py           # CRUD for recipe templates (meal_types, methods, calories)
│   ├── shopping_repo.py           # Shopping list CRUD + quantity-merge logic
│   ├── weekly_menu_repo.py        # CRUD for the weekly menu grid
│   └── recommendation_settings_repo.py  # Saved "excluded ingredients" list
├── services/
│   ├── meal_service.py            # Meal business logic
│   ├── recommendation_agent.py    # Diversity-aware recommender
│   ├── auth_service.py            # Registration, login, sessions, password reset
│   └── family_service.py          # Family group creation/invites/sharing
├── rest/
│   ├── router.py                  # HTTP routing, auth, JSON in/out (http.server)
│   ├── templates_router.py        # Recipe template endpoints (mixin)
│   └── ui.py                      # The entire single-page UI (HTML+CSS+JS as one string)
├── utils/
│   ├── data_generator.py          # Sample data seeder (--seed)
│   └── visualizer.py              # Terminal charts (--charts)
└── seed_test_data.py              # Standalone script for bulk test data
```

---

## Data model (SQLite, `data/meals.db`)

- `users`, `sessions`, `password_resets` — auth.
- `family_groups`, `family_members` — family sharing (`status`: pending/active).
- `meals` + `products` — logged meal instances (one `meal_type` each), with
  an optional `calories` integer column.
- `recipe_templates` + `template_products` — the recipe book. `meal_types`
  and `methods` are stored as JSON arrays (e.g. `["lunch","dinner"]`,
  `["air_fryer"]`); `meal_type` is kept as the first selected type for
  backward compatibility and sorting; `calories` is optional.
- `shopping_list` — `sources` (JSON) tracks which recipe/meal/slot
  contributed how much of each line, which is what makes quantity merging
  idempotent.
- `weekly_menu` — one row per (week_start, day_offset, slot); `products_json`
  holds that slot's ingredient list.
- `recommendation_settings` — one row per owner; `excluded_ingredients`
  (JSON array of ingredient names) is always applied when generating
  recommendations for that owner.

All tables except `users`/`sessions`/`family_*` are scoped by `user_id`
(family members share data by resolving to the group owner's `user_id` — see
`FamilyService.get_effective_user_id`).

---

## API reference

All routes are JSON in/out. Routes marked 🔒 require a valid session cookie
(set automatically by `/auth/login` or `/auth/register`), and are scoped to
the requesting user's (or their family's) own data.

**Auth**
- `POST /auth/register`, `POST /auth/login`, `POST /auth/logout` 🔒
- `GET /auth/me` 🔒
- `POST /auth/forgot-password`, `POST /auth/reset-password`

**Meals**
- `GET /meals/` 🔒 — all meals, or `?meal_date=YYYY-MM-DD`
- `POST /meals/` 🔒 — create — body may include optional `calories` (integer ≥ 0)
- `GET /meals/range?start=...&end=...` 🔒
- `GET /meals/{id}` 🔒, `PUT /meals/{id}` 🔒, `DELETE /meals/{id}` 🔒

**Recipes (templates)**
- `GET /templates/` 🔒, `POST /templates/` 🔒
- `GET /templates/{id}` 🔒, `PUT /templates/{id}` 🔒, `DELETE /templates/{id}` 🔒
  — body takes `meal_types: [...]` (required, one or more), optional
  `methods: [...]` (`air_fryer` / `instant_pot`), and optional `calories`

**Recommendations**
- `GET /recommendations/next-day?target_date=...` 🔒
- `GET /recommendations/week?start_date=...` 🔒
- `GET /recommendations/settings` 🔒 — `{"excluded_ingredients": [...]}`
- `PUT /recommendations/settings` 🔒 — body `{"excluded_ingredients": [...]}`,
  replaces the saved list (case-insensitive de-duplicated)

**Shopping list**
- `GET /shopping/` 🔒, `POST /shopping/` 🔒 (single item), `POST /shopping/bulk` 🔒
  — bulk items may include `source` (e.g. `template:12`) to make re-adding
  idempotent; omit it for a plain one-off manual add
- `PUT /shopping/{id}/toggle` 🔒, `PUT /shopping/{id}` 🔒, `DELETE /shopping/{id}` 🔒
- `DELETE /shopping/done` 🔒 — clear checked-off items

**Weekly menu**
- `GET /weekly-menu/?week_start=YYYY-MM-DD` 🔒
- `PUT /weekly-menu/slot` 🔒, `POST /weekly-menu/from-rec` 🔒 (bulk from a
  recommendation), `DELETE /weekly-menu/clear?week_start=...` 🔒

**Family**
- `GET /family/` 🔒, `POST /family/create` 🔒, `POST /family/invite` 🔒,
  `POST /family/accept` 🔒, `POST /family/leave` 🔒, `DELETE /family/member/{id}` 🔒

### Example: add a meal

```bash
curl -X POST http://127.0.0.1:8080/meals/ \
  -H "Content-Type: application/json" \
  -b "session=<your-session-cookie>" \
  -d '{
    "name": "Avocado toast",
    "meal_type": "breakfast",
    "meal_date": "2026-03-10",
    "calories": 350,
    "products": [
      {"name": "bread",   "quantity": "2 slices"},
      {"name": "avocado", "quantity": "1 pcs"}
    ],
    "notes": "Add chili flakes"
  }'
```

---

## Recommendation agent

- Candidates come from **Recipes** matching the target slot (a recipe tagged
  both lunch and dinner is eligible for either); falls back to meal-log
  history only if no recipes exist at all for that slot.
- Looks at the **last 14 days** of meals for ingredient-overlap scoring.
- **Blocks** a recipe from repeating in the same slot within the last
  **4 days**, and never picks the same recipe twice on the same day across
  slots. (This block is per-slot and based on your logged meal history, not
  on a recipe's tags — a recipe eaten as lunch doesn't block it from being
  suggested as dinner a couple of days later.)
- Scores candidates by ingredient diversity — less overlap with recently
  eaten ingredients scores higher — and ties are rotated by date so a full
  week doesn't get stuck on one option.
- **Ingredients that are near-universal across your recipes** (salt, oil,
  water, ...) are automatically down-weighted using an inverse-document-frequency
  calculation over your own recipe book, so they don't drown out ingredients
  that actually distinguish one meal from another. This adapts to *your*
  recipes — no hardcoded ignore-list.
- **Seasoning-scale quantities** (a pinch, a teaspoon/ч.л., a tablespoon/с.л.,
  a cup or glass/ч.ч.) are fully excluded from scoring regardless of how
  common the ingredient is, in both English and Bulgarian units.
- **Manually excluded ingredients** (Recommend tab → "Exclude ingredients
  from scoring", saved via `/recommendations/settings`) are always applied on
  top of the above. Matching is an **exact, case-insensitive string match** —
  typing "egg" will *not* also exclude an ingredient named "eggs"; add both
  forms if your recipes are inconsistent about singular/plural naming.
- Returns a `diversity_score` (0–1) and a human-readable `reason` per slot.

---

## Known limitations

- Shopping-list quantity merging tracks contributions per source, but if you
  remove an ingredient from a recipe entirely, its old contribution to the
  shopping list isn't retracted on re-export — only added/updated.
- Excluded-ingredient matching (manual list) is exact-string, not
  plural-aware or fuzzy — see the Recommendation agent section above.
- The dev server (`http.server`) is single-process/synchronous — fine for
  one household's worth of traffic, not meant to be exposed publicly on the
  internet.

Previously listed here and since fixed: unscoped single-record access on
meals/recipes/shopping items (now checks ownership), plain-SHA256 password
hashing (now PBKDF2, with existing accounts upgraded transparently on next
login), and stack traces leaking into error responses (now logged
server-side only).
