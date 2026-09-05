"""One JSON-ready integration point for a FastAPI route or worker."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
from typing import Any

from .contracts import PurchaseEvent, coerce_events
from .forecasting import forecast_restocks
from .pantry import build_virtual_pantry
from .reminders import plan_restock_bundle
from .shopping import generate_pantry_aware_shopping_list


def run_agent(
    purchases: Iterable[PurchaseEvent | Mapping[str, Any]],
    *,
    intent: str | None = None,
    today: date | None = None,
    delivery_threshold: float = 199.0,
) -> dict[str, Any]:
    """Run the full sense -> model -> reason pipeline in one call."""
    events = coerce_events(purchases)
    forecasts = forecast_restocks(events, today=today)
    pantry = build_virtual_pantry(events, today=today)
    response: dict[str, Any] = {
        "purchase_count": len(events),
        "forecasts": [forecast.to_dict() for forecast in forecasts],
        "pantry": pantry,
        "restock_plan": plan_restock_bundle(
            forecasts,
            delivery_threshold=delivery_threshold,
        ),
    }
    if intent:
        response["shopping_list"] = generate_pantry_aware_shopping_list(intent, pantry)
    return response
