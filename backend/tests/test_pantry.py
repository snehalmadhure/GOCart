from datetime import datetime, timedelta, timezone


def to_json_time(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def create_purchase(client, item_name: str, quantity: str, purchased_at: datetime, expires_at: datetime | None = None):
    payload = {
        "item_name": item_name,
        "quantity": quantity,
        "unit": "count",
        "purchased_at": to_json_time(purchased_at),
    }
    if expires_at is not None:
        payload["expires_at"] = to_json_time(expires_at)
    response = client.post("/api/v1/purchases", json=payload)
    assert response.status_code == 201


def pantry_at(client, as_of: datetime, status: str = "all"):
    response = client.get(
        "/api/v1/pantry",
        params={"as_of": to_json_time(as_of), "status": status},
    )
    assert response.status_code == 200
    return {item["item_name"]: item for item in response.json()["items"]}


def test_single_purchase_is_unknown_and_refreshes_automatically(client):
    now = datetime.now(timezone.utc)
    create_purchase(client, "Coffee", "1", now)

    pantry = pantry_at(client, now)

    assert pantry["Coffee"]["status"] == "unknown"
    assert pantry["Coffee"]["days_left"] is None


def test_pantry_calculates_in_stock_low_out_and_expired_statuses(client):
    now = datetime.now(timezone.utc)

    create_purchase(client, "Rice", "10", now - timedelta(days=10))
    create_purchase(client, "Rice", "10", now - timedelta(days=1))

    create_purchase(client, "Milk", "10", now - timedelta(days=9))
    create_purchase(client, "Milk", "2", now)

    create_purchase(client, "Bread", "9", now - timedelta(days=3))
    create_purchase(client, "Bread", "1", now - timedelta(days=2))

    create_purchase(client, "Yogurt", "1", now - timedelta(days=3), now - timedelta(days=1))

    pantry = pantry_at(client, now)

    assert pantry["Rice"]["status"] == "in_stock"
    assert float(pantry["Rice"]["days_left"]) > 2
    assert pantry["Milk"]["status"] == "low"
    assert 0 < float(pantry["Milk"]["days_left"]) <= 2
    assert pantry["Bread"]["status"] == "out"
    assert pantry["Yogurt"]["status"] == "expired"


def test_pantry_status_filter_returns_only_matching_items(client):
    now = datetime.now(timezone.utc)
    create_purchase(client, "Tea", "8", now - timedelta(days=8))
    create_purchase(client, "Tea", "1", now)
    create_purchase(client, "Beans", "5", now)

    pantry = pantry_at(client, now, status="low")

    assert list(pantry) == ["Tea"]
    assert pantry["Tea"]["status"] == "low"


def test_new_refill_is_not_expired_by_an_older_purchase(client):
    now = datetime.now(timezone.utc)
    create_purchase(client, "Apples", "5", now - timedelta(days=5), now - timedelta(days=1))
    create_purchase(client, "Apples", "5", now)

    pantry = pantry_at(client, now)

    assert pantry["Apples"]["status"] == "in_stock"
