"""
tests/test_products.py
----------------------
Test suite for the ``/products`` API endpoints.

Covers:
- CRUD happy paths (create, list, get, update, delete).
- Business rule: SKU uniqueness (409 on duplicate).
- Validation: negative price and quantity rejected (422).
- Edge cases: get/update/delete non-existent product (404).
- Partial update: only provided fields are changed.
"""

import pytest


class TestCreateProduct:
    def test_create_returns_201(self, client, product_payload):
        resp = client.post("/products", json=product_payload)
        assert resp.status_code == 201

    def test_create_returns_correct_fields(self, client, product_payload):
        data = client.post("/products", json=product_payload).json()
        assert data["name"] == product_payload["name"]
        assert data["sku"] == product_payload["sku"]
        assert float(data["price"]) == product_payload["price"]
        assert data["quantity"] == product_payload["quantity"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_duplicate_sku_returns_409(self, client, product_payload):
        client.post("/products", json=product_payload)
        resp = client.post("/products", json=product_payload)
        assert resp.status_code == 409
        assert "SKU" in resp.json()["detail"]

    def test_different_sku_same_name_allowed(self, client, product_payload):
        client.post("/products", json=product_payload)
        payload2 = {**product_payload, "sku": "WGT-002"}
        resp = client.post("/products", json=payload2)
        assert resp.status_code == 201

    def test_negative_price_returns_422(self, client, product_payload):
        resp = client.post("/products", json={**product_payload, "price": -1})
        assert resp.status_code == 422

    def test_negative_quantity_returns_422(self, client, product_payload):
        resp = client.post("/products", json={**product_payload, "quantity": -5})
        assert resp.status_code == 422

    def test_zero_price_allowed(self, client, product_payload):
        resp = client.post("/products", json={**product_payload, "price": 0})
        assert resp.status_code == 201

    def test_zero_quantity_allowed(self, client, product_payload):
        resp = client.post("/products", json={**product_payload, "quantity": 0})
        assert resp.status_code == 201

    def test_missing_required_field_returns_422(self, client):
        resp = client.post("/products", json={"name": "Incomplete"})
        assert resp.status_code == 422


class TestListProducts:
    def test_list_empty_returns_200(self, client):
        resp = client.get("/products")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_created_product(self, client, created_product):
        resp = client.get("/products")
        assert resp.status_code == 200
        ids = [p["id"] for p in resp.json()]
        assert created_product["id"] in ids

    def test_list_returns_all_products(self, client, product_payload):
        for sku in ["SKU-1", "SKU-2", "SKU-3"]:
            client.post("/products", json={**product_payload, "sku": sku})
        resp = client.get("/products")
        assert len(resp.json()) == 3


class TestGetProduct:
    def test_get_existing_product(self, client, created_product):
        resp = client.get(f"/products/{created_product['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created_product["id"]

    def test_get_nonexistent_returns_404(self, client):
        resp = client.get("/products/99999")
        assert resp.status_code == 404


class TestUpdateProduct:
    def test_update_name(self, client, created_product):
        resp = client.put(f"/products/{created_product['id']}", json={"name": "Widget B"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Widget B"

    def test_update_price(self, client, created_product):
        resp = client.put(f"/products/{created_product['id']}", json={"price": 19.99})
        assert resp.status_code == 200
        assert float(resp.json()["price"]) == 19.99

    def test_update_quantity(self, client, created_product):
        resp = client.put(f"/products/{created_product['id']}", json={"quantity": 50})
        assert resp.status_code == 200
        assert resp.json()["quantity"] == 50

    def test_partial_update_leaves_other_fields_unchanged(self, client, created_product):
        resp = client.put(f"/products/{created_product['id']}", json={"name": "New Name"})
        data = resp.json()
        assert data["sku"] == created_product["sku"]
        assert float(data["price"]) == float(created_product["price"])
        assert data["quantity"] == created_product["quantity"]

    def test_update_sku_conflict_returns_409(self, client, product_payload):
        p1 = client.post("/products", json=product_payload).json()
        p2 = client.post("/products", json={**product_payload, "sku": "OTHER-SKU"}).json()
        resp = client.put(f"/products/{p2['id']}", json={"sku": p1["sku"]})
        assert resp.status_code == 409

    def test_update_negative_price_returns_422(self, client, created_product):
        resp = client.put(f"/products/{created_product['id']}", json={"price": -10})
        assert resp.status_code == 422

    def test_update_negative_quantity_returns_422(self, client, created_product):
        resp = client.put(f"/products/{created_product['id']}", json={"quantity": -1})
        assert resp.status_code == 422

    def test_update_nonexistent_returns_404(self, client):
        resp = client.put("/products/99999", json={"name": "Ghost"})
        assert resp.status_code == 404

    def test_updated_at_changes_after_update(self, client, created_product):
        original_updated_at = created_product["updated_at"]
        resp = client.put(f"/products/{created_product['id']}", json={"name": "Changed"})
        assert resp.json()["updated_at"] >= original_updated_at


class TestDeleteProduct:
    def test_delete_returns_204(self, client, created_product):
        resp = client.delete(f"/products/{created_product['id']}")
        assert resp.status_code == 204

    def test_deleted_product_not_found(self, client, created_product):
        client.delete(f"/products/{created_product['id']}")
        resp = client.get(f"/products/{created_product['id']}")
        assert resp.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete("/products/99999")
        assert resp.status_code == 404
