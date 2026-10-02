"""
HTTP request router built on top of stdlib http.server.
Handles JSON in/out, routing, session auth, and error responses.
"""

import json
import re
import traceback
from datetime import date
from http.server import BaseHTTPRequestHandler
from typing import Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import config
from dto.validators import ValidationError, validate_meal_payload, validate_date
from services.meal_service import MealService
from services.recommendation_agent import RecommendationAgent
from services.auth_service import AuthService
from services.family_service import FamilyService
from repo.template_repo import TemplateRepo
from repo.shopping_repo import ShoppingRepo
from repo.weekly_menu_repo import WeeklyMenuRepo
from repo.recommendation_settings_repo import RecommendationSettingsRepo
from repo.fridge_repo import FridgeRepo
from repo.ingredient_repo import IngredientRepo
from rest.ui import HTML
from rest.templates_router import TemplateHandlerMixin


# ── route table ───────────────────────────────────────────────────────────────
# Each entry: (METHOD, compiled-regex, handler-name, requires_auth)
_ROUTES: List[Tuple[str, re.Pattern, str, bool]] = [
    # Public
    ("GET",    re.compile(r"^/ui/?$"),                       "serve_ui",            False),
    ("GET",    re.compile(r"^/reset/?$"),                    "serve_reset_page",    False),
    ("GET",    re.compile(r"^/?$"),                          "health",              False),
    # Auth
    ("POST",   re.compile(r"^/auth/register/?$"),            "auth_register",       False),
    ("POST",   re.compile(r"^/auth/login/?$"),               "auth_login",          False),
    ("POST",   re.compile(r"^/auth/logout/?$"),              "auth_logout",         True),
    ("GET",    re.compile(r"^/auth/me/?$"),                  "auth_me",             True),
    ("POST",   re.compile(r"^/auth/forgot-password/?$"),     "auth_forgot",         False),
    ("POST",   re.compile(r"^/auth/reset-password/?$"),      "auth_reset",          False),
    # Meals
    ("GET",    re.compile(r"^/meals/?$"),                    "list_meals",          True),
    ("POST",   re.compile(r"^/meals/?$"),                    "create_meal",         True),
    ("GET",    re.compile(r"^/meals/range/?$"),              "meals_range",         True),
    ("GET",    re.compile(r"^/meals/(\d+)/?$"),              "get_meal",            True),
    ("PUT",    re.compile(r"^/meals/(\d+)/?$"),              "update_meal",         True),
    ("DELETE", re.compile(r"^/meals/(\d+)/?$"),              "delete_meal",         True),
    # Templates
    ("GET",    re.compile(r"^/templates/?$"),                "list_templates",      True),
    ("POST",   re.compile(r"^/templates/?$"),                "create_template",     True),
    ("GET",    re.compile(r"^/templates/(\d+)/?$"),          "get_template",        True),
    ("PUT",    re.compile(r"^/templates/(\d+)/?$"),          "update_template",     True),
    ("DELETE", re.compile(r"^/templates/(\d+)/?$"),          "delete_template",     True),
    # Recommendations
    ("GET",    re.compile(r"^/recommendations/next-day/?$"), "recommend_next_day",  True),
    ("GET",    re.compile(r"^/recommendations/week/?$"),     "recommend_week",      True),
    ("GET",    re.compile(r"^/recommendations/settings/?$"), "get_rec_settings",    True),
    ("PUT",    re.compile(r"^/recommendations/settings/?$"), "update_rec_settings", True),
    # Shopping
    ("GET",    re.compile(r"^/shopping/?$"),                 "list_shopping",       True),
    ("POST",   re.compile(r"^/shopping/?$"),                 "add_shopping",        True),
    ("POST",   re.compile(r"^/shopping/bulk/?$"),            "bulk_add_shopping",   True),
    ("PUT",    re.compile(r"^/shopping/(\d+)/toggle/?$"),    "toggle_shopping",     True),
    ("PUT",    re.compile(r"^/shopping/(\d+)/?$"),           "update_shopping",     True),
    ("DELETE", re.compile(r"^/shopping/(\d+)/?$"),           "delete_shopping",     True),
    ("DELETE", re.compile(r"^/shopping/done/?$"),            "clear_done_shopping", True),
    # Weekly menu
    ("GET",    re.compile(r"^/weekly-menu/?$"),              "get_weekly_menu",     True),
    ("PUT",    re.compile(r"^/weekly-menu/slot/?$"),         "set_weekly_menu_slot",True),
    ("POST",   re.compile(r"^/weekly-menu/from-rec/?$"),     "weekly_menu_from_rec",True),
    ("DELETE", re.compile(r"^/weekly-menu/clear/?$"),        "clear_weekly_menu",   True),
    # Fridge
    ("GET",    re.compile(r"^/fridge/?$"),                   "list_fridge",         True),
    ("POST",   re.compile(r"^/fridge/bulk/?$"),              "bulk_add_fridge",     True),
    ("POST",   re.compile(r"^/fridge/cooked/?$"),            "mark_cooked",         True),
    ("PUT",    re.compile(r"^/fridge/(\d+)/?$"),             "update_fridge_item",  True),
    ("DELETE", re.compile(r"^/fridge/(\d+)/?$"),             "delete_fridge_item",  True),
    # Ingredient unit dictionary
    ("GET",    re.compile(r"^/ingredients/units/?$"),        "list_ingredient_units", True),
    ("POST",   re.compile(r"^/ingredients/units/rename/?$"), "rename_ingredient_unit", True),
    # Family
    ("GET",    re.compile(r"^/family/?$"),                   "family_get",          True),
    ("POST",   re.compile(r"^/family/create/?$"),            "family_create",       True),
    ("POST",   re.compile(r"^/family/invite/?$"),            "family_invite",       True),
    ("POST",   re.compile(r"^/family/accept/?$"),            "family_accept",       True),
    ("POST",   re.compile(r"^/family/leave/?$"),             "family_leave",        True),
    ("DELETE", re.compile(r"^/family/member/(\d+)/?$"),      "family_remove",       True),
]


