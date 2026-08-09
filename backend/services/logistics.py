from __future__ import annotations
from math import radians, sin, cos, sqrt, atan2
from typing import Tuple

# Minimal coordinates for a selection of Yemeni governorates (latitude, longitude)
GOV_COORDS = {
    "sana'a": (15.3694, 44.1910),
    "taiz": (13.5764, 44.0209),
    "aden": (12.7855, 45.0187),
    "al_hudaydah": (14.7978, 42.9530),
    "marib": (15.4076, 45.3416),
}

CARRIER_MULTIPLIER = {
    "standard": 1.0,
    "express": 1.6,
    "economy": 0.85,
}

RISK_SCORE_MULTIPLIER = {
    "low": 1.0,
    "medium": 1.25,
    "high": 1.6,
}

BASE_RATE_PER_KM = 0.15  # base USD per km
WEIGHT_RATE_PER_KG = 0.5 # USD per kg


def haversine(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    # returns distance in kilometers
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    rlat1 = radians(lat1)
    rlat2 = radians(lat2)
    x = sin(dlat/2)**2 + cos(rlat1)*cos(rlat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(x), sqrt(1-x))
    return R * c


def risk_score_for_route(origin: str, destination: str) -> str:
    # Simple heuristic: if either point is not in known coords, mark medium risk
    if origin not in GOV_COORDS or destination not in GOV_COORDS:
        return "medium"
    # Example: routes to Marib marked higher risk
    if origin == "marib" or destination == "marib":
        return "high"
    return "low"


def calculate_shipping(origin: str, destination: str, weight_kg: float = 1.0, service: str = "standard", carrier: str = "default") -> dict:
    o = origin.lower()
    d = destination.lower()
    coord_o = GOV_COORDS.get(o)
    coord_d = GOV_COORDS.get(d)
    if coord_o and coord_d:
        distance_km = haversine(coord_o, coord_d)
    else:
        # Fallback: approximate distance of 200 km for unknowns
        distance_km = 200.0

    base = distance_km * BASE_RATE_PER_KM
    weight_cost = max(0.0, weight_kg) * WEIGHT_RATE_PER_KG
    carrier_mult = CARRIER_MULTIPLIER.get(service, 1.0)
    risk = risk_score_for_route(o, d)
    risk_mult = RISK_SCORE_MULTIPLIER.get(risk, 1.0)

    total = (base + weight_cost) * carrier_mult * risk_mult

    return {
        "origin": origin,
        "destination": destination,
        "distance_km": round(distance_km, 2),
        "weight_kg": round(weight_kg, 2),
        "service_level": service,
        "risk_score": risk,
        "carrier": carrier,
        "estimated_cost_usd": round(total, 2),
        "breakdown": {
            "base": round(base, 2),
            "weight_cost": round(weight_cost, 2),
            "carrier_multiplier": carrier_mult,
            "risk_multiplier": risk_mult,
        }
    }
