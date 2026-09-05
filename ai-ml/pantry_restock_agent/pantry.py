"""Virtual-pantry state derived from purchase events and the ML forecast."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date, timedelta
from typing import Any

from .catalog import get_catalog_item, resolve_item
from .contracts import PurchaseEvent, coerce_events
from .forecasting import forecast_restocks


def build_virtual_pantry(
    purchases: Iterable[PurchaseEvent | Mapping[str, Any]],
    *,
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Return a readable, JSON-ready pantry inventory for the frontend."""
    event_list = coerce_events(purchases)
    forecasts = forecast_restocks(event_list, today=today)
    target_day = today or date.today()
    latest_event_by_item: dict[str, PurchaseEvent] = {}
    for event in event_list:
        item = resolve_item(event.item)
        if item not in latest_event_by_item or event.date >= latest_event_by_item[item].date:
            latest_event_by_item[item] = event

    pantry: list[dict[str, Any]] = []
    for forecast in forecasts:
        latest_event = latest_event_by_item[forecast.item]
        catalog_item = get_catalog_item(forecast.item)
        shelf_life = latest_event.expires_in_days
        if shelf_life is None:
            shelf_life = catalog_item.shelf_life_days
        expiry_date = latest_event.date + timedelta(days=shelf_life) if shelf_life is not None else None
        if expiry_date is None:
            expiry_status = "unknown"
        elif expiry_date < target_day:
            expiry_status = "expired"
        elif (expiry_date - target_day).days <= 2:
            expiry_status = "expires_soon"
        else:
            expiry_status = "fresh"

        status = "expired" if expiry_status == "expired" else forecast.status
        pantry.append(
            {
                **forecast.to_dict(),
                "status": status,
                "expiry_date": expiry_date.isoformat() if expiry_date else None,
                "expiry_status": expiry_status,
                "display_text": f"{forecast.item}: about {forecast.days_left:.1f} days left",
            }
        )

    return pantry
