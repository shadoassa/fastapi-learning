import pytest
from fastapi.testclient import TestClient

from api.main import app, reset_todos

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset():
    reset_todos()
    yield
    reset_todos()


def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world!"}


def test_not_found():
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_list_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo():
    response = client.post("/todos", json={"title": "牛乳を買う"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "牛乳を買う"
    assert body["done"] is False
    assert body["id"] == 1


def test_list_todos_after_create():
    client.post("/todos", json={"title": "一件目"})
    client.post("/todos", json={"title": "二件目"})
    response = client.get("/todos")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["一件目", "二件目"]