class MealRouter(TemplateHandlerMixin, BaseHTTPRequestHandler):
    """Injected via class attributes before the server starts."""
    meal_service:      MealService
    agent:             RecommendationAgent
    template_repo:     TemplateRepo
    shopping_repo:     ShoppingRepo
    weekly_menu_repo:  WeeklyMenuRepo
    auth_service:      AuthService
    family_service:    FamilyService
    rec_settings_repo: RecommendationSettingsRepo
    fridge_repo:       FridgeRepo
    ingredient_repo:   IngredientRepo

    # ── routing ───────────────────────────────────────────────────────────────

    def _dispatch(self, method: str) -> None:
        parsed = urlparse(self.path)
        path   = parsed.path
        query  = parse_qs(parsed.query)

        for m, pattern, handler_name, needs_auth in _ROUTES:
            if m != method:
                continue
            match = pattern.match(path)
            if not match:
                continue
            groups = match.groups()
            try:
                if needs_auth:
                    user = self._require_auth()
                    if user is None:
                        return
                    # Resolve effective user_id (family sharing)
                    eff_id = self.family_service.get_effective_user_id(user["id"])
                    self._current_user    = user
                    self._effective_uid   = eff_id
                else:
                    self._current_user  = None
                    self._effective_uid = None
                getattr(self, handler_name)(query, *groups)
            except ValidationError as e:
                self._send_json({"error": str(e)}, 400)
            except Exception:
                print(traceback.format_exc())
                self._send_json({"error": "Internal server error"}, 500)
            return

        self._send_json({"error": f"Not found: {method} {path}"}, 404)

    def do_GET(self):    self._dispatch("GET")
    def do_POST(self):   self._dispatch("POST")
    def do_PUT(self):    self._dispatch("PUT")
    def do_DELETE(self): self._dispatch("DELETE")

    # ── session helpers ───────────────────────────────────────────────────────

    def _get_session_token(self) -> Optional[str]:
        cookie_header = self.headers.get("Cookie", "")
        for part in cookie_header.split(";"):
            part = part.strip()
            if part.startswith("session="):
                return part[len("session="):]
        return None

    def _require_auth(self) -> Optional[dict]:
        token = self._get_session_token()
        user  = self.auth_service.get_user_by_token(token) if token else None
        if user is None:
            self._send_json({"error": "Not authenticated"}, 401)
            return None
        return user

    # ── public pages ──────────────────────────────────────────────────────────

    def serve_ui(self, _q):
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_reset_page(self, query):
        """Serve the password-reset form (token passed as ?token=...)."""
        token = self._qparam(query, "token") or ""
        valid = self.auth_service.validate_reset_token(token) if token else False
        if not valid:
            page = _RESET_INVALID_PAGE
        else:
            page = _RESET_FORM_PAGE.replace("__TOKEN__", token)
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def health(self, _q):
        self._send_json({"status": "ok", "ui": "/ui"})

    # ── auth endpoints ────────────────────────────────────────────────────────

    def auth_register(self, _q):
        body = self._read_json()
        try:
            user = self.auth_service.register(
                body.get("username", ""),
                body.get("email", ""),
                body.get("password", ""),
            )
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)
            return
        # Auto-login after register
        token = self.auth_service.login(body["username"], body["password"])
        self._set_session_cookie(token)
        self._send_json({"user": user}, 201)

    def auth_login(self, _q):
        body  = self._read_json()
        token = self.auth_service.login(
            body.get("username", ""),
            body.get("password", ""),
        )
        if token is None:
            self._send_json({"error": "Invalid username/email or password"}, 401)
            return
        user = self.auth_service.get_user_by_token(token)
        self._set_session_cookie(token)
        self._send_json({"user": user})

    def auth_logout(self, _q):
        token = self._get_session_token()
        if token:
            self.auth_service.logout(token)
        self._clear_session_cookie()
        self._send_json({"logged_out": True})

    def auth_me(self, _q):
        self._send_json({"user": self._current_user})

    def auth_forgot(self, _q):
        body  = self._read_json()
        email = body.get("email", "").strip()
        if not email:
            self._send_json({"error": "Email is required"}, 400)
            return
        base_url = config.APP_BASE_URL or f"http://{self.headers.get('Host', 'localhost')}"
        found = self.auth_service.request_password_reset(email, base_url)
        # Always return 200 to avoid leaking which emails are registered
        self._send_json({"message": "If that email is registered, a reset link has been sent."})

    def auth_reset(self, _q):
        body     = self._read_json()
        token    = body.get("token", "")
        new_pass = body.get("password", "")
        if not token or not new_pass:
            self._send_json({"error": "token and password are required"}, 400)
            return
        try:
            ok = self.auth_service.reset_password(token, new_pass)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)
            return
        if not ok:
            self._send_json({"error": "Invalid or expired reset link"}, 400)
        else:
            self._send_json({"message": "Password updated. Please log in."})

    # ── meal handlers ─────────────────────────────────────────────────────────

    def list_meals(self, query):
        uid = self._effective_uid
        date_param = self._qparam(query, "meal_date")
        if date_param:
            d     = validate_date(date_param, "meal_date")
            meals = self.meal_service.get_by_date(d, user_id=uid)
            self._send_json([m.to_dict() for m in meals])
        else:
            meals = self.meal_service.get_all(user_id=uid)
            self._send_json([m.to_summary_dict() for m in meals])

    def create_meal(self, _q):
        body = self._read_json()
        data = validate_meal_payload(body)
        meal = self.meal_service.add_meal(data, user_id=self._effective_uid)
        self._send_json(meal.to_dict(), 201)

    def meals_range(self, query):
        start = validate_date(self._qparam(query, "start"), "start")
        end   = validate_date(self._qparam(query, "end"),   "end")
        if start > end:
            raise ValidationError("'start' must be <= 'end'")
        meals = self.meal_service.get_range(start, end, user_id=self._effective_uid)
        self._send_json([m.to_dict() for m in meals])

    def get_meal(self, _q, meal_id: str):
        meal = self.meal_service.get_meal(int(meal_id), user_id=self._effective_uid)
        if meal is None:
            self._send_json({"error": "Meal not found"}, 404)
        else:
            self._send_json(meal.to_dict())

    def update_meal(self, _q, meal_id: str):
        body = self._read_json()
        data = validate_meal_payload(body)
        meal = self.meal_service.update_meal(int(meal_id), data, user_id=self._effective_uid)
        if meal is None:
            self._send_json({"error": "Meal not found"}, 404)
        else:
            self._send_json(meal.to_dict())

    def delete_meal(self, _q, meal_id: str):
        if self.meal_service.delete_meal(int(meal_id), user_id=self._effective_uid):
            self._send_json({"deleted": int(meal_id)})
        else:
            self._send_json({"error": "Meal not found"}, 404)

    def recommend_next_day(self, query):
        date_param = self._qparam(query, "target_date")
        target = validate_date(date_param, "target_date") if date_param else None
        exclude = self.rec_settings_repo.get_excluded_ingredients(self._effective_uid)
        result = self.agent.recommend_day(target, user_id=self._effective_uid,
                                          exclude_ingredients=exclude)
        self._send_json(result)

    def recommend_week(self, query):
        date_param = self._qparam(query, "start_date")
        start = validate_date(date_param, "start_date") if date_param else None
        exclude = self.rec_settings_repo.get_excluded_ingredients(self._effective_uid)
        result = self.agent.recommend_week(start, user_id=self._effective_uid,
                                           exclude_ingredients=exclude)
        self._send_json(result)

    def get_rec_settings(self, _q):
        names = self.rec_settings_repo.get_excluded_ingredients(self._effective_uid)
        self._send_json({"excluded_ingredients": sorted(names, key=str.lower)})

    def update_rec_settings(self, _q):
        body = self._read_json()
        raw  = body.get("excluded_ingredients", [])
        if not isinstance(raw, list) or not all(isinstance(x, str) for x in raw):
            raise ValidationError("'excluded_ingredients' must be an array of strings")
        seen, names = set(), []
        for n in sorted(raw, key=str.lower):
            n = n.strip()
            if n and n.lower() not in seen:
                seen.add(n.lower())
                names.append(n)
        saved = self.rec_settings_repo.set_excluded_ingredients(self._effective_uid, names)
        self._send_json({"excluded_ingredients": saved})

    # ── shopping list ─────────────────────────────────────────────────────────

    def list_shopping(self, _q):
        self._send_json(self.shopping_repo.get_all(user_id=self._effective_uid))

    def add_shopping(self, _q):
        body = self._read_json()
        item = body.get("item", "")
        if not isinstance(item, str) or not item.strip():
            raise ValidationError("'item' must be a non-empty string")
        qty = body.get("quantity", "")
        self._send_json(self.shopping_repo.add(item, qty, user_id=self._effective_uid), 201)

    def bulk_add_shopping(self, _q):
        body  = self._read_json()
        items = body.get("items", [])
        if not isinstance(items, list):
            raise ValidationError("'items' must be an array")
        adjusted = self.fridge_repo.reconcile_with_shopping_list(items, user_id=self._effective_uid)
        from_fridge = len(items) - len(adjusted)
        added = self.shopping_repo.add_many(adjusted, user_id=self._effective_uid)
        self._send_json({"added": len(added), "items": added, "from_fridge": from_fridge}, 201)

    def toggle_shopping(self, _q, item_id: str):
        result = self.shopping_repo.toggle_done(int(item_id), user_id=self._effective_uid)
        if result is None:
            self._send_json({"error": "Item not found"}, 404)
        else:
            self._send_json(result)

    def update_shopping(self, _q, item_id: str):
        body = self._read_json()
        item = body.get("item", "")
        if not isinstance(item, str) or not item.strip():
            raise ValidationError("'item' must be a non-empty string")
        qty    = body.get("quantity", "")
        result = self.shopping_repo.update(int(item_id), item, qty, user_id=self._effective_uid)
        if result is None:
            self._send_json({"error": "Item not found"}, 404)
        else:
            self._send_json(result)

    def delete_shopping(self, _q, item_id: str):
        if self.shopping_repo.delete(int(item_id), user_id=self._effective_uid):
            self._send_json({"deleted": int(item_id)})
        else:
            self._send_json({"error": "Item not found"}, 404)

    def clear_done_shopping(self, _q):
        done_items = self.shopping_repo.get_done(user_id=self._effective_uid)
        if done_items:
            self.fridge_repo.add_many(
                [{"name": it["item"], "quantity": it["quantity"]} for it in done_items],
                user_id=self._effective_uid,
            )
        count = self.shopping_repo.clear_done(user_id=self._effective_uid)
        self._send_json({"cleared": count, "added_to_fridge": len(done_items)})

    # ── weekly menu ───────────────────────────────────────────────────────────

    def get_weekly_menu(self, query):
        date_param = self._qparam(query, "week_start")
        week_start = validate_date(date_param, "week_start") if date_param else None
        rows       = self.weekly_menu_repo.get_week(week_start, user_id=self._effective_uid)
        current    = self.weekly_menu_repo.get_current_week_start()
        self._send_json({"week_start": rows[0]["week_start"] if rows else current, "slots": rows})

    def set_weekly_menu_slot(self, _q):
        body       = self._read_json()
        week_start = body.get("week_start", "")
        day_offset = body.get("day_offset")
        slot       = body.get("slot", "")
        meal_name  = body.get("meal_name", "")
        products   = body.get("products", [])
        if not week_start:
            raise ValidationError("'week_start' is required")
        if day_offset is None or not isinstance(day_offset, int) or not (0 <= day_offset <= 6):
            raise ValidationError("'day_offset' must be an integer 0–6")
        if slot not in ("breakfast", "lunch", "dinner"):
            raise ValidationError("'slot' must be breakfast, lunch, or dinner")
        result = self.weekly_menu_repo.set_slot(
            week_start, day_offset, slot, meal_name, products,
            user_id=self._effective_uid,
        )
        self._send_json(result)

    def weekly_menu_from_rec(self, _q):
        body       = self._read_json()
        week_start = body.get("week_start", "")
        days       = body.get("days", [])
        if not week_start:
            raise ValidationError("'week_start' is required")
        if not isinstance(days, list) or not days:
            raise ValidationError("'days' must be a non-empty array")
        rows = self.weekly_menu_repo.set_week_from_recommendation(
            week_start, days, user_id=self._effective_uid
        )
        self._send_json({"week_start": week_start, "slots": rows})

    def clear_weekly_menu(self, query):
        week_start = self._qparam(query, "week_start")
        if not week_start:
            raise ValidationError("'week_start' query param is required")
        self.weekly_menu_repo.clear_week(week_start, user_id=self._effective_uid)
        self._send_json({"cleared": True, "week_start": week_start})

    # ── fridge ────────────────────────────────────────────────────────────────

    def list_fridge(self, _q):
        self._send_json(self.fridge_repo.get_all(user_id=self._effective_uid))

    def bulk_add_fridge(self, _q):
        body  = self._read_json()
        items = body.get("items", [])
        if not isinstance(items, list) or not items:
            raise ValidationError("'items' must be a non-empty array")
        clean = []
        for i, entry in enumerate(items):
            if not isinstance(entry, dict):
                raise ValidationError(f"items[{i}] must be an object")
            name = entry.get("name", "")
            if not isinstance(name, str) or not name.strip():
                raise ValidationError(f"items[{i}].name must be a non-empty string")
            qty = entry.get("quantity", "")
            if not isinstance(qty, str):
                raise ValidationError(f"items[{i}].quantity must be a string")
            clean.append({"name": name.strip(), "quantity": qty.strip()})
        added = self.fridge_repo.add_many(clean, user_id=self._effective_uid)
        self._send_json({"added": len(added), "items": added}, 201)

    def update_fridge_item(self, _q, item_id: str):
        body = self._read_json()
        name = body.get("name", "")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("'name' must be a non-empty string")
        qty = body.get("quantity", "")
        if not isinstance(qty, str):
            raise ValidationError("'quantity' must be a string")
        result = self.fridge_repo.update(int(item_id), name, qty, user_id=self._effective_uid)
        if result is None:
            self._send_json({"error": "Item not found"}, 404)
        else:
            self._send_json(result)

    def delete_fridge_item(self, _q, item_id: str):
        if self.fridge_repo.delete(int(item_id), user_id=self._effective_uid):
            self._send_json({"deleted": int(item_id)})
        else:
            self._send_json({"error": "Item not found"}, 404)

    def mark_cooked(self, _q):
        """Marking a meal "Cooked" does two things: logs it exactly like
        POST /meals/ would, and settles the Fridge — subtracting only the
        shortfall that was bought specifically for `source` (e.g. a weekly-menu
        slot), not the recipe's full ingredient list, since whatever the
        Fridge already had on hand was taken out back at export time."""
        body = self._read_json()
        source = body.get("source", "")
        if not isinstance(source, str) or not source.strip():
            raise ValidationError("'source' is required")
        data = validate_meal_payload(body.get("meal", {}))
        settled = self.fridge_repo.consume_pending(source.strip(), user_id=self._effective_uid)
        meal = self.meal_service.add_meal(data, user_id=self._effective_uid)
        self._send_json({"meal": meal.to_dict(), "fridge_settled": settled}, 201)

    def list_ingredient_units(self, _q):
        self._send_json(self.ingredient_repo.get_common_units(user_id=self._effective_uid))

    def rename_ingredient_unit(self, _q):
        """Retroactively swap an ingredient's unit everywhere it's used (recipes,
        logged meals, the fridge, the shopping list) — triggered when the user
        confirms they want to change their established unit convention, not
        just use a different one for a single entry."""
        body = self._read_json()
        name = body.get("name", "")
        old_unit = body.get("old_unit", "")
        new_unit = body.get("new_unit", "")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("'name' is required")
        if not isinstance(old_unit, str) or not old_unit.strip():
            raise ValidationError("'old_unit' is required")
        if not isinstance(new_unit, str) or not new_unit.strip():
            raise ValidationError("'new_unit' is required")
        changed = self.ingredient_repo.rename_unit(name, old_unit, new_unit, user_id=self._effective_uid)
        self._send_json({"changed": changed})

    # ── family ────────────────────────────────────────────────────────────────

    def family_get(self, _q):
        group = self.family_service.get_my_group(self._current_user["id"])
        self._send_json({"group": group})

    def family_create(self, _q):
        body = self._read_json()
        name = body.get("name", "Family")
        try:
            group = self.family_service.create_group(self._current_user["id"], name)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)
            return
        self._send_json({"group": group}, 201)

    def family_invite(self, _q):
        body  = self._read_json()
        email = body.get("email", "")
        try:
            result = self.family_service.invite_by_email(self._current_user["id"], email)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)
            return
        self._send_json(result)

    def family_accept(self, _q):
        ok = self.family_service.accept_invite(self._current_user["id"])
        if ok:
            self._send_json({"accepted": True})
        else:
            self._send_json({"error": "No pending invite found"}, 404)

    def family_leave(self, _q):
        ok = self.family_service.leave_group(self._current_user["id"])
        self._send_json({"left": ok})

    def family_remove(self, _q, target_id: str):
        ok = self.family_service.remove_member(self._current_user["id"], int(target_id))
        if ok:
            self._send_json({"removed": int(target_id)})
        else:
            self._send_json({"error": "Member not found or you are not the owner"}, 404)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _set_session_cookie(self, token: str) -> None:
        self._pending_cookie = f"session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=259200"

    def _clear_session_cookie(self) -> None:
        self._pending_cookie = "session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        raw    = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")

    def _send_json(self, data, status: int = 200) -> None:
        body = json.dumps(data, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        # Attach Set-Cookie if one was queued
        cookie = getattr(self, "_pending_cookie", None)
        if cookie:
            self.send_header("Set-Cookie", cookie)
            self._pending_cookie = None
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def _qparam(query: Dict, key: str) -> Optional[str]:
        vals = query.get(key)
        return vals[0] if vals else None

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()}  {fmt % args}")


