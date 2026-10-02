"""
Intelligent recommendation agent — stdlib only.

  1. Candidates come ONLY from recipe templates (+ logged meal history as fallback).
  2. The "no-repeat" window is anchored to target_date, not today.
  3. Within a single recommend_day() call each slot picks a DIFFERENT meal.
  4. When recommending consecutive future dates the already-chosen meals are
     accumulated into the blocked set so each day gets genuinely different food.
  5. All queries are scoped to user_id for per-user isolation.
"""

import math
from collections import Counter
from datetime import date, timedelta
from typing import Dict, List, Optional, Set, Tuple

from models.meal import Meal
from models.meal_type import MealType, MEAL_SLOTS
from repo.meal_repo import MealRepo
from repo.template_repo import TemplateRepo

# Quantity markers for seasoning-scale measures — a pinch of salt or a teaspoon
# of vanilla doesn't make two recipes meaningfully similar just because they
# share it, so these are excluded from diversity/overlap scoring entirely
# regardless of how common the ingredient itself is. Covers both Bulgarian and
# English units since recipes in this app are written in either.
_SMALL_UNIT_MARKERS = (
    "ч.л", "чаена лъжичка",    # teaspoon
    "с.л", "супена лъжица",    # tablespoon
    "щипка",                   # pinch
    "ч.ч", "чаша",             # cup / glass
    "tsp", "teaspoon",
    "tbsp", "tablespoon",
    "pinch",
    "cup", "glass",
)


def _unit_discount(quantity: str) -> float:
    q = (quantity or "").lower()
    return 0.0 if any(marker in q for marker in _SMALL_UNIT_MARKERS) else 1.0


