"""
tests/test_orders.py
--------------------
Test suite for the ``/orders`` API endpoints.

Covers:
- Happy path: create order, list orders, get order, cancel order.
- Business rules:
    - Stock is decremented when an order is placed.
    - Stock is restored when an order is cancelled.
    - Order with insufficient stock is rejected (422).
    - Multi-item orders are supported.
    - ``total_amount`` is calculated server-side.
- Edge cases: non-existent customer, non-existent product, get/delete 404.
"""

import pytest


@pytest.fixture()
def order_payload(created_product, created_customer):
    """Valid order payload referencing an existing customer and product."""
    return {
        "customer_id": created_customer["id"],
        "items": [{"product_id": created_product["id"], "quantity": 2}],
    }


@pytest.fixture()
def created_order(client, order_payload):
    """An order that has already been placed via the API."""
    resp = client.post("/orders", json=order_payload)
    assert resp.status_code == 201
    return resp.json()


class TestCreateOrder:
    def test_create_returns_201(self, client, order_payload):
        resp = client.post("/orders", json=order_payload)
        assert resp.status_code == 201

    def test_create_returns_nested_customer_and_items(self, client, order_payload):
        data = client.post("/orders", json=order_payload).json()
        assert "customer" in data
        assert "items" in data
        assert len(data["items"]) == 1

    def test_total_amount_calculated_correctly(self, client, order_payload, created_product):
        data = client.post("/orders", json=order_payload).json()
        expected = float(created_product["price"]) * 2
        assert abs(float(data["total_amount"]) - expected) < 0.01

    def test_stock_decremented_after_order(self, client, order_payload, created_product):
        initial_qty = created_product["quantity"]
        client.post("/orders", json=order_payload)
        updated = client.get(f"/products/{created_product['id']}").json()
        assert updated["quantity"] == initial_qty - 2

    def test_unit_price_snapshotted_at_order_time(self, client, order_payload, created_product):
        """Price stored in order_item should match product price at creation."""
        data = client.post("/orders", json=order_payload).json()
        assert float(data["items"][0]["unit_price"]) == float(created_product["price"])

    def test_insufficient_stock_returns_422(self, client, created_product, created_customer):
        payload = {
            "customer_id": created_customer["id"],
            "items": [{"product_id": created_product["id"], "quantity": 99999}],
        }
        resp = client.post("/orders", json=payload)
        assert resp.status_code == 422
        assert "Insufficient stock" in resp.json()["detail"]

    def test_zero_quantity_item_returns_422(self, client, created_product, created_customer):
        payload = {
            "customer_id": created_customer["id"],
            "items": [{"product_id": created_product["id"], "quantity": 0}],
        }
        resp = client.post("/orders", json=payload)
        assert resp.status_code == 422

    def test_empty_items_list_returns_422(self, client, created_customer):
        resp = client.post("/orders", json={"customer_id": created_customer["id"], "items": []})
        assert resp.status_code == 422

    def test_nonexistent_customer_returns_404(self, client, created_product):
        payload = {
            "customer_id": 99999,
            "items": [{"product_id": created_product["id"], "quantity": 1}],
        }
        resp = client.post("/orders", json=payload)
        assert resp.status_code == 404

    def test_nonexistent_product_returns_404(self, client, created_customer):
        payload = {
            "customer_id": created_customer["id"],
            "items": [{"product_id": 99999, "quantity": 1}],
        }
        resp = client.post("/orders", json=payload)
        assert resp.status_code == 404

    def test_multi_item_order(self, client, product_payload, customer_payload):
        """Order with two distinct products calculates total across both items."""
        p1 = client.post("/products", json={**product_payload, "sku": "P1", "price": 10.00, "quantity": 50}).json()
        p2 = client.post("/products", json={**product_payload, "sku": "P2", "price": 5.00, "quantity": 50}).json()
        c = client.post("/customers", json={**customer_payload, "email": "multi@test.com"}).json()

        payload = {
            "customer_id": c["id"],
            "items": [
                {"product_id": p1["id"], "quantity": 2},
                {"product_id": p2["id"], "quantity": 4},
            ],
        }
        data = client.post("/orders", json=payload).json()
        assert len(data["items"]) == 2
        # 2 × 10.00 + 4 × 5.00 = 40.00
        assert abs(float(data["total_amount"]) - 40.00) < 0.01

    def test_stock_not_decremented_on_failure(self, client, created_product, created_customer):
        """If one item fails, no stock should be changed (atomic transaction)."""
        initial_qty = created_product["quantity"]
        payload = {
            "customer_id": created_customer["id"],
            "items": [
                {"product_id": created_product["id"], "quantity": 1},
                {"product_id": 99999, "quantity": 1},  # non-existent — causes 404
            ],
        }
        client.post("/orders", json=payload)
        current_qty = client.get(f"/products/{created_product['id']}").json()["quantity"]
        assert current_qty == initial_qty


class TestListOrders:
    def test_list_empty_returns_200(self, client):
        resp = client.get("/orders")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_placed_order(self, client, created_order):
        resp = client.get("/orders")
        ids = [o["id"] for o in resp.json()]
        assert created_order["id"] in ids


class TestGetOrder:
    def test_get_existing_order(self, client, created_order):
        resp = client.get(f"/orders/{created_order['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created_order["id"]

    def test_get_order_includes_customer_and_items(self, client, created_order):
        data = client.get(f"/orders/{created_order['id']}").json()
        assert "customer" in data
        assert "items" in data

    def test_get_nonexistent_order_returns_404(self, client):
        resp = client.get("/orders/99999")
        assert resp.status_code == 404


class TestCancelOrder:
    def test_cancel_returns_204(self, client, created_order):
        resp = client.delete(f"/orders/{created_order['id']}")
        assert resp.status_code == 204

    def test_cancelled_order_not_found(self, client, created_order):
        client.delete(f"/orders/{created_order['id']}")
        resp = client.get(f"/orders/{created_order['id']}")
        assert resp.status_code == 404

    def test_stock_restored_after_cancel(self, client, order_payload, created_product):
        initial_qty = created_product["quantity"]
        order = client.post("/orders", json=order_payload).json()
        client.delete(f"/orders/{order['id']}")
        restored_qty = client.get(f"/products/{created_product['id']}").json()["quantity"]
        assert restored_qty == initial_qty

    def test_cancel_nonexistent_returns_404(self, client):
        resp = client.delete("/orders/99999")
        assert resp.status_code == 404