# ── minimal HTML pages for password reset ────────────────────────────────────

_RESET_FORM_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reset Password — Meal Manager</title>
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
</head>
<body class="bg-dark text-light d-flex align-items-center justify-content-center vh-100">
<div class="card bg-secondary text-light p-4" style="min-width:340px;max-width:420px;width:100%">
  <h4 class="mb-3">🔑 Set a new password</h4>
  <div id="msg"></div>
  <form id="resetForm">
    <input type="hidden" id="token" value="__TOKEN__">
    <div class="mb-3">
      <label class="form-label">New password</label>
      <input type="password" id="pw1" class="form-control" minlength="6" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Confirm password</label>
      <input type="password" id="pw2" class="form-control" minlength="6" required>
    </div>
    <button type="submit" class="btn btn-primary w-100">Save new password</button>
  </form>
</div>
<script>
document.getElementById('resetForm').addEventListener('submit', async e => {
  e.preventDefault();
  const pw1 = document.getElementById('pw1').value;
  const pw2 = document.getElementById('pw2').value;
  const msg = document.getElementById('msg');
  if (pw1 !== pw2) { msg.innerHTML='<div class="alert alert-danger">Passwords do not match.</div>'; return; }
  const res = await fetch('/auth/reset-password', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({token: document.getElementById('token').value, password: pw1})
  });
  const data = await res.json();
  if (res.ok) {
    msg.innerHTML='<div class="alert alert-success">Password updated! <a href="/ui">Go to login</a></div>';
    document.getElementById('resetForm').style.display='none';
  } else {
    msg.innerHTML=`<div class="alert alert-danger">${data.error}</div>`;
  }
});
</script>
</body>
</html>"""

_RESET_INVALID_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Invalid Link — Meal Manager</title>
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
</head>
<body class="bg-dark text-light d-flex align-items-center justify-content-center vh-100">
<div class="card bg-secondary text-light p-4 text-center" style="max-width:420px;width:100%">
  <h4>⚠️ Invalid or expired link</h4>
  <p class="mt-3">This password reset link is no longer valid.<br>
  Please request a new one from the login page.</p>
  <a href="/ui" class="btn btn-primary mt-2">Back to login</a>
</div>
</body>
</html>"""
