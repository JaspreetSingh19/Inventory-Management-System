"""
tests/test_health.py
--------------------
Smoke test for the ``/health`` endpoint.
"""


def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_returns_ok_status(client):
    data = client.get("/health").json()
    assert data == {"status": "ok"}
