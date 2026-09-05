"""Decision policy for batched, delivery-threshold-aware restock nudges."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from math import ceil
from typing import Any

from .catalog import get_catalog_item
from .contracts import RestockForecast


def _as_row(forecast: RestockForecast | Mapping[str, Any]) -> dict[str, Any]:
    return forecast.to_dict() if isinstance(forecast, RestockForecast) else dict(forecast)


def _suggested_quantity(row: Mapping[str, Any], target_days: float) -> int:
    days_left = max(0.0, float(row["days_left"]))
    days_per_unit = max(0.1, float(row["days_per_unit"]))
    return max(1, ceil(max(0.0, target_days - days_left) / days_per_unit))


def plan_restock_bundle(
    forecasts: Iterable[RestockForecast | Mapping[str, Any]],
    *,
    delivery_threshold: float = 199.0,
    target_days: float = 7.0,
    batch_window_days: float = 4.0,
) -> dict[str, Any]:
    """Bundle urgent and near-future purchases into one non-spammy reminder."""
    if delivery_threshold < 0 or target_days <= 0 or batch_window_days < 0:
        raise ValueError("invalid reminder-planning thresholds")

    rows = [_as_row(forecast) for forecast in forecasts]
    urgent = [row for row in rows if row.get("status") in {"out", "low"}]
    upcoming = [
        row
        for row in rows
        if row.get("status") == "ok" and float(row.get("days_left", 0)) <= target_days + batch_window_days
    ]
    upcoming.sort(key=lambda row: float(row["days_left"]))

    selected = urgent[:]
    subtotal = 0.0

    def format_item(row: Mapping[str, Any]) -> dict[str, Any]:
        catalog_item = get_catalog_item(str(row["item"]))
        quantity = _suggested_quantity(row, target_days)
        price = catalog_item.typical_price
        return {
            "item": row["item"],
            "quantity": quantity,
            "unit": catalog_item.unit,
            "days_left": round(float(row["days_left"]), 2),
            "priority": row["status"],
            "estimated_line_total": round((price or 0.0) * quantity, 2) if price is not None else None,
        }

    selected_items = [format_item(row) for row in selected]
    subtotal = sum(item["estimated_line_total"] or 0.0 for item in selected_items)

    for candidate in upcoming:
        if subtotal >= delivery_threshold:
            break
        selected_items.append(format_item(candidate))
        subtotal += selected_items[-1]["estimated_line_total"] or 0.0

    threshold_met = subtotal >= delivery_threshold
    min_days_left = min((float(row["days_left"]) for row in urgent), default=float("inf"))
    should_notify_now = bool(urgent) and (threshold_met or min_days_left <= 0)

    return {
        "should_notify_now": should_notify_now,
        "delivery_threshold": round(delivery_threshold, 2),
        "estimated_subtotal": round(subtotal, 2),
        "threshold_met": threshold_met,
        "threshold_gap": round(max(0.0, delivery_threshold - subtotal), 2),
        "items": selected_items,
        "held_for_batching": [
            row["item"] for row in upcoming if row["item"] not in {item["item"] for item in selected_items}
        ],
        "reason": (
            "At least one item is out, so send a reminder now."
            if min_days_left <= 0
            else "The bundle reaches the delivery threshold."
            if should_notify_now
            else "Low-stock items are being held briefly to avoid a small, inefficient order."
        ),
    }
