from conftest import register_login

def test_booking_approval_makes_property_unavailable(client):
    owner = register_login(client, "Owner", "owner@example.com", "Password123!", "owner")
    tenant = register_login(client, "Tenant", "tenant@example.com", "Password123!", "tenant")
    p = client.post("/properties", headers=owner, json={"title":"Sunny flat","description":"Nice home","location":"Hyderabad","price_per_month":"12000","bedrooms":2})
    assert p.status_code == 201, p.text
    booking = client.post("/bookings", headers=tenant, json={"property_id":p.json()["id"],"start_date":"2026-11-01T00:00:00","end_date":"2027-01-01T00:00:00"})
    assert booking.status_code == 201, booking.text
    approved = client.patch(f"/bookings/{booking.json()['id']}/approve", headers=owner)
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert client.get("/properties").json() == []

def test_owner_cannot_manage_other_owner_property(client):
    owner1 = register_login(client, "Owner One", "one@example.com", "Password123!", "owner")
    owner2 = register_login(client, "Owner Two", "two@example.com", "Password123!", "owner")
    p = client.post("/properties", headers=owner1, json={"title":"Sunny flat","description":"Nice home","location":"Hyderabad","price_per_month":"12000","bedrooms":2})
    result = client.put(f"/properties/{p.json()['id']}", headers=owner2, json={"title":"Hijacked"})
    assert result.status_code == 403

def test_duplicate_active_booking_rejected(client):
    owner = register_login(client, "Owner", "owner@example.com", "Password123!", "owner")
    tenant = register_login(client, "Tenant", "tenant@example.com", "Password123!", "tenant")
    p = client.post("/properties", headers=owner, json={"title":"Sunny flat","description":"Nice home","location":"Hyderabad","price_per_month":"12000","bedrooms":2}).json()
    payload = {"property_id":p["id"],"start_date":"2026-11-01T00:00:00","end_date":"2027-01-01T00:00:00"}
    assert client.post("/bookings", headers=tenant, json=payload).status_code == 201
    assert client.post("/bookings", headers=tenant, json=payload).status_code == 409
