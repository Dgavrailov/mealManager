"""
Terminal visualisations — pure stdlib, no matplotlib required.
Coloured bar charts printed directly to stdout.
"""

from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import List

from models.meal import Meal
from models.meal_type import MealType

# ANSI colours
_C = {
    "yellow": "\033[93m",
    "green":  "\033[92m",
    "blue":   "\033[94m",
    "cyan":   "\033[96m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "reset":  "\033[0m",
}
_TYPE_COLOR = {
    MealType.BREAKFAST: _C["yellow"],
    MealType.LUNCH:     _C["green"],
    MealType.DINNER:    _C["blue"],
}
_BAR  = "█"
_WIDE = 30


def _bar(value: float, max_val: float, width: int = _WIDE) -> str:
    filled = int(width * value / max_val) if max_val else 0
    return _BAR * filled + "░" * (width - filled)


class Visualizer:
    def __init__(self, meals: List[Meal]):
        self.meals = meals

    def print_all(self) -> None:
        self._section("Meal-type distribution")
        self._type_distribution()

        self._section("Daily meal coverage  (last 14 days)")
        self._daily_heatmap()

        self._section("Top 12 ingredients")
        self._top_ingredients(12)

        self._section("Daily diversity trend  (last 14 days)")
        self._diversity_trend()

    # ------------------------------------------------------------------ charts

    def _type_distribution(self) -> None:
        counts = Counter(m.meal_type for m in self.meals)
        total  = len(self.meals) or 1
        for mt in MealType:
            n   = counts.get(mt, 0)
            col = _TYPE_COLOR[mt]
            print(f"  {col}{mt.value:<11}{_C['reset']} {_bar(n, total)}  {n:3d}  ({n/total*100:.0f}%)")

    def _daily_heatmap(self) -> None:
        today  = date.today()
        by_day = defaultdict(set)
        for m in self.meals:
            by_day[m.meal_date].add(m.meal_type)

        print(f"  {'Date':<12} {'B':^3} {'L':^3} {'D':^3}  Coverage")
        for offset in range(13, -1, -1):
            d     = today - timedelta(days=offset)
            types = by_day.get(d, set())
            b = f"{_C['yellow']}●{_C['reset']}" if MealType.BREAKFAST in types else f"{_C['dim']}·{_C['reset']}"
            l = f"{_C['green']}●{_C['reset']}"  if MealType.LUNCH     in types else f"{_C['dim']}·{_C['reset']}"
            dn= f"{_C['blue']}●{_C['reset']}"   if MealType.DINNER    in types else f"{_C['dim']}·{_C['reset']}"
            bar   = _BAR * len(types) + "░" * (3 - len(types))
            today_marker = f"  {_C['cyan']}← today{_C['reset']}" if d == today else ""
            print(f"  {d.isoformat():<12} {b}   {l}   {dn}   {bar}{today_marker}")

    def _top_ingredients(self, top_n: int) -> None:
        counter: Counter = Counter()
        for m in self.meals:
            for p in m.products:
                counter[p.name.lower()] += 1
        most_common = counter.most_common(top_n)
        if not most_common:
            print("  (no data)")
            return
        max_c = most_common[0][1]
        for name, cnt in most_common:
            print(f"  {name:<24} {_bar(cnt, max_c)}  {cnt}")

    def _diversity_trend(self) -> None:
        """
        Diversity proxy per day = unique products / total products logged.
        1.0 means every ingredient that day was different.
        """
        today  = date.today()
        by_day: defaultdict = defaultdict(list)
        for m in self.meals:
            by_day[m.meal_date].extend(p.name.lower() for p in m.products)

        print(f"  {'Date':<12}  Score  Bar")
        for offset in range(13, -1, -1):
            d     = today - timedelta(days=offset)
            prods = by_day.get(d, [])
            score = len(set(prods)) / len(prods) if prods else 0.0
            today_marker = f"  {_C['cyan']}← today{_C['reset']}" if d == today else ""
            print(f"  {d.isoformat():<12}  {score:.2f}   {_bar(score, 1.0)}{today_marker}")

    # ------------------------------------------------------------------ helper

    @staticmethod
    def _section(title: str) -> None:
        width = 52
        print(f"\n{_C['bold']}{'─' * width}{_C['reset']}")
        print(f"{_C['bold']}  {title}{_C['reset']}")
        print(f"{_C['bold']}{'─' * width}{_C['reset']}")
