"""Typed, JSON-friendly contracts shared by ML and backend code."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Any


def normalize_item(value: str) -> str:
    """Normalize user-entered item names without changing their meaning."""
    normalized = re.sub(r"[^a-z0-9]+", " ", value.strip().lower())
    return re.sub(r"\s+", " ", normalized).strip()


def parse_date(value: date | datetime | str) -> date:
    """Accept ISO strings and date-like objects at the integration boundary."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError as error:
            raise ValueError("date must be an ISO date such as 2026-06-01") from error
    raise TypeError("date must be a date, datetime, or ISO date string")


@dataclass(frozen=True)
class PurchaseEvent:
    """A single purchase event supplied by the backend or a test fixture."""

    item: str
    quantity: float
    date: date
    unit: str = "unit"
    unit_price: float | None = None
    expires_in_days: int | None = None

    def __post_init__(self) -> None:
        clean_item = normalize_item(self.item)
        if not clean_item:
            raise ValueError("item cannot be empty")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")
        if self.unit_price is not None and self.unit_price < 0:
            raise ValueError("unit_price cannot be negative")
        if self.expires_in_days is not None and self.expires_in_days < 0:
            raise ValueError("expires_in_days cannot be negative")
        object.__setattr__(self, "item", clean_item)
        object.__setattr__(self, "date", parse_date(self.date))
        object.__setattr__(self, "unit", self.unit.strip() or "unit")

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "PurchaseEvent":
        required = {"item", "quantity", "date"}
        missing = required.difference(payload)
        if missing:
            raise ValueError(f"purchase is missing required fields: {sorted(missing)}")
        return cls(
            item=str(payload["item"]),
            quantity=float(payload["quantity"]),
            date=parse_date(payload["date"]),
            unit=str(payload.get("unit") or "unit"),
            unit_price=(
                float(payload["unit_price"])
                if payload.get("unit_price") is not None
                else None
            ),
            expires_in_days=(
                int(payload["expires_in_days"])
                if payload.get("expires_in_days") is not None
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "item": self.item,
            "quantity": self.quantity,
            "date": self.date.isoformat(),
            "unit": self.unit,
            "unit_price": self.unit_price,
            "expires_in_days": self.expires_in_days,
        }


def coerce_events(events: Iterable[PurchaseEvent | Mapping[str, Any]]) -> list[PurchaseEvent]:
    """Convert JSON payloads to validated purchase events exactly once."""
    return [event if isinstance(event, PurchaseEvent) else PurchaseEvent.from_dict(event) for event in events]


@dataclass(frozen=True)
class ConsumptionEstimate:
    item: str
    days_per_unit: float
    units_per_day: float
    confidence: float
    observations: int
    variation: float
    method: str = "robust_recency_weighted_gap"

    def to_dict(self) -> dict[str, Any]:
        return {
            "item": self.item,
            "days_per_unit": round(self.days_per_unit, 2),
            "units_per_day": round(self.units_per_day, 4),
            "confidence": round(self.confidence, 2),
            "observations": self.observations,
            "variation": round(self.variation, 3),
            "method": self.method,
        }


@dataclass(frozen=True)
class RestockForecast:
    item: str
    unit: str
    estimated_quantity_left: float
    days_left: float
    runout_date: date
    status: str
    confidence: float
    observations: int
    days_per_unit: float
    last_purchase_date: date

    def to_dict(self) -> dict[str, Any]:
        return {
            "item": self.item,
            "unit": self.unit,
            "estimated_quantity_left": round(self.estimated_quantity_left, 2),
            "days_left": round(self.days_left, 2),
            "runout_date": self.runout_date.isoformat(),
            "status": self.status,
            "confidence": round(self.confidence, 2),
            "observations": self.observations,
            "days_per_unit": round(self.days_per_unit, 2),
            "last_purchase_date": self.last_purchase_date.isoformat(),
        }
