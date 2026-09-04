from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()


class Todo(BaseModel):
    id: int
    title: str
    done: bool = False


class TodoCreate(BaseModel):
    title: str


todos_db: list[Todo] = []
_next_id = 1


def reset_todos() -> None:
    """テスト用: インメモリのTodoストアと採番カウンタを初期状態に戻す"""
    global _next_id
    todos_db.clear()
    _next_id = 1


@app.get("/hello")
async def hello() -> dict[str, str]:
    return {"message": "hello world!"}


@app.get("/todos")
async def list_todos(
    done: bool | None = None,
    limit: int | None = Query(default=None, ge=0),
    offset: int = Query(default=0, ge=0),
) -> list[Todo]:
    result = todos_db
    if done is not None:
        result = [todo for todo in result if todo.done == done]
    result = result[offset:]
    if limit is not None:
        result = result[:limit]
    return result


@app.post("/todos", status_code=201)
async def create_todo(payload: TodoCreate) -> Todo:
    global _next_id
    todo = Todo(id=_next_id, title=payload.title, done=False)
    _next_id += 1
    todos_db.append(todo)
    return todo
