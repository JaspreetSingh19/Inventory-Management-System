"""
tests/test_customers.py
-----------------------
Test suite for the ``/customers`` API endpoints.

Covers:
- CRUD happy paths (create, list, get, delete).
- Business rule: email uniqueness (409 on duplicate).
- Validation: malformed email rejected (422).
- Edge cases: get/delete non-existent customer (404).
"""


class TestCreateCustomer:
    def test_create_returns_201(self, client, customer_payload):
        resp = client.post("/customers", json=customer_payload)
        assert resp.status_code == 201

    def test_create_returns_correct_fields(self, client, customer_payload):
        data = client.post("/customers", json=customer_payload).json()
        assert data["full_name"] == customer_payload["full_name"]
        assert data["email"] == customer_payload["email"]
        assert data["phone"] == customer_payload["phone"]
        assert "id" in data
        assert "created_at" in data

    def test_duplicate_email_returns_409(self, client, customer_payload):
        client.post("/customers", json=customer_payload)
        resp = client.post("/customers", json={**customer_payload, "full_name": "Other Person"})
        assert resp.status_code == 409
        assert "Email" in resp.json()["detail"] or "email" in resp.json()["detail"].lower()

    def test_different_emails_allowed(self, client, customer_payload):
        client.post("/customers", json=customer_payload)
        resp = client.post("/customers", json={**customer_payload, "email": "other@example.com"})
        assert resp.status_code == 201

    def test_invalid_email_returns_422(self, client, customer_payload):
        resp = client.post("/customers", json={**customer_payload, "email": "not-an-email"})
        assert resp.status_code == 422

    def test_missing_required_field_returns_422(self, client):
        resp = client.post("/customers", json={"full_name": "Incomplete"})
        assert resp.status_code == 422


class TestListCustomers:
    def test_list_empty_returns_200(self, client):
        resp = client.get("/customers")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_created_customer(self, client, created_customer):
        resp = client.get("/customers")
        ids = [c["id"] for c in resp.json()]
        assert created_customer["id"] in ids

    def test_list_returns_all_customers(self, client, customer_payload):
        emails = ["a@test.com", "b@test.com", "c@test.com"]
        for email in emails:
            client.post("/customers", json={**customer_payload, "email": email})
        resp = client.get("/customers")
        assert len(resp.json()) == 3


class TestGetCustomer:
    def test_get_existing_customer(self, client, created_customer):
        resp = client.get(f"/customers/{created_customer['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created_customer["id"]

    def test_get_nonexistent_returns_404(self, client):
        resp = client.get("/customers/99999")
        assert resp.status_code == 404


class TestDeleteCustomer:
    def test_delete_returns_204(self, client, created_customer):
        resp = client.delete(f"/customers/{created_customer['id']}")
        assert resp.status_code == 204

    def test_deleted_customer_not_found(self, client, created_customer):
        client.delete(f"/customers/{created_customer['id']}")
        resp = client.get(f"/customers/{created_customer['id']}")
        assert resp.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete("/customers/99999")
        assert resp.status_code == 404
