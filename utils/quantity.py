"""Shared free-text quantity parsing — used by the shopping list and the fridge.

A quantity like '200g' or '1/2 cup' is split into a (value, unit) pair so two
quantities can be compared/combined only when their units actually match.
Values may be negative (the fridge can go into deficit when more of an
ingredient is used than was on hand).
"""

import re
from typing import Optional, Tuple

_QTY_RE = re.compile(r"^(-?\d+/\d+|-?\d+(?:[.,]\d+)?)\s*(.*)$")


def parse_qty(qty: str) -> Optional[Tuple[float, str]]:
    """Split a free-text quantity into (value, unit).

    Returns None when it doesn't start with a recognisable number (e.g. '',
    'to taste') — callers treat that as "can't safely combine".
    """
    qty = (qty or "").strip()
    if not qty:
        return None
    m = _QTY_RE.match(qty)
    if not m:
        return None
    num_str, unit = m.group(1), m.group(2).strip().lower()
    if "/" in num_str:
        n, d = num_str.split("/")
        if d == "0":
            return None
        value = float(n) / float(d)
    else:
        value = float(num_str.replace(",", "."))
    return value, unit


def format_qty(value: float, unit: str) -> str:
    num_str = str(int(value)) if value == int(value) else f"{value:.2f}".rstrip("0").rstrip(".")
    return f"{num_str} {unit}" if unit else num_str


def group_key(quantity: str):
    """Two quantities are combinable only if they land on the same group key:
    same parsed unit, or (for text we can't parse, e.g. 'to taste') identical
    raw text."""
    parsed = parse_qty(quantity)
    if parsed is not None:
        return ("unit", parsed[1])
    return ("raw", quantity.strip().lower())
