"""
Centralized Cost Normalization & Multi-Currency Engine for AI Travel Planner.
"""

from typing import Dict, Any, Optional

# Standard exchange rates to INR (Base currency for total budget aggregation)
EXCHANGE_RATES_TO_INR = {
    "INR": 1.0,
    "EUR": 95.0,
    "USD": 87.0,
    "GBP": 112.0,
    "JPY": 0.58,
    "AED": 23.7,
    "CHF": 98.0,
    "THB": 2.5,
    "SGD": 65.0,
    "CAD": 63.5,
    "AUD": 57.0,
}

CURRENCY_SYMBOLS = {
    "INR": "₹",
    "EUR": "€",
    "USD": "$",
    "GBP": "£",
    "JPY": "¥",
    "AED": "AED ",
    "CHF": "CHF ",
    "THB": "฿",
    "SGD": "S$",
    "CAD": "C$",
    "AUD": "A$",
}

# Country to Local Currency Code Map
COUNTRY_CURRENCY_MAP = {
    "France": "EUR",
    "Italy": "EUR",
    "Spain": "EUR",
    "Germany": "EUR",
    "Netherlands": "EUR",
    "Greece": "EUR",
    "Portugal": "EUR",
    "Austria": "EUR",
    "Belgium": "EUR",
    "Ireland": "EUR",
    "Japan": "JPY",
    "United Kingdom": "GBP",
    "UK": "GBP",
    "United States": "USD",
    "USA": "USD",
    "United Arab Emirates": "AED",
    "UAE": "AED",
    "Switzerland": "CHF",
    "Thailand": "THB",
    "Singapore": "SGD",
    "Canada": "CAD",
    "Australia": "AUD",
    "India": "INR"
}


def get_country_currency(country_name: str) -> str:
    if not country_name:
        return "INR"
    for key, code in COUNTRY_CURRENCY_MAP.items():
        if key.lower() in country_name.lower():
            return code
    return "INR"


def normalize_place_cost(cost_val: Optional[float], currency_code: str = "INR", is_explicitly_free: bool = False, place_name: str = "", category: str = "") -> Dict[str, Any]:
    """
    Centralized cost-normalization function.
    Validates amount, identifies currency, distinguishes free from unknown,
    converts currency when required, and returns a consistent structure.
    """
    cost = None
    if cost_val is not None:
        if isinstance(cost_val, (int, float)):
            cost = float(cost_val)
        elif isinstance(cost_val, str):
            import re
            clean_num = re.sub(r'[^\d.]', '', cost_val)
            cost = float(clean_num) if clean_num else 0.0

    # Check if place is known to be free
    is_free = (
        is_explicitly_free or 
        (cost == 0.0 and ("free" in (category or "").lower() or "free" in (place_name or "").lower())) or
        "cathedral" in (place_name or "").lower() or
        "basilica" in (place_name or "").lower() or
        "park" in (category or "").lower()
    )

    if is_free:
        return {
            "amount": 0.0,
            "currency": currency_code,
            "display_amount": "Free 🎟️",
            "inr_amount": 0.0,
            "is_free": True,
            "is_unknown": False
        }

    if cost is None or cost < 0:
        return {
            "amount": 0.0,
            "currency": currency_code,
            "display_amount": "Price unavailable",
            "inr_amount": 0.0,
            "is_free": False,
            "is_unknown": True
        }

    symbol = CURRENCY_SYMBOLS.get(currency_code, f"{currency_code} ")
    rate = EXCHANGE_RATES_TO_INR.get(currency_code, 1.0)
    inr_val = round(cost * rate, 2)

    if currency_code == "INR":
        disp = f"₹{int(cost):,}" if cost.is_integer() else f"₹{cost:,.2f}"
    else:
        disp = f"{symbol}{int(cost):,}" if cost.is_integer() else f"{symbol}{cost:,.2f} (≈ ₹{int(inr_val):,})"

    return {
        "amount": cost,
        "currency": currency_code,
        "display_amount": disp,
        "inr_amount": inr_val,
        "is_free": False,
        "is_unknown": False
    }
