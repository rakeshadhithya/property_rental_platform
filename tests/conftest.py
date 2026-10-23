import os
os.environ["DATABASE_URL"] = "sqlite:///./test_property_rental.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["UPLOAD_DIR"] = "./test_uploads"

import pytest
from fastapi.testclient import TestClient
from database import Base, engine
import models
from main import app

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def register_login(client, name, email, password, role):
    r = client.post("/auth/register", json={"name": name, "email": email, "password": password, "role": role})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
