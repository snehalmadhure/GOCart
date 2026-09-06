"""Adapter between persisted backend data and the repository's ML package."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys

from app.models import Purchase


# ``ai-ml`` is a sibling directory rather than an installed dependency. Add it
# once so both Uvicorn and pytest can use the same repository-local ML package.
ML_PACKAGE_ROOT = Path(__file__).resolve().parents[3] / "ai-ml"
if str(ML_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_PACKAGE_ROOT))

from pantry_restock_agent.forecasting import forecast_restocks  # noqa: E402
from pantry_restock_agent.shopping import generate_pantry_aware_shopping_list  # noqa: E402


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
    pantry_warning: str | None = None


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def estimate_consumption(purchases: list[Purchase], as_of: datetime) -> ConsumptionEstimate:
    """Use the ML package's robust, recency-weighted forecast for one item."""

    if len(purchases) < 2 or len({purchase.unit for purchase in purchases}) != 1:
        return ConsumptionEstimate(None, None, None, None, "insufficient_history")

    item_name = purchases[0].item.name
    ml_purchases = [
        {
            "item": item_name,
            "quantity": float(purchase.quantity),
            "date": _as_utc(purchase.purchased_at).date().isoformat(),
            "unit": purchase.unit,
        }
        for purchase in purchases
    ]
    forecast = forecast_restocks(ml_purchases, today=_as_utc(as_of).date())[0]
    run_out_at = datetime.combine(forecast.runout_date, datetime.min.time(), tzinfo=timezone.utc)
    return ConsumptionEstimate(
        estimated_quantity=Decimal(str(forecast.estimated_quantity_left)),
        daily_usage=Decimal(str(1 / forecast.days_per_unit)),
        days_left=Decimal(str(forecast.days_left)),
        run_out_at=run_out_at,
        confidence="ml",
    )


def generate_list(intent: str, pantry_items: list[object]) -> list[SuggestedItem]:
    """Generate an ML pantry-aware list using current backend pantry states."""

    ml_pantry = [
        {
            "item": state.item.name,
            "estimated_quantity_left": float(state.estimated_quantity or 0),
            "status": "ok" if state.status == "in_stock" else state.status,
        }
        for state in pantry_items
    ]
    result = generate_pantry_aware_shopping_list(intent, ml_pantry)
    suggestions: list[SuggestedItem] = []
    for row in result["needs_to_buy"]:
        suggestions.append(
            SuggestedItem(
                item_name=row["item"],
                quantity=Decimal(str(row["quantity"])),
                unit=row["unit"],
                reason="Suggested by the pantry restock model",
            )
        )
    for row in result["already_have"]:
        suggestions.append(
            SuggestedItem(
                item_name=row["item"],
                quantity=Decimal(str(row["quantity"])),
                unit=row["unit"],
                reason="Already available in the pantry",
                pantry_warning=row["nudge"],
            )
        )
    return suggestions
