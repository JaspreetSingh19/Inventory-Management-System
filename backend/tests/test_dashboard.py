"""
tests/test_dashboard.py
-----------------------
Test suite for the ``/dashboard/summary`` endpoint.

Covers:
- Response structure and field types.
- Correct counts for products, customers, and orders.
- Low-stock list: products below threshold appear, those above do not.
- Low-stock list is sorted by quantity ascending.
- Out-of-stock products (quantity = 0) appear in the low-stock list.
"""

import pytest


@pytest.fixture()
def populated_db(client, product_payload, customer_payload):
    """Create a baseline set of products, customers, and an order."""
    p = client.post("/products", json={**product_payload, "sku": "BASE-1", "quantity": 50}).json()
    c = client.post("/customers", json={**customer_payload, "email": "base@test.com"}).json()
    client.post("/orders", json={
        "customer_id": c["id"],
        "items": [{"product_id": p["id"], "quantity": 1}],
    })
    return {"product": p, "customer": c}


class TestDashboardSummary:
    def test_returns_200(self, client):
        resp = client.get("/dashboard/summary")
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client):
        data = client.get("/dashboard/summary").json()
        assert "total_products" in data
        assert "total_customers" in data
        assert "total_orders" in data
        assert "low_stock_products" in data

    def test_counts_zero_on_empty_db(self, client):
        data = client.get("/dashboard/summary").json()
        assert data["total_products"] == 0
        assert data["total_customers"] == 0
        assert data["total_orders"] == 0
        assert data["low_stock_products"] == []

    def test_product_count_increments(self, client, product_payload):
        client.post("/products", json=product_payload)
        data = client.get("/dashboard/summary").json()
        assert data["total_products"] == 1

    def test_customer_count_increments(self, client, customer_payload):
        client.post("/customers", json=customer_payload)
        data = client.get("/dashboard/summary").json()
        assert data["total_customers"] == 1

    def test_order_count_increments(self, client, populated_db):
        data = client.get("/dashboard/summary").json()
        assert data["total_orders"] == 1

    def test_all_counts_correct(self, client, populated_db):
        data = client.get("/dashboard/summary").json()
        assert data["total_products"] == 1
        assert data["total_customers"] == 1
        assert data["total_orders"] == 1


class TestLowStockProducts:
    def test_product_below_threshold_appears(self, client, product_payload):
        client.post("/products", json={**product_payload, "quantity": 5})
        data = client.get("/dashboard/summary").json()
        assert any(p["sku"] == product_payload["sku"] for p in data["low_stock_products"])

    def test_product_at_threshold_excluded(self, client, product_payload):
        """Quantity == 10 should NOT appear (threshold is strictly < 10)."""
        client.post("/products", json={**product_payload, "quantity": 10})
        data = client.get("/dashboard/summary").json()
        assert not any(p["sku"] == product_payload["sku"] for p in data["low_stock_products"])

    def test_product_above_threshold_excluded(self, client, product_payload):
        client.post("/products", json={**product_payload, "quantity": 100})
        data = client.get("/dashboard/summary").json()
        assert data["low_stock_products"] == []

    def test_out_of_stock_product_appears(self, client, product_payload):
        client.post("/products", json={**product_payload, "quantity": 0})
        data = client.get("/dashboard/summary").json()
        assert any(p["quantity"] == 0 for p in data["low_stock_products"])

    def test_low_stock_list_sorted_ascending(self, client, product_payload):
        """Low-stock products should be returned with lowest quantity first."""
        for i, qty in enumerate([7, 1, 4]):
            client.post("/products", json={**product_payload, "sku": f"LS-{i}", "quantity": qty})
        data = client.get("/dashboard/summary").json()
        quantities = [p["quantity"] for p in data["low_stock_products"]]
        assert quantities == sorted(quantities)

    def test_low_stock_fields_present(self, client, product_payload):
        client.post("/products", json={**product_payload, "quantity": 3})
        data = client.get("/dashboard/summary").json()
        item = data["low_stock_products"][0]
        assert "id" in item
        assert "name" in item
        assert "sku" in item
        assert "quantity" in item
