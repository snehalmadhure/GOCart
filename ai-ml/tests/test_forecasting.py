from datetime import date

from pantry_restock_agent.contracts import PurchaseEvent
from pantry_restock_agent.forecasting import fit_consumption_model, forecast_restocks


def test_quantity_aware_estimator_handles_bulk_purchase() -> None:
    events = [
        PurchaseEvent("milk", 2, date(2026, 1, 1)),
        PurchaseEvent("milk", 1, date(2026, 1, 9)),
        PurchaseEvent("milk", 1, date(2026, 1, 13)),
    ]

    estimate = fit_consumption_model(events)["milk"]

    assert estimate.days_per_unit == 4.0
    assert estimate.units_per_day == 0.25


def test_forecast_replays_purchase_ledger() -> None:
    events = [
        PurchaseEvent("milk", 1, date(2026, 1, 1)),
        PurchaseEvent("milk", 1, date(2026, 1, 5)),
        PurchaseEvent("milk", 1, date(2026, 1, 9)),
    ]

    forecast = forecast_restocks(events, today=date(2026, 1, 10))[0]

    assert round(forecast.estimated_quantity_left, 2) == 0.75
    assert round(forecast.days_left, 2) == 3.0
    assert forecast.status == "ok"
