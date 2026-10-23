from conftest import register_login

def test_upload_rejects_non_image(client):
    owner = register_login(client, "Owner", "owner@example.com", "Password123!", "owner")
    p = client.post("/properties", headers=owner, json={"title":"Sunny flat","description":"Nice home","location":"Hyderabad","price_per_month":"12000","bedrooms":2}).json()
    response = client.post(f"/properties/{p['id']}/upload-image", headers=owner, files={"image":("note.txt", b"hello", "text/plain")})
    assert response.status_code == 415

def test_upload_accepts_png_signature(client):
    owner = register_login(client, "Owner", "owner@example.com", "Password123!", "owner")
    p = client.post("/properties", headers=owner, json={"title":"Sunny flat","description":"Nice home","location":"Hyderabad","price_per_month":"12000","bedrooms":2}).json()
    # A PNG signature is enough for the current format/signature validation.
    png_header = b"\x89PNG\r\n\x1a\n" + b"test-image-data"
    response = client.post(f"/properties/{p['id']}/upload-image", headers=owner, files={"image":("house.png", png_header, "image/png")})
    assert response.status_code == 200, response.text
    assert response.json()["image_path"].startswith("/uploads/")
