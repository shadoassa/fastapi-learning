from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world!"}


def test_not_found():
    response = client.get("/nonexistent")
    assert response.status_code == 404
