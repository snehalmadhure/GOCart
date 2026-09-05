from datetime import datetime, timedelta, timezone

from tests.test_pantry import create_purchase, pantry_at


def test_prediction_failure_retains_the_last_successful_pantry_state(client, monkeypatch):
    now = datetime.now(timezone.utc)
    create_purchase(client, "Flour", "8", now - timedelta(days=8))
    create_purchase(client, "Flour", "8", now - timedelta(days=1))
    before = pantry_at(client, now)["Flour"]

    def unavailable(*_args, **_kwargs):
        raise RuntimeError("ML service is unavailable")

    monkeypatch.setattr("app.services.pantry.estimate_consumption", unavailable)
    after = pantry_at(client, now + timedelta(hours=1))["Flour"]

    assert after["status"] == before["status"]
    assert after["estimated_quantity"] == before["estimated_quantity"]


def test_restock_alerts_batch_deduplicate_and_can_be_dismissed(client):
    now = datetime.now(timezone.utc)
    create_purchase(client, "Bread", "9", now - timedelta(days=3))
    create_purchase(client, "Bread", "1", now - timedelta(days=2))
    create_purchase(client, "Milk", "10", now - timedelta(days=9))
    create_purchase(client, "Milk", "2", now)
    pantry_at(client, now)

    first = client.get("/api/v1/restock-alerts")
    second = client.get("/api/v1/restock-alerts")

    assert first.status_code == 200
    assert len(first.json()) == 1
    assert {item["item_name"] for item in first.json()[0]["items"]} == {"Bread", "Milk"}
    assert second.json()[0]["id"] == first.json()[0]["id"]
    assert len(second.json()[0]["items"]) == 2

    dismissed = client.post(f"/api/v1/restock-alerts/{first.json()[0]['id']}/dismiss")
    assert dismissed.status_code == 200
    assert dismissed.json()["status"] == "dismissed"
    assert client.get("/api/v1/restock-alerts").json() == []
    assert client.get("/api/v1/restock-alerts?include_dismissed=true").json()[0]["status"] == "dismissed"


def test_generated_list_warns_about_well_stocked_pantry_item(client):
    now = datetime.now(timezone.utc)
    create_purchase(client, "Tomato Sauce", "8", now - timedelta(days=8))
    create_purchase(client, "Tomato Sauce", "8", now - timedelta(days=1))
    pantry_at(client, now)

    response = client.post("/api/v1/shopping-lists/generate", json={"intent": "Pasta for dinner"})

    assert response.status_code == 200
    suggestions = {item["item_name"]: item for item in response.json()["items"]}
    assert suggestions["tomato sauce"]["pantry_warning"] is not None
    assert suggestions["pasta"]["pantry_warning"] is None


def test_generated_list_rejects_an_empty_intent(client):
    response = client.post("/api/v1/shopping-lists/generate", json={"intent": ""})

    assert response.status_code == 422


def test_health_endpoint_allows_the_local_react_origin(client):
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
