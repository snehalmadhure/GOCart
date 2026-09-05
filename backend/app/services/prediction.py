"""Temporary consumption-estimation adapter.

This module is the only boundary that Phase 4 should replace with functions
from ``ml/``. Its implementation is intentionally simple and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models import Purchase


@dataclass(frozen=True)
class ConsumptionEstimate:
    estimated_quantity: Decimal | None
    daily_usage: Decimal | None
    days_left: Decimal | None
    run_out_at: datetime | None
    confidence: str


@dataclass(frozen=True)
class SuggestedItem:
    """A shopping-list suggestion returned by the temporary ML adapter."""

    item_name: str
    quantity: Decimal
    unit: str
    reason: str


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def estimate_consumption(purchases: list[Purchase], as_of: datetime) -> ConsumptionEstimate:
    """Estimate usage from the time between the oldest and newest purchases.

    At least two purchases using one unit are required. The newest purchase is
    treated as the current refill; earlier purchases establish average daily
    use. This is a temporary estimator, not a production forecasting model.
    """

    if len(purchases) < 2 or len({purchase.unit for purchase in purchases}) != 1:
        return ConsumptionEstimate(None, None, None, None, "insufficient_history")

    ordered = sorted(purchases, key=lambda purchase: _as_utc(purchase.purchased_at))
    first_at = _as_utc(ordered[0].purchased_at)
    latest = ordered[-1]
    latest_at = _as_utc(latest.purchased_at)
    elapsed_between_purchases = Decimal(str((latest_at - first_at).total_seconds())) / Decimal("86400")
    if elapsed_between_purchases <= 0:
        return ConsumptionEstimate(None, None, None, None, "insufficient_history")

    consumed_quantity = sum((purchase.quantity for purchase in ordered[:-1]), start=Decimal("0"))
    daily_usage = consumed_quantity / elapsed_between_purchases
    if daily_usage <= 0:
        return ConsumptionEstimate(None, None, None, None, "insufficient_history")

    elapsed_since_latest = max(
        Decimal("0"),
        Decimal(str((_as_utc(as_of) - latest_at).total_seconds())) / Decimal("86400"),
    )
    remaining_quantity = max(Decimal("0"), latest.quantity - daily_usage * elapsed_since_latest)
    days_left = remaining_quantity / daily_usage
    run_out_at = _as_utc(as_of) + timedelta(seconds=float(days_left * Decimal("86400")))
    return ConsumptionEstimate(remaining_quantity, daily_usage, days_left, run_out_at, "low")


def generate_list(intent: str, pantry_items: list[object]) -> list[SuggestedItem]:
    """Generate a deterministic starter list until the ML model is integrated.

    ``pantry_items`` remains part of the contract even though the temporary
    implementation does not reason over it. Phase 4 can replace this function
    directly with the ML teammate's implementation.
    """

    normalized_intent = intent.casefold()
    if "pasta" in normalized_intent:
        return [
            SuggestedItem("pasta", Decimal("1"), "pack", "needed for pasta"),
            SuggestedItem("tomato sauce", Decimal("1"), "pack", "needed for pasta sauce"),
            SuggestedItem("garlic", Decimal("1"), "pack", "needed for pasta seasoning"),
        ]
    return [SuggestedItem("milk", Decimal("1"), "litre", "general pantry staple")]