class RecommendationAgent:
    def __init__(
        self,
        meal_repo: MealRepo,
        template_repo: Optional[TemplateRepo] = None,
        history_days: int = 14,
        no_repeat_days: int = 4,
    ):
        self.meal_repo      = meal_repo
        self.template_repo  = template_repo
        self.history_days   = history_days
        self.no_repeat_days = no_repeat_days

    # ── public ────────────────────────────────────────────────────────────────

    def recommend_week(self, start_date: Optional[date] = None,
                       user_id: Optional[int] = None,
                       exclude_ingredients: Optional[List[str]] = None) -> Dict:
        """Recommend 7 consecutive days, each aware of previous days' picks."""
        if start_date is None:
            start_date = date.today() + timedelta(days=1)

        weights = self._ingredient_weights(user_id=user_id)
        for name in (exclude_ingredients or []):
            weights[name.strip().lower()] = 0.0
        week_days: List[Dict] = []
        extra_blocked: Dict[MealType, Set[str]] = {t: set() for t in MEAL_SLOTS}
        extra_products: Counter = Counter()

        for offset in range(7):
            target  = start_date + timedelta(days=offset)
            history = self._history_before(target, user_id=user_id)
            recent_products = self._recent_products(history, weights) + extra_products
            blocked = self._blocked_names(history, target)

            for mt in MEAL_SLOTS:
                blocked[mt] |= extra_blocked[mt]

            date_offset       = (target - date(2000, 1, 1)).days
            chosen_this_day: Set[str] = set()

            day_result = {"date": target.isoformat(), "day": target.strftime("%A")}
            for slot in MEAL_SLOTS:
                rec = self._recommend_slot(
                    slot, history, blocked[slot] | chosen_this_day,
                    recent_products, date_offset, user_id=user_id,
                )
                chosen_this_day.add(rec["meal_name"])
                day_result[slot.value] = rec

            for slot in MEAL_SLOTS:
                name = day_result[slot.value]["meal_name"]
                extra_blocked[slot].add(name)
                for p in day_result[slot.value]["suggested_products"]:
                    is_dict = isinstance(p, dict)
                    pname = (p["name"] if is_dict else p).lower()
                    pqty  = p.get("quantity", "") if is_dict else ""
                    extra_products[pname] += weights.get(pname, 1.0) * _unit_discount(pqty)

            week_days.append(day_result)

        return {
            "start_date": start_date.isoformat(),
            "end_date":   (start_date + timedelta(days=6)).isoformat(),
            "days":       week_days,
        }

    def recommend_day(self, target_date: Optional[date] = None,
                      user_id: Optional[int] = None,
                      exclude_ingredients: Optional[List[str]] = None) -> Dict:
        if target_date is None:
            target_date = date.today() + timedelta(days=1)

        weights = self._ingredient_weights(user_id=user_id)
        for name in (exclude_ingredients or []):
            weights[name.strip().lower()] = 0.0

        history         = self._history_before(target_date, user_id=user_id)
        recent_products = self._recent_products(history, weights)
        blocked         = self._blocked_names(history, target_date)
        date_offset     = (target_date - date(2000, 1, 1)).days
        chosen: Set[str] = set()

        results = {}
        for slot in MEAL_SLOTS:
            rec = self._recommend_slot(
                slot, history, blocked[slot] | chosen,
                recent_products, date_offset, user_id=user_id,
            )
            chosen.add(rec["meal_name"])
            results[slot.value] = rec

        return {
            "target_date": target_date.isoformat(),
            "breakfast":   results[MealType.BREAKFAST.value],
            "lunch":       results[MealType.LUNCH.value],
            "dinner":      results[MealType.DINNER.value],
        }

    # ── internals ─────────────────────────────────────────────────────────────

    def _recommend_slot(
        self,
        meal_type: MealType,
        history: List[Meal],
        blocked: Set[str],
        recent_products: Counter,
        date_offset: int = 0,
        user_id: Optional[int] = None,
    ) -> Dict:
        candidates = self._build_candidates(meal_type, history, user_id=user_id)

        if not candidates:
            return {
                "meal_name":          "No recipes found",
                "meal_type":          meal_type.value,
                "diversity_score":    0.0,
                "reason":             "Add recipes in the Recipes tab first.",
                "suggested_products": [],
            }

        def _pnames(c):
            return [(p["name"], p.get("quantity", "")) for p in c["products"]]

        scored = [
            (self._diversity_score(_pnames(c), recent_products), c)
            for c in candidates
            if c["name"] not in blocked
        ]
        if not scored:
            scored = [(self._diversity_score(_pnames(c), recent_products), c)
                      for c in candidates]

        scored.sort(key=lambda x: x[0], reverse=True)
        top_score = scored[0][0]
        tied      = [c for s, c in scored if abs(s - top_score) < 0.01]
        best      = tied[date_offset % len(tied)]

        return {
            "meal_name":          best["name"],
            "meal_type":          meal_type.value,
            "diversity_score":    round(top_score, 3),
            "reason":             self._build_reason(best["name"], top_score, blocked),
            "suggested_products": best["products"],
        }

    def _build_candidates(self, meal_type: MealType, history: List[Meal],
                          user_id: Optional[int] = None) -> List[Dict]:
        seen: Dict[str, Dict] = {}

        if self.template_repo:
            for t in self.template_repo.get_all(user_id=user_id):
                types = t.get("meal_types") or [t.get("meal_type")]
                if meal_type.value in types:
                    seen[t["name"]] = {
                        "name":     t["name"],
                        "products": [
                            {"name": p["name"], "quantity": p.get("quantity", "")}
                            for p in t.get("products", [])
                        ],
                    }

        if not seen:
            for meal in history:
                if meal.meal_type == meal_type:
                    seen[meal.name] = {
                        "name":     meal.name,
                        "products": [
                            {"name": p.name, "quantity": p.quantity}
                            for p in meal.products
                        ],
                    }

        return list(seen.values())

    def _history_before(self, target_date: date,
                        user_id: Optional[int] = None) -> List[Meal]:
        end   = target_date - timedelta(days=1)
        start = end - timedelta(days=self.history_days - 1)
        return self.meal_repo.get_range(start, end, user_id=user_id)

    def _blocked_names(self, history: List[Meal], target_date: date) -> Dict[MealType, Set[str]]:
        cutoff = target_date - timedelta(days=self.no_repeat_days)
        result: Dict[MealType, Set[str]] = {t: set() for t in MEAL_SLOTS}
        for meal in history:
            if meal.meal_type in result and meal.meal_date >= cutoff:
                result[meal.meal_type].add(meal.name)
        return result

    def _ingredient_weights(self, user_id: Optional[int] = None) -> Dict[str, float]:
        """Down-weight ingredients that show up in almost every recipe (salt, oil,
        water, ...) so they don't drown out the ones that actually distinguish one
        meal from another.

        This is the classic inverse-document-frequency idea: treat each recipe as
        a "document" and each ingredient as a "term" — an ingredient in every
        recipe carries no information and gets weight ~0, one in a single recipe
        keeps its full weight ~1. It's computed fresh from the user's own recipes
        (falling back to logged meal history if there are none yet), so it adapts
        to whatever *their* staples are instead of a hardcoded ignore-list.
        """
        corpus: List[List[str]] = []
        if self.template_repo:
            corpus = [[p["name"] for p in t.get("products", [])]
                      for t in self.template_repo.get_all(user_id=user_id)]
        if not corpus:
            corpus = [m.product_names() for m in self.meal_repo.get_recent(
                days=self.history_days, user_id=user_id)]
        if not corpus:
            return {}

        doc_count: Counter = Counter()
        for ingredients in corpus:
            for name in {n.lower() for n in ingredients}:
                doc_count[name] += 1
        total = len(corpus)
        return {name: 1.0 - (count / total) for name, count in doc_count.items()}

    @staticmethod
    def _recent_products(history: List[Meal], weights: Optional[Dict[str, float]] = None) -> Counter:
        weights = weights or {}
        counter: Counter = Counter()
        for meal in history:
            for p in meal.products:
                name = p.name.lower()
                counter[name] += weights.get(name, 1.0) * _unit_discount(p.quantity)
        return counter

    @staticmethod
    def _diversity_score(products: List[Tuple[str, str]], recent_products: Counter) -> float:
        """products: (name, quantity) pairs for the candidate being scored."""
        if not products:
            return 0.5
        total_overlap, weighted_len = 0.0, 0.0
        for name, qty in products:
            w = _unit_discount(qty)
            total_overlap += recent_products.get(name.lower(), 0) * w
            weighted_len  += w
        if weighted_len == 0:
            return 1.0  # every ingredient here is seasoning-scale — nothing left to compare
        max_freq      = max(recent_products.values(), default=1) or 1
        overlap_ratio = total_overlap / (weighted_len * max_freq)
        return round(1.0 - math.tanh(overlap_ratio * 2), 4)

    @staticmethod
    def _build_reason(name: str, score: float, blocked: Set[str]) -> str:
        if score >= 0.8:
            freshness = "completely fresh ingredients vs recent meals"
        elif score >= 0.5:
            freshness = "mostly different ingredients from recent meals"
        else:
            freshness = "some overlap but not repeated recently"
        shown = [b for b in list(blocked)[:3] if b != "No recipes found"]
        avoid = f" (skipped: {', '.join(shown)})" if shown else ""
        return f"'{name}' — {freshness}{avoid}."
