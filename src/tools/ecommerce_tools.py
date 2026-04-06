"""
Demo tools for multi-step commerce reasoning (lab baseline inventory).
"""
from __future__ import annotations

from typing import Any, Dict, List

_STOCK = {"iphone": 50, "ipad": 20, "macbook": 8}
_COUPONS = {"WINNER": 0.10, "SAVE5": 0.05}


def _normalize_item(name: str) -> str:
    n = name.lower().strip()
    if "iphone" in n:
        return "iphone"
    if "ipad" in n:
        return "ipad"
    if "macbook" in n:
        return "macbook"
    return n.replace(" ", "")


def check_stock(item_name: str) -> str:
    key = _normalize_item(item_name)
    qty = _STOCK.get(key)
    if qty is None:
        return f"Unknown item '{item_name}'. Known: iphone, ipad, macbook."
    return f"{key}: {qty} units available."


def get_discount(coupon_code: str) -> str:
    c = coupon_code.strip().upper()
    pct = _COUPONS.get(c)
    if pct is None:
        return f"Invalid coupon '{coupon_code}'. Valid: {', '.join(_COUPONS)}."
    return f"Coupon {c} gives {int(pct * 100)}% off the item subtotal (before shipping)."


def calc_shipping(weight_kg: float, destination: str) -> str:
    d = destination.lower()
    if "hanoi" in d:
        base = 5.0
    elif "hcm" in d or "saigon" in d or "ho chi minh" in d:
        base = 7.0
    else:
        base = 12.0
    w = max(0.0, float(weight_kg))
    cost = base + w * 2.0
    return f"Shipping to '{destination}': ${cost:.2f} (base ${base} + ${2*w:.2f} weight surcharge)."


def _run_check_stock(args: List[Any]) -> str:
    if not args:
        return "Error: check_stock needs item_name, e.g. check_stock(\"iPhone\")."
    return check_stock(str(args[0]))


def _run_get_discount(args: List[Any]) -> str:
    if not args:
        return "Error: get_discount needs coupon_code."
    return get_discount(str(args[0]))


def _run_calc_shipping(args: List[Any]) -> str:
    if len(args) < 2:
        return "Error: calc_shipping needs (weight_kg, destination), e.g. calc_shipping(0.8, \"Hanoi\")."
    return calc_shipping(float(args[0]), str(args[1]))


def get_tool_specs() -> List[Dict[str, Any]]:
    """
    Each tool: name, description (for the LLM), run(args: List[Any]) -> str
    """
    return [
        {
            "name": "check_stock",
            "description": (
                "Check warehouse stock for a product. "
                "Args: one string item_name (e.g. iPhone, iPad, MacBook). "
                "Returns quantity available."
            ),
            "run": _run_check_stock,
        },
        {
            "name": "get_discount",
            "description": (
                "Look up a coupon code. Args: one string coupon_code (e.g. WINNER, SAVE5). "
                "Returns percent discount on subtotal."
            ),
            "run": _run_get_discount,
        },
        {
            "name": "calc_shipping",
            "description": (
                "Estimate shipping cost. Args: weight_kg (number), destination (string city/region). "
                "Returns a dollar amount string."
            ),
            "run": _run_calc_shipping,
        },
    ]
