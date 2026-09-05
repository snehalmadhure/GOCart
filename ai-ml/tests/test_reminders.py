from pantry_restock_agent.reminders import plan_restock_bundle


def test_bundle_adds_near_future_item_to_reach_delivery_threshold() -> None:
    forecasts = [
        {"item": "milk", "days_left": 1, "days_per_unit": 4, "status": "low"},
        {"item": "bread", "days_left": 5, "days_per_unit": 5, "status": "ok"},
    ]

    plan = plan_restock_bundle(forecasts, delivery_threshold=150, target_days=7, batch_window_days=4)

    assert {item["item"] for item in plan["items"]} == {"milk", "bread"}
    assert plan["threshold_met"] is True
    assert plan["should_notify_now"] is True
