import pytest
from fastapi.testclient import TestClient

from api.main import app, reset_todos, todos_db

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


def test_list_todos_filter_by_done():
    client.post("/todos", json={"title": "未完了"})
    client.post("/todos", json={"title": "完了済み"})
    # PUT /todos/{id}は別ブランチ実装のため未提供。ストアを直接書き換えてdone済みを用意する。
    todos_db[1].done = True

    response = client.get("/todos", params={"done": True})
    assert response.status_code == 200
    body = response.json()
    assert [t["title"] for t in body] == ["完了済み"]

    response = client.get("/todos", params={"done": False})
    assert response.status_code == 200
    body = response.json()
    assert [t["title"] for t in body] == ["未完了"]


def test_list_todos_pagination():
    for i in range(5):
        client.post("/todos", json={"title": f"item{i}"})

    response = client.get("/todos", params={"limit": 2, "offset": 1})
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["item1", "item2"]

    response = client.get("/todos", params={"offset": 4})
    titles = [t["title"] for t in response.json()]
    assert titles == ["item4"]

    response = client.get("/todos", params={"limit": 0})
    assert response.json() == []


def test_list_todos_filter_and_pagination_combined():
    for i in range(5):
        client.post("/todos", json={"title": f"item{i}"})
    for i, todo in enumerate(todos_db):
        if i % 2 == 0:
            todo.done = True

    response = client.get("/todos", params={"done": True, "limit": 1, "offset": 1})
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["item2"]


def test_list_todos_invalid_pagination_params():
    response = client.get("/todos", params={"limit": -1})
    assert response.status_code == 422

    response = client.get("/todos", params={"offset": -1})
    assert response.status_code == 422
