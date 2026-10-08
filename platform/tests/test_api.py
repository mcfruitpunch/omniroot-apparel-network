import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import create_app


@pytest.fixture()
def client(tmp_path):
    return TestClient(create_app(str(tmp_path / "test.sqlite3")))


def create_user(client, email="test@example.com", password="long-unique-password-123"):
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    return r.json()


def csrf(user):
    return {"X-CSRF-Token": user["csrf_token"]}


def save_fit(client, user, chest=100, hip=105):
    return client.put(
        "/api/fit-profile",
        headers=csrf(user),
        json={"measurements": {"chest_cm": chest, "hip_cm": hip}, "method": "self_reported", "preference": "relaxed"},
    )


def test_public_catalog_and_health(client):
    catalog = client.get("/api/catalog")
    assert catalog.status_code == 200
    assert catalog.json()["checkout_enabled"] is False
    assert all(x["status"] == "research_only" for x in catalog.json()["garments"])
    assert client.get("/api/health").json()["status"] == "ok"
    assert "frame-ancestors 'none'" in catalog.headers["Content-Security-Policy"]


def test_session_cookie_security_and_access(client):
    assert client.get("/api/fit-profile").status_code == 401
    response = client.post("/api/auth/register", json={"email":"test@example.com", "password":"long-unique-password-123"})
    assert response.status_code == 201
    user = response.json()
    assert "httponly" in response.headers["set-cookie"].lower()
    assert "samesite=lax" in response.headers["set-cookie"].lower()
    assert client.get("/api/me").json()["email"] == "test@example.com"
    assert "omniroot_session" in client.cookies
    assert client.post("/api/auth/logout", headers=csrf(user)).status_code == 200
    assert client.get("/api/me").status_code == 401


def test_csrf_origin_and_validation(client):
    user = create_user(client)
    valid = {"measurements": {"chest_cm": 101.0}, "method": "self_reported", "preference": "regular"}
    assert client.put("/api/fit-profile", json=valid).status_code == 403
    assert client.put("/api/fit-profile", headers={**csrf(user), "Origin": "https://evil.test"}, json=valid).status_code == 403
    assert client.put("/api/fit-profile", headers=csrf(user), json={**valid, "measurements": {"chest_cm": 900}}).status_code == 422
    assert client.put("/api/fit-profile", headers=csrf(user), json=valid).status_code == 200


def test_private_profiles_and_requests(client):
    alice = create_user(client, "alice@example.com")
    assert save_fit(client, alice).status_code == 200
    bad_fabric = client.post("/api/requests", headers=csrf(alice), json={"garment_id": "trouser-v1", "fabric_id": "linen-blend"})
    assert bad_fabric.status_code == 422
    missing = client.post("/api/requests", headers=csrf(alice), json={"garment_id": "trouser-v1", "fabric_id": "cotton-twill"})
    assert missing.status_code == 422
    order = client.post("/api/requests", headers=csrf(alice), json={"garment_id": "overshirt-v1", "fabric_id": "linen-blend"})
    assert order.status_code == 201, order.text
    order_id = order.json()["id"]
    assert order.json()["status"] == "awaiting_human_review"
    assert len(client.get("/api/requests").json()["requests"]) == 1

    client.post("/api/auth/logout", headers=csrf(alice))
    bob = create_user(client, "bob@example.com")
    assert client.get("/api/fit-profile").json()["profile"] is None
    assert client.get("/api/requests").json()["requests"] == []
    assert client.post(f"/api/requests/{order_id}/withdraw", headers=csrf(bob)).status_code == 404
    assert client.get("/api/export").json()["requests"] == []

    client.post("/api/auth/logout", headers=csrf(bob))
    login = client.post("/api/auth/login", json={"email":"alice@example.com", "password":"long-unique-password-123"})
    assert login.status_code == 200
    alice = login.json()
    assert client.get("/api/fit-profile").json()["profile"]["measurements"]["chest_cm"] == 100
    assert client.post(f"/api/requests/{order_id}/withdraw", headers=csrf(alice)).json()["status"] == "withdrawn"
    assert client.post(f"/api/requests/{order_id}/withdraw", headers=csrf(alice)).status_code == 409


def test_design_rights_export_and_account_erasure(client):
    user = create_user(client)
    submission = {"name": "Ribbon Jacket", "description": "A jacket with a layered ribbon collar for exploration.", "rights_confirmed": False}
    assert client.post("/api/designs", headers=csrf(user), json=submission).status_code == 422
    submission["rights_confirmed"] = True
    assert client.post("/api/designs", headers=csrf(user), json=submission).status_code == 201
    assert len(client.get("/api/designs").json()["designs"]) == 1
    assert client.get("/api/export").json()["designs"][0]["name"] == "Ribbon Jacket"
    assert client.request("DELETE", "/api/account", headers=csrf(user), json={"password": "wrong-password"}).status_code == 403
    assert client.request("DELETE", "/api/account", headers=csrf(user), json={"password": "long-unique-password-123"}).json()["deleted"]
    assert client.get("/api/me").status_code == 401
    assert client.post("/api/auth/login", json={"email": "test@example.com","password": "long-unique-password-123"}).status_code == 401


def test_fit_delete_and_revisions(client):
    user = create_user(client)
    assert save_fit(client, user).status_code == 200
    assert save_fit(client, user, 102, 106).status_code == 200
    profile = client.get("/api/fit-profile").json()["profile"]
    assert profile["revision"] == 2
    assert profile["measurements"] == {"chest_cm": 102, "hip_cm": 106}
    assert client.delete("/api/fit-profile", headers=csrf(user)).json()["deleted"]
    assert client.get("/api/fit-profile").json()["profile"] is None


def test_no_customer_measurements_in_request_response(client):
    user = create_user(client)
    save_fit(client, user, 137, 149)
    res = client.post("/api/requests", headers=csrf(user), json={"garment_id":"overshirt-v1","fabric_id":"cotton-twill"})
    assert res.status_code == 201
    output = str(client.get("/api/requests").json())
    assert "137" not in output and "149" not in output


def test_browser_entry_and_assets(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "OmniRoot Apparel" in page.text
    assert 'id="fit-form"' in page.text
    assert "frame-ancestors 'none'" in page.headers["Content-Security-Policy"]
    client_script = client.get("/assets/app.js")
    assert client_script.status_code == 200
    assert "await api" in client_script.text
    styles = client.get("/assets/style.css")
    assert styles.status_code == 200
    assert "@media" in styles.text
