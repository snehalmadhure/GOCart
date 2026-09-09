def purchase_payload(**overrides):
    payload = {
        "item_name": "Milk",
        "quantity": "1.5",
        "unit": "litre",
        "purchased_at": "2026-09-05T09:00:00Z",
        "expires_at": "2026-09-08T09:00:00Z",
    }
    return payload | overrides


def test_create_purchase_persists_and_returns_item(client):
    response = client.post("/api/v1/purchases", json=purchase_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["item_name"] == "Milk"
    assert body["quantity"] == "1.500"
    assert body["unit"] == "litre"


def test_purchase_reuses_item_regardless_of_name_case(client):
    first = client.post("/api/v1/purchases", json=purchase_payload())
    second = client.post(
        "/api/v1/purchases",
        json=purchase_payload(item_name=" milk ", quantity="2"),
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json()["item_id"] == first.json()["item_id"]


def test_list_purchases_can_filter_and_paginates(client):
    client.post("/api/v1/purchases", json=purchase_payload(item_name="Milk"))
    client.post("/api/v1/purchases", json=purchase_payload(item_name="Bread"))

    response = client.get("/api/v1/purchases", params={"item_name": "milk", "limit": 1})

    assert response.status_code == 200
    assert [purchase["item_name"] for purchase in response.json()] == ["Milk"]


def test_purchase_rejects_invalid_payloads(client):
    negative = client.post("/api/v1/purchases", json=purchase_payload(quantity="0"))
    blank_unit = client.post("/api/v1/purchases", json=purchase_payload(unit=" "))
    invalid_dates = client.post(
        "/api/v1/purchases",
        json=purchase_payload(expires_at="2026-09-04T09:00:00Z"),
    )

    assert negative.status_code == 422
    assert blank_unit.status_code == 422
    assert invalid_dates.status_code == 422


def test_import_history_returns_empty_status_until_a_source_is_connected(client):
    response = client.post("/api/purchases/import")

    assert response.status_code == 200
    assert response.json() == {"found": 0, "ready": 0, "review": 0}
