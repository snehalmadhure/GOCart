"""Explainable consumption-rate inference and restock forecasting."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from datetime import date, timedelta
from math import ceil
from statistics import median
from typing import Any

from .catalog import get_catalog_item, resolve_item
from .contracts import ConsumptionEstimate, PurchaseEvent, RestockForecast, coerce_events


def _group_by_item(events: Iterable[PurchaseEvent]) -> dict[str, list[PurchaseEvent]]:
    grouped: dict[str, list[PurchaseEvent]] = defaultdict(list)
    for event in events:
        grouped[resolve_item(event.item)].append(event)
    for item_events in grouped.values():
        item_events.sort(key=lambda event: event.date)
    return dict(grouped)


def _clip_outliers(values: list[float]) -> list[float]:
    """Winsorize extreme purchase gaps using a robust median/MAD rule."""
    if len(values) < 3:
        return values[:]

    center = median(values)
    deviations = [abs(value - center) for value in values]
    mad = median(deviations)
    if mad == 0:
        lower = max(0.1, center / 2.5)
        upper = max(lower, center * 2.5)
    else:
        robust_sigma = 1.4826 * mad
        lower = max(0.1, center - 3.5 * robust_sigma)
        upper = center + 3.5 * robust_sigma
    return [min(max(value, lower), upper) for value in values]


def _confidence(observations: int, variation: float) -> float:
    if observations == 0:
        return 0.05
    count_score = min(1.0, observations / 6)
    stability_score = max(0.0, 1.0 - min(1.0, variation))
    return min(0.98, 0.12 + 0.63 * count_score + 0.25 * stability_score)


def fit_consumption_model(
    purchases: Iterable[PurchaseEvent | Mapping[str, Any]],
    *,
    default_days_per_unit: float = 7.0,
    half_life_days: float = 60.0,
) -> dict[str, ConsumptionEstimate]:
    """Fit a robust, recency-weighted days-per-unit estimate per grocery item.

    Consecutive gaps are divided by the *previous* purchase quantity. For
    example, buying two cartons on Monday and one carton eight days later is
    treated as four days per carton instead of an eight-day cadence.
    """
    if default_days_per_unit <= 0 or half_life_days <= 0:
        raise ValueError("default_days_per_unit and half_life_days must be positive")

    grouped = _group_by_item(coerce_events(purchases))
    estimates: dict[str, ConsumptionEstimate] = {}

    for item, events in grouped.items():
        raw_gaps: list[float] = []
        gap_dates: list[date] = []
        for previous, current in zip(events, events[1:]):
            days_between = (current.date - previous.date).days
            if days_between <= 0:
                continue
            raw_gaps.append(days_between / previous.quantity)
            gap_dates.append(current.date)

        clipped_gaps = _clip_outliers(raw_gaps)
        if clipped_gaps:
            most_recent_observation = max(gap_dates)
            weights = [
                0.5 ** (max(0, (most_recent_observation - observed_on).days) / half_life_days)
                for observed_on in gap_dates
            ]
            total_weight = sum(weights)
            days_per_unit = sum(value * weight for value, weight in zip(clipped_gaps, weights)) / total_weight
            variation = sum(
                weight * abs(value - days_per_unit) / max(days_per_unit, 0.1)
                for value, weight in zip(clipped_gaps, weights)
            ) / total_weight
        else:
            days_per_unit = default_days_per_unit
            variation = 1.0

        estimates[item] = ConsumptionEstimate(
            item=item,
            days_per_unit=days_per_unit,
            units_per_day=1 / days_per_unit,
            confidence=_confidence(len(clipped_gaps), variation),
            observations=len(clipped_gaps),
            variation=variation,
        )

    return estimates


def estimate_consumption_rates(
    purchases: Iterable[PurchaseEvent | Mapping[str, Any]],
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """JSON-ready convenience wrapper used by API routes."""
    estimates = fit_consumption_model(purchases, **kwargs)
    return [estimates[item].to_dict() for item in sorted(estimates)]


def _replay_inventory(events: list[PurchaseEvent], units_per_day: float, today: date) -> float:
    """Replay purchases as an event-sourced stock ledger with inferred usage."""
    if today < events[0].date:
        raise ValueError("today cannot be earlier than the first purchase")

    inventory = 0.0
    cursor = events[0].date
    for event in events:
        elapsed_days = (event.date - cursor).days
        inventory = max(0.0, inventory - elapsed_days * units_per_day)
        inventory += event.quantity
        cursor = event.date

    inventory = max(0.0, inventory - (today - cursor).days * units_per_day)
    return inventory


def forecast_restocks(
    purchases: Iterable[PurchaseEvent | Mapping[str, Any]],
    *,
    today: date | None = None,
    default_days_per_unit: float = 7.0,
) -> list[RestockForecast]:
    """Forecast remaining stock and run-out date for every observed item."""
    event_list = coerce_events(purchases)
    if not event_list:
        return []

    target_day = today or date.today()
    grouped = _group_by_item(event_list)
    estimates = fit_consumption_model(
        event_list,
        default_days_per_unit=default_days_per_unit,
    )
    forecasts: list[RestockForecast] = []

    for item, events in grouped.items():
        estimate = estimates[item]
        inventory = _replay_inventory(events, estimate.units_per_day, target_day)
        days_left = inventory / estimate.units_per_day
        runout_date = target_day + timedelta(days=ceil(max(days_left, 0.0)))
        catalog_item = get_catalog_item(item)
        status = "out" if inventory <= 0.05 else "low" if days_left <= catalog_item.low_stock_days else "ok"
        last_event = events[-1]
        forecasts.append(
            RestockForecast(
                item=item,
                unit=last_event.unit if last_event.unit != "unit" else catalog_item.unit,
                estimated_quantity_left=inventory,
                days_left=days_left,
                runout_date=runout_date,
                status=status,
                confidence=estimate.confidence,
                observations=estimate.observations,
                days_per_unit=estimate.days_per_unit,
                last_purchase_date=last_event.date,
            )
        )

    return sorted(forecasts, key=lambda forecast: (forecast.days_left, forecast.item))
